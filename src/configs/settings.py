from pathlib import Path
from contextvars import ContextVar

import redis.asyncio as redis

# SERVER CONFIGS
PORT = 10002
ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH.joinpath("data")
TRACEID_CONTEXT = ContextVar("trace_id")
DEBUG = True

# FILE RESPONSE CONFIGS
FILE_CHUNK_SIZE = 1024 * 1024 # 1MB
UPLOAD_DIRECT_SIZE = 1024 * 1024 # 1MB

# FILE CACHE CONFIGS
FILE_CACHE_DIRECTORY = Path("/tmp/upload_cache")

# REDIS KEY PATTERN
# 用户对应分片式文件上传文件计数 FILE_TRANSFER:SPLIT_UPLOAD:<username>_<filename> value count number int
SPLIT_UPLOAD_REDIS_KEY_PATTERN = "FILE_TRANSFER:SPLIT_UPLOAD:%s_%s" 

# REDIS CONFIGS
REDIS_CONNECT_URL = "redis://localhost"
REDIS_CONNECT_POOL = redis.ConnectionPool.from_url(REDIS_CONNECT_URL)