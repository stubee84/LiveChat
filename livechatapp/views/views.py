import django.http.request as request
from rest_framework import response, status, views, generics
from django.shortcuts import render
from livechatapp.controllers.utils import extract_values_from_error, logger
from livechatapp.controllers.twilio import twilio_controller as tc
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth import login, decorators
from livechatapp.models import User, Caller, Message
from livechatapp.serializers import RegistrationSerializer, LoginSerializer, UserSerializer, NumberSerializer, CallerSerializer, MessageSerializer


all_decorators = [decorators.login_required, csrf_protect]

class UserRegistration(views.APIView):
    def post(self, request: request.HttpRequest, format='json') -> response.Response:
        serializer = RegistrationSerializer(data=request.data)
        
        try:
            if serializer.is_valid(raise_exception=True):
                user: User = serializer.create(validated_data=request.data)
                if user:
                    return response.Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            try:
                msg = extract_values_from_error(e.detail)
                code = e.status_code
            except AttributeError:
                msg = extract_values_from_error(e.message_dict)
                code = status.HTTP_400_BAD_REQUEST
        return response.Response(data=msg, status=code)

@method_decorator(csrf_protect, name="post")
class UserLogin(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request: request.HttpRequest, format='json') -> response.Response:
        serializer: LoginSerializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data

            if user is not None:
                login(request=request, user=user)
                return response.Response(data={
                    "user": UserSerializer(user, context=self.get_serializer_context()).data
                    }, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f'failed to login user: {user}')
        except BaseException as err:
            logger.error(f'error: {err}')
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

@method_decorator(all_decorators, name="get")
@method_decorator(all_decorators, name="post")
@method_decorator(all_decorators, name="delete")
class GetNumbers(generics.ListCreateAPIView, generics.DestroyAPIView):
    def get_serializer_class(self):    
        if self.request.method == "POST":
            return CallerSerializer
        return NumberSerializer
    
    def get_queryset(self):
        if self.request.method == "DELETE":
            self.lookup_field = "number"
            return Caller.objects.filter(number=self.number)
        return Caller.objects.values('number')

    def post(self, request: request.HttpRequest, *args, **kwargs):
        self.number: str = request.path.strip('/').split('/')[-1]
        caller = tc.get_caller_info(number=self.number)
        caller = {"number": self.number, "country": caller.country_code}

        data, code = None, status.HTTP_400_BAD_REQUEST
        serializer: CallerSerializer = self.get_serializer(data=caller)
        try:
            serializer.is_valid(raise_exception=True)
            added = serializer.create(validated_data=caller)

            if added:
                data = serializer.data
                code = status.HTTP_201_CREATED
        except BaseException as e:
            data = f"Failed to create number: {self.number}. Reason: {e}"
            logger.error(data)
        return response.Response(data=data, status=code)
    
    def delete(self, request: request.HttpRequest, *args, **kwargs):
        self.number: str = request.path.strip('/').split('/')[-1]
        serializer: NumberSerializer = self.get_serializer(data={"number":self.number})

        data, code = None, status.HTTP_400_BAD_REQUEST
        try:
            serializer.is_valid(raise_exception=True)
            return super().delete(request, *args, **kwargs)
        except BaseException as e:
            data = f"Failed to remove number: {self.number}. Reason: {e}"
            logger.error(data)
        return response.Response(data=data, status=code)

@method_decorator(all_decorators, name="get")
class GetMessages(generics.ListAPIView):
    serializer_class: MessageSerializer = MessageSerializer

    def get_queryset(self):
        num = self.kwargs['number']
        return Message.objects.filter(number=num)

@decorators.login_required
def index(request: request.HttpRequest):
    return render(request, 'index.html')

