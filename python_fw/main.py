try:
    import uasyncio as asyncio
except:
    import asyncio

from app import Autoboat

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():
    set_global_exception()  # Debug aid
    app = Autoboat()  # Constructor might create tasks
    # asyncio.create_task(app.startup())  # Or you might do this
    await app.main()  # Non-terminating method
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state
