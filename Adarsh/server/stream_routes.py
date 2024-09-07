import re
import math
import logging
import secrets
import mimetypes
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine

from Adarsh.bot import multi_clients, work_loads
from Adarsh.server.exceptions import FIleNotFound, InvalidHash
from Adarsh.utils.render_template import render_page
from Adarsh.utils.custom_dl import ByteStreamer
from Adarsh.vars import Var
from Adarsh import StartTime, __version__
from ..utils.time_format import get_readable_time

routes = web.RouteTableDef()
class_cache = {}


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    """Root handler for the server."""
    return web.json_response("SK Movies Official")


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def watch_handler(request: web.Request):
    """Handles streaming of media through the /watch endpoint."""
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        
        if match:
            secure_hash, id = match.group(1), int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        
        return web.Response(text=await render_page(id, secure_hash), content_type='text/html')

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)

    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)

    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass

    except Exception as e:
        logging.critical(str(e))
        raise web.HTTPInternalServerError(text=str(e))


@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    """General media stream handler for other paths."""
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)

        if match:
            secure_hash, id = match.group(1), int(match.group(2))
        else:
            id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        
        return await media_streamer(request, id, secure_hash)

    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)

    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)

    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass

    except Exception as e:
        logging.critical(str(e))
        raise web.HTTPInternalServerError(text=str(e))


async def media_streamer(request: web.Request, id: int, secure_hash: str):
    """Handles media streaming by processing range requests."""
    range_header = request.headers.get("Range", 0)
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    if Var.MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect

    logging.debug("Fetching file properties...")
    file_id = await tg_connect.get_file_properties(id)
    logging.debug("File properties fetched.")

    # Validate file hash
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash

    file_size = file_id.file_size

    # Process range header
    if range_header:
        from_bytes, until_bytes = map(
            int, range_header.replace("bytes=", "").split("-")
        )
        until_bytes = until_bytes if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    # Check for invalid ranges
    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    # Stream the file in chunks
    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1
    req_length = until_bytes - from_bytes + 1

    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    # Determine mime type and file name
    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if not mime_type:
        mime_type = "application/octet-stream"
    if not file_name:
        file_name = f"{secrets.token_hex(2)}.unknown"
    
    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
