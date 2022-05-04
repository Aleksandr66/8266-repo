
# def tcp_callback():
import os
import pathlib
import asyncio
import time
import aiohttp.web as web
from aiohttp import WSCloseCode
from aiohttp.web import middleware
# from aiohttp_se
import logging


from typing import Any
from aiomisc import entrypoint, Service, get_context
from aiomisc.service.aiohttp import AIOHTTPService
from aiomisc.service import TCPServer, MemoryTracer, Profiler, RespawningProcessService
from aiomisc.service.sdwatchdog import SDWatchdogService
from aiomisc.service.periodic import PeriodicService
#from aiomultiprocess import Pool
#from aiomisc.log import basic_config
# GLOBAL FIXME
WS_FILE = os.path.join(os.path.dirname(__file__), "index.html")
root_path = str(pathlib.Path(__file__).parent)+'/'
# Configure logging
#basic_config(level=logging.DEBUG, buffered=False, log_format='color')
#log = logging.getLogger(__name__)
#########################################
# logging
# logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
# logging.getLogger('aiohttp.client').setLevel(logging.WARNING)
# logging.getLogger('aiohttp.internal').setLevel(logging.WARNING)
# logging.getLogger('aiohttp.server').setLevel(logging.WARNING)
# logging.getLogger('aiohttp.web').setLevel(logging.WARNING)
# logging.getLogger('aiohttp.websocket').setLevel(logging.WARNING)
#####################################
# @middleware


async def web_middle(request, handler):
    # resp = await handler(request)
    #resp.text = resp.text + ' wink'
    print("in middle", request, handler)
    return request


class EchoServer(TCPServer):
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        ID = False
        print("->device connection tcp", self.context, self.c)
        print(f"", TCPServer)
        self.context['wait_time'] = time.time()
        # await writer.drain()
        while not reader.at_eof():
            # data = await reader.read(3000)
            try:
                data = await asyncio.wait_for(reader.read(3000), timeout=50)
                print("===============\n", data)
            except:
                print("<-device EXCEPT closed")
                break
######################################
        print("<-device connection closed")
        #log.debug(f"data {data}")
        # writer.write()


async def handle(request):
    TKT = request.cookies.get('tkt', False)
    USER = False
    print("->Client connection WS")
    print(f"ws list", request.app["ws"])
    ws_app = request.app["ws"]
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    if not available:
        head = {

        }
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)
    msg = {"connect": True, "news": True, "auth": True}
    await resp.send_json(msg)
    try:
        request.app["ws"].append(resp)
        async for msg in resp:
            print(f"WS========={str(msg.type)}\n{msg.data}")  # msg.json()
            #print("JSON", msg.json)
            # msg.
            # for k, v in msg.json:
            #    print(f"{k}={v}")
            # print(resp)
            #jsn = json.loads(msg.data)
###################
        return resp
###################
    finally:
        request.app["ws"].remove(resp)
        print(f"Someone disconnected. T->{TKT} U->{USER}")


async def ctx_cleanup(app):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!init app", app)
    yield
    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY, message='Server shutdown or restart')
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!clean app", app)


async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY, message='Server shutdown or restart')
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!clean app", app)


# class MyService(PeriodicService):  # Service mega customself.start_event.set()
    # def __init__(self, **kwargs):
    #    self.a = kwargs.get('a', None)
    #    self.b = kwargs.get('b', None)

    # async def callback(self):
    # Send signal to entrypoint for continue running
    #context = get_context()

    # wait_time = await context['wait_time']
    # event.set()
    # Start service task
    #self.context['wait_time'] += 1
    #print("looper", wait_time)
    # await asyncio.sleep(10)

class TCP_service(RespawningProcessService):
    # def __init__(self, n, s, t):
    #print(n, s, t)
    #self.name = n
    #self.surname = s

    def in_process(self) -> Any:

        time.sleep(10)
        #logging.warning("Goodbye mad world")
        print("GOOD BYE", self.t)
        exit(42)


class REST(AIOHTTPService):
    async def create_application(self):
        app = web.Application()
        app["ws"] = []
        app.router.add_static("/build", f'{root_path}/build', show_index=True, append_version=True)
        app.router.add_static("/assets", f'{root_path}/assets', show_index=True, append_version=True)
        app.router.add_static("/img", f'{root_path}/img', show_index=True, append_version=True)
        app.router.add_static("/file", f'{root_path}/file', show_index=True, append_version=True)
        app.router.add_static("/mp3", f'{root_path}/mp3', show_index=True, append_version=True)
        # app.router
        app.router.add_get("/{tail:.*}", handle)
        # app.on_response_prepare.append(web_middle)
        app.cleanup_ctx.append(ctx_cleanup)
        app.on_shutdown.append(on_shutdown)
   # app.add_routes([
   #     web.get('/', handle),
   #     web.get('/{name}', handle)
   # ])

        return app


def main():
    app = REST(address='0.0.0.0', port=80)
    service = (
        app,
        #EchoServer(address='0.0.0.0', port=40804, name=app),
        #MemoryTracer(interval=10, top_results=15),
        #Profiler(interval=15, top_results=15)
        #MyService(interval=10, delay=0, a=2, b=2),
        TCP_service(f=1, t=2, z=3),
        SDWatchdogService(),
    )
    with entrypoint(*service, pool_size=2, log_level='info', log_format='color', log_buffer_size=1024, log_flush_interval=0.2, log_config=True, policy=asyncio.DefaultEventLoopPolicy(), debug=False,) as loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
