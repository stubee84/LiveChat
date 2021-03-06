import redis, os
from dotenv import load_dotenv
from typing import List

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

class redisController:
    redis.Connection(host=os.environ['REDIS_HOST'],port=os.environ['REDIS_PORT']).connect()
    redis_obj = redis.Redis()

    @staticmethod
    def set(key: str, value: str):
        try:
            redisController.redis_obj.set(name=key, value=value)
        except redis.RedisError as e:
            raise redis.RedisError(f"failed to set {key}. {e}")

    @staticmethod
    def get(key: str) -> str:
        value = ''
        try:
            value = redisController.redis_obj.get(name=key)
        except redis.RedisError as e:
            raise redis.RedisError(f"failed to set {key}. {e}")
        return value.decode()
    
    @staticmethod
    def delete(key: str) -> bool:
        try:
            if redisController.redis_obj.delete(key) != 0:
                return False
        except redis.RedisError as e:
            raise redis.RedisError(f"failed to delete {key}. {e}")
        return True