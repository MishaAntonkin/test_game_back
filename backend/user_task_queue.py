import asyncio
import json

from backend.methods_handler import methods_handler


class UserTaskQueue:

    def __init__(self, ws):
        self.queue = asyncio.Queue()
        self.ws = ws

    async def start(self):
        while True:
            msg = await self.queue.get()
            result = await methods_handler.handle(msg)
            if result is not None:
                if isinstance(result, (dict, list)):
                    await self.ws.send_str(json.dumps(result))
                elif isinstance(result, str):
                    await self.ws.send_str(result)
                else:
                    print("unsupported return data", flush=True)
            self.queue.task_done()

    def push_message(self, message):
        self.queue.put_nowait(message)
