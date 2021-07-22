import os, time, logging, sys
from channels.db import database_sync_to_async
from dotenv import load_dotenv
from django.contrib.auth import hashers, password_validation
from django.core.exceptions import ValidationError

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

ws_url = os.environ.get("WEBSOCKET_URL")
twilio_url = "https://api.twilio.com/"
salt = os.environ.get("SALT")

class database_routines:
    @staticmethod
    @database_sync_to_async
    def insert(model, **attrs):
        model(**attrs).save(force_insert=True)

    @staticmethod
    @database_sync_to_async
    def fetch(model, **attrs):
        return model.objects.get(**attrs)

class password_management():
    def __init__(self, password: str):
        try: 
            password_validation.validate_password(password)
            self.password = password
            self.salt = salt
        except ValidationError:
            raise ValidationError(message={"failure":password_validation.password_validators_help_texts()}, code=500)

    def hash(self) -> str:
        hasher = hashers.PBKDF2PasswordHasher()
        return hasher.encode(password=self.password, salt=self.salt)

def extract_values_from_error(err: dict) -> str:
    items = str()
    for v in err.values():
        items += ' '.join(v) + ' '

    return items.strip(", ")

def setup_logging(path: str) -> logging.Logger:
    if not os.path.exists(path):
        os.mkdir(path)

    unix_time = time.time()
    unix_time = str(unix_time).split('.')[0]

    logger = logging.getLogger("LiveChatApp")
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    shandler = logging.StreamHandler(sys.stdout)
    fhandler = logging.FileHandler(filename=f"{path}/LiveChat_{unix_time}.log")
    shandler.setFormatter(formatter)
    fhandler.setFormatter(formatter)

    logger.addHandler(shandler)
    logger.addHandler(fhandler)
    return logger

logger = setup_logging(os.environ.get("LOGGING_PATH"))