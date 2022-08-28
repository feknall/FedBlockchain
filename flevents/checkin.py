# from rest import gateway_rest_api
# import asyncio
# import threading
# from base.support.utils import log_json, log_msg
#
#
# async def periodic(gateway_rest_api):
#     while True:
#         log_msg('Checking-in...')
#         gateway_rest_api.check_in_trainer()
#         await asyncio.sleep(30)
#
#
# def loop_in_thread(loop, gateway_rest_api):
#     loop.create_task(periodic(gateway_rest_api))
#     try:
#         loop.run_forever()
#     except Exception as e:
#         print("Something went wrong", repr(e))
#
#
# def start(gateway_rest_api):
#     loop = asyncio.get_event_loop()
#     t = threading.Thread(target=loop_in_thread, args=(loop, gateway_rest_api, ))
#     t.start()
#
#
