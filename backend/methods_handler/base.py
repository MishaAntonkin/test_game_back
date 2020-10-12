from .main import methods_handler

class BaseMethodHandler:

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        methods_handler.register(cls)

    async def handle(self, message):
        pass
