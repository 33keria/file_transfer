

from fastapi import Request, HTTPException
import aiofiles
import structlog
from urllib.parse import unquote

from configs import settings
from utils.route_utils import get_trace_id

logger = structlog.get_logger("resolve_file_upload")


class FileUploader:
    async def upload_direct(self, request: Request):
        """
        当上传文件小于大小限制，直接读取写入存储路径

        Args:
            request (Request): 请求对象
            filename (str): 上传文件名
        """
        filename = unquote(request.headers["filename"])
        fp = settings.DATA_PATH.joinpath(filename)
        try:
            async with aiofiles.open(fp, "wb") as f:
                async for chunk in request.stream():
                    await f.write(chunk)
        except Exception as error:
            logger.error("Failed to upload file", error=error)
            return {"ok": False, "error": "Failed to upload file"}
            
        return {"ok": True, "filename": filename, "error": ""}
    
    async def upload_split(
            self, 
            request: Request, 
            body: bytes, 
        ):
        """
        当上传文件总体大小超出直接上传限制执行分批上传

        Args:
            request (Request): 
        """
        trace_id = await get_trace_id()
        # TODO: 1. 将上传的文件分割数据保存至缓存目录
        # 分割文件保存路径settings.FILE_CACHE_DIRECTORY/<username>_<filename>/<index>.temp
        username = request.headers["username"]
        filename = request.headers["filename"]
        if "index" not in request.headers:
            logger.error(
                "当上传文件总体大小超出直接上传限制执行分批上传 请求头缺失index",
                trace_id=trace_id,
                headers=request.headers
            )
            return HTTPException(status_code=400, detail="request error")
        file_index = request.headers["index"]
        temp_dir = "%s_%s" % (username, filename)
        temp_filename = "%s.temp" % file_index
        fp = settings.FILE_CACHE_DIRECTORY.joinpath(temp_dir, temp_filename)
        async with aiofiles.open(fp, "wb") as f:
            await f.write(body)
        
        # TODO: 2. 确认文件分割部分全部上传完毕进行数据合并
