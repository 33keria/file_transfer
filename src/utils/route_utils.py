from typing import Callable, Any, Coroutine
import uuid
import json
import sys

import structlog
from fastapi.routing import APIRoute
from fastapi import Request, Response, HTTPException
from fastapi.exceptions import RequestValidationError

from configs import settings


async def get_request_body(request: Request) -> dict:
    """获取请求入参

    Args:
        request (Request)
    """
    # get request body
    try:
        body = await request.body()
        if sys.getsizeof(body) > (1024*1024):
            body = "<body size too big to view>"
        # else:
        #     raise HTTPException(status_code=400, detail=f"Unknown request method:{request.method}")
    except json.decoder.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return body


async def get_trace_id():
    trace_id = settings.TRACEID_CONTEXT.get('')
    if not trace_id:
        trace_id = uuid.uuid4().hex
        settings.TRACEID_CONTEXT.set(trace_id)
    return trace_id


async def clean_trace_id():
    token = settings.TRACEID_CONTEXT.set('')
    settings.TRACEID_CONTEXT.reset(token)


class ApiLogRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handler = super().get_route_handler()
        
        async def auth_body(request: Request) -> Response:
            logger = structlog.get_logger()
    
            headers = dict(request.headers)
            logger = logger.bind(headers=headers, trace_id=await get_trace_id())

            body = await get_request_body(request)
            logger.info(
                "Get request", 
                input=body, 
                headers=headers,
                url=request.url)

            try:
                res = await handler(request)
                if hasattr(res, "body"):
                    logger.info("Request response", res=res.body)
                else:
                    logger.info("Request response", res=res)
                return res
            except RequestValidationError as exc:
                body = await request.body()
                detail = {"errors": exc.errors(), "body": body.decode()}
                raise HTTPException(status_code=400, detail=detail)
            finally:
                await clean_trace_id()
        return auth_body