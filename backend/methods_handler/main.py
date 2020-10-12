class MethodsHandler:

    def __init__(self):
        self.handlers = {}

    def register(self, handler_cls):
        handler = handler_cls()
        self.handlers[handler.method] = handler

    async def handle(self, message: dict):
        method_name = message.get('method')
        if method_name in self.handlers:
            return await self.handlers[method_name].handle(message)
        else:
            print("Not existed method type, discard", flush=True)


methods_handler = MethodsHandler()
