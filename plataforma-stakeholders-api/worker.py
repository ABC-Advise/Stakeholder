from redis import Redis
from rq import Queue, SimpleWorker
from config import load_redis_config
from configparser import ConfigParser

class DummyApp:
    def __init__(self):
        self.config = {}

parser = ConfigParser()
parser.read("config.ini")
dummy_app = DummyApp()
redis_url = load_redis_config(dummy_app, parser)

conn = Redis.from_url(redis_url)
queue = Queue(connection=conn)

class NoPenalty:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

worker = SimpleWorker([queue], connection=conn)
worker.death_penalty_class = NoPenalty

print("👷 Worker RQ iniciado no modo SimpleWorker (Windows) sem death_penalty...")
worker.work()