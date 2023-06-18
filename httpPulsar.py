__author__ = 'lmpeiris'

import asyncio
from pulsar.apps import http
from ScriptApiClass import ScriptTransformApi
import json
# import aiofiles

template_file = ScriptTransformApi.read_tlg_config('template_file')
http_request_type = ScriptTransformApi.read_tlg_config('http_request_type')
http_target_url = ScriptTransformApi.read_tlg_config('http_target_url')
template_out_file = ScriptTransformApi.read_tlg_config('template_out_file')
data_file = ScriptTransformApi.read_tlg_config('template_out_file')
log_file = 'logs/pulsar_0.log'
tcp_pool_size = int(ScriptTransformApi.read_tlg_config('connection_pool'))
http_timeout = int(ScriptTransformApi.read_tlg_config('http_timeout'))
tcp_close = False

if int(ScriptTransformApi.read_tlg_config('tcp_close')) == 1:
    tcp_close = True

async def send_http_get(target_url, data_string):
    response = await sessions.get(target_url, params=json.loads(data_string))
    log_handler.write(str(response.status_code) + '|' + response.text())

async def send_http_post(target_url, data_string):
    response = await sessions.post(target_url, data=data_string)
    log_handler.write(str(response.status_code) + '|' + response.text())


if __name__ == '__main__':
    print("INFO - starting pulsar HTTP client")
    log_handler = open(log_file, 'w')
    # create async pulsar sessions
    sessions = http.HttpClient(pool_size=tcp_pool_size, close_connections=tcp_close, timeout=http_timeout, verify=False)
    # initialise an empty event loop (python standard async)
    loop = asyncio.get_event_loop()
    tasks = []
    if http_request_type == 'GET':
        for line in open(data_file, 'r'):
            tasks.append(asyncio.ensure_future(send_http_get(http_target_url, line)))
    elif http_request_type == 'POST':
        for line in open(data_file, 'r'):
            tasks.append(asyncio.ensure_future(send_http_post(http_target_url, line)))


    # add created tasks array and ask to be run until all events are complete, async
    print("INFO - Adding " + str(len(tasks)) + " tasks to loop is complete")
    loop.run_until_complete(asyncio.wait(tasks))
    print("INFO - pulsar HTTP client completed")
    loop.close()
    log_handler.close()
