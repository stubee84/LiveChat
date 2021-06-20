import redis, os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

class redisController:
    redis.Connection(host=os.environ['REDIS_HOST'],port=os.environ['REDIS_PORT']).connect()

    @staticmethod
    def set(key: str, value: str):
        try:
            redis.Redis.set(name=key, value=value)
        except redis.RedisError as e:
            raise redis.RedisError(f"failed to set {key}. {e}")

    @staticmethod
    def get(key: str) -> str:
        value = ''
        try:
            value = redis.Redis.get(name=key)
        except redis.RedisError as e:
            raise redis.RedisError(f"failed to set {key}. {e}")
        return value