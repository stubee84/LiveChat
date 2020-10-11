import twilio.rest, os, asyncio, requests, json, google.auth
import google.auth.transport.requests as tr_requests
from dotenv import load_dotenv
from google.cloud import storage, speech
from google.resumable_media.requests import ResumableUpload

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

sid = os.environ.get("TWILIO_ACCOUNT_SID")
token = os.environ.get("TWILIO_AUTH_TOKEN")
phone_number = os.environ.get("TWILIO_NUMBER")
twilio_url = "https://api.twilio.com/"

class google_controller:
    storage_client: storage.Client = None
    speech_client: speech.SpeechClient = None
    transport: tr_requests.AuthorizedSession = None
    bucket_name: str = os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET_NAME")
    # bucket_name: str = "rare-charmer-214613.appspot.com"
    upload_url: str = u'https://www.googleapis.com/upload/storage/v1/b/{bucket}/o?uploadType=resumable'.format(bucket=bucket_name)
    wr_scope: str = u'https://www.googleapis.com/auth/devstorage.read_write'

    def connect(**kwargs):
        '''
            params: destination - for connection to Google Cloud Storage use `storage`
        '''
        try:
            if kwargs['destination'].lower() == "storage":
                google_controller.storage_client = storage.Client()
                credentials, _ = google.auth.default(scopes=(google_controller.wr_scope,))
                google_controller.transport = tr_requests.AuthorizedSession(credentials)
            elif kwargs['destination'].lower() == "speech":
                google_controller.speech_client = speech.SpeechClient()
        except KeyError as e:
            print(e)
            return

    def download_audio_and_upload(recording_sid: str, recording_url: str) -> str:
        chunk_resp: requests.Response = None
        response = requests.get(url=recording_url, stream=True)
        # filename = f"{recording_sid}.wav"
        content_type = u"audio/wav"
        # #metadata name key is the blob_name to upload to
        metadata = {u'name': recording_sid}

        google_controller.connect(destination="storage")
        #chunk must be divisible by 256.0
        upload = ResumableUpload(google_controller.upload_url, 1024 * 256)
        #the response.raw is the raw bytes from http response. it is only useable if you provide stream=True in the request
        gc_resp = upload.initiate(google_controller.transport, response.raw, metadata, content_type, stream_final=False)

        if gc_resp.status_code == 200:
            while not upload.finished:
                chunk_resp = upload.transmit_next_chunk(google_controller.transport)
        else:
            print(resp.status_code)

        return 'gs://{bucket_name}/{blob_name}'.format(google_controller.bucket_name, recording_sid)
        # with open(file=filename, mode='wb') as f:
        #     for chunk in req.iter_content(chunk_size=1024):
        #         if chunk:
        #             f.write(chunk)
        
        # google_controller.connect(destination="storage")
        # google_controller.upload_to_google_cloud(file_name=os.path.realpath(filename), sid=recording_sid)

    def transcribe_audio(gcs_uri: str) -> str:
        google_controller.connect(destination="speech")
        audio = speech.RecognitionAudio(uri=gcs_uri)
        config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,sample_rate_hertz=8000,language_code="en-US")

        operation = google_controller.speech_client.long_running_recognize(request={"config":config,"audio":audio})

        print("Waiting for operation to complete")
        response = operation.result(timeout=90)

        for result in response.results:
            transcript = u'Transcript: {}'.format(result.alternatives[0].transcript)
            print(u'Confidence: {}'.format(result.alternatives[0].confidence))
        
        return transcript

    
    def upload_to_google_cloud(file_name: str, sid: str) -> bool:
        try:
            bucket = google_controller.storage_client.bucket(google_controller.bucket_name)
            blob = bucket.blob(sid)
            blob.upload_from_filename(filename=file_name)
            return True
        except BaseException as e:
            print(e)
            return False

    def download_audio_and_transcribe():
        chunk_resp: requests.Response = None
        google_controller.connect(destination="speech")
        response = requests.get(url=recording_url, stream=True)

        requests = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in response.iter_content())
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=8000,
            language_code="en-US",
        )
        streaming_config = speech.StreamingRecognitionConfig(config=config)

        responses = google_controller.speech_client.streaming_recognize(config=streaming_config, requests=requests,)

        for response in responses:
            # Once the transcription has settled, the first result will contain the
            # is_final result. The other results will be for subsequent portions of
            # the audio.
            for result in response.results:
                print("Finished: {}".format(result.is_final))
                print("Stability: {}".format(result.stability))
                alternatives = result.alternatives
                # The alternatives are ordered from most likely to least.
                for alternative in alternatives:
                    print("Confidence: {}".format(alternative.confidence))
                    print(u"Transcript: {}".format(alternative.transcript))

class twilio_controller:
    #Rest client variable. Maybe call this rest_clients
    twilio_client: twilio.rest.Client = None
    
    async def connect(**kwargs):
        try:
            if kwargs['destination'] == "Twilio":
                await twilio_controller.twilio_connect(sid=sid,token=token)
        except KeyError:
            return

    #Maybe: put these two functitons into their own twilio child class
    async def twilio_connect(sid: str, token: str):
        if twilio_controller.twilio_client is None:
            twilio_controller.twilio_client = twilio.rest.Client(username=sid,password=token)
        
    async def twilio_send_message(to_number: str, body: str) -> bool:
        result = twilio_controller.twilio_client.messages.create(to=to_number,from_=phone_number,body=body)
        #possibly change this to query the URI for status once it has been sent or received
        if result._properties["status"] == "queued":
            return True
        return False