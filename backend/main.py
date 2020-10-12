import asyncio
from contextlib import AsyncExitStack

import aiohttp
from aiohttp import web
import aioredis
import databases

from backend import settings
from backend.resources import resources
from backend.user.auth import register_user, login_user, ValidationError
from backend.libs.auth import parse_user_id_from_auth_token
from backend.user_task_queue import UserTaskQueue
from backend.utils.jrpc import format_jrpc_response


async def handle(request):
    with open('/work/index.html', 'r+') as f:
        return web.Response(text=f.read(), content_type='text/html')


async def register_handler(request):
    data = await request.json()
    try:
        token = await register_user(data)
    except ValidationError:
        return web.json_response(
            format_jrpc_response(error={'text': 'wrong data'})
        )
    response_data = {}
    if token:
        response_data['token'] = token
    return web.json_response(format_jrpc_response(response_data))


async def login_handler(request):
    data = await request.json()
    try:
        token = await login_user(data)
    except ValidationError:
        return web.json_response(
            format_jrpc_response(error={'text': 'wrong data'})
        )
    response_data = {}
    if token:
        response_data['token'] = token
    return web.json_response(format_jrpc_response(response_data))


async def socket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    user_id = None
    async for msg in ws:
        try:
            data = msg.json()
        except Exception as e:
            print(f'Unknown message exception {e}', flush=True)
            continue

        user_id = parse_user_id_from_auth_token(data.get("id"))
        if not user_id:
            await ws.close()
            continue

        user_queue = request.app['users_map'].get(user_id)
        if user_queue is None:
            user_queue = UserTaskQueue(ws)
            request.app['users_map'][user_id] = user_queue
            asyncio.create_task(user_queue.start())

        user_queue.push_message(data)

        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print(
                'ws connection closed with exception %s' % ws.exception(),
                flush=True
            )

    user_queue = request.app['users_map'].pop(user_id, None)
    if user_queue:
        await user_queue.queue.join()

    print('websocket connection closed', flush=True)
    return ws


async def init_user_queue(app):
    app['users_map'] = {}


async def close_user_queue(app):
    await asyncio.gather(
        *(
            users_queue.queue.join()
            for users_queue in app['users_map'].values()
        )
    )


async def setup_resources(app):
    async with AsyncExitStack():
        db = databases.Database(settings.DATABASE_URL)
        await db.connect()
        app['database'] = db
        cache_conf = settings.CONFIG['cache']
        redis = await aioredis.create_redis_pool(
            [cache_conf['host'],
             cache_conf['port']],
            encoding='utf-8',
            db=1,
        )
        app['cache'] = redis
        resources.ctx_db.set(db)
        resources.ctx_cache.set(redis)

        yield

        await db.disconnect()
        redis.close()
        await redis.wait_closed()


def create_app():
    app = web.Application()
    app.add_routes(
        [
            web.get('/', handle),
            web.get('/ws', socket_handler),
            web.post('/register', register_handler),
            web.post('/login', login_handler),
        ]
    )
    app.on_startup.extend([init_user_queue])
    app.on_cleanup.extend([close_user_queue])
    app.cleanup_ctx.extend([setup_resources])
    return app


def start_app():
    app = create_app()
    web.run_app(app, port=8000)


if __name__ == '__main__':
    start_app()
