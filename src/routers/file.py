from typing import Annotated
import os
from urllib.parse import quote, unquote
import sys

from fastapi import  File, UploadFile, Request, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
import aiofiles
import structlog

from configs import settings
from utils.route_utils import ApiLogRoute
from resolvers.resolve_file_upload import FileUploader

router = APIRouter(prefix="/file", route_class=ApiLogRoute)
logger = structlog.get_logger("file")


@router.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    with open("a.pdf", "wb") as f:
        f.write(file)
    return {"file_size": len(file)}


@router.post("/uploadfile/")
async def create_upload_file(request: Request):
    if "filename" not in request.headers or "username" not in request.headers:
        return HTTPException(status_code=400, detail="request error")
    uploader = FileUploader()
    body = await request.body()
    if sys.getsizeof(body) < settings.UPLOAD_DIRECT_SIZE:
        res = await uploader.upload_direct(request=request)
    return res


@router.get("/list/")
async def files_list():
    fp = settings.DATA_PATH
    files = [i.name for i in fp.iterdir()]
    return {"files": files}


@router.get("/get/")
async def get_file(filename: str):
    fp = settings.DATA_PATH.joinpath(filename)
    filesize = os.path.getsize(fp)
    fend = filename.split(".")[-1]
    media_type_map = {
        "pdf": "application/pdf", 
        "mp4": "video/mp4",
        "txt": "text/plain",
    }
    async def iterfile():
        async with aiofiles.open(fp, "rb") as f:
            while chunk := await f.read(settings.FILE_CHUNK_SIZE):
                yield chunk
    headers = {
        'Content-Disposition': 'attachement; filename="%s"' % quote(filename), 
        'filesize': str(filesize)
    }
    return StreamingResponse(iterfile(), headers=headers, media_type=media_type_map[fend])