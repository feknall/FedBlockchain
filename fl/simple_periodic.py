import asyncio
import threading

from identity.base.support.utils import log_msg


class SimplePeriodic:
    def check_in_func(self):
        pass

    async def periodic(self):
        while True:
            log_msg('Checking-in...')
            self.check_in_func()
            await asyncio.sleep(30)

    def loop_in_thread(self, loop):
        loop.create_task(self.periodic())
        try:
            loop.run_forever()
        except Exception as e:
            print("Something went wrong", repr(e))

    def check_in(self):
        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=self.loop_in_thread, args=(loop,))
        thread.start()
