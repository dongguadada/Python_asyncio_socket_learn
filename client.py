# -*- coding = utf-8 -*-
# @Time : 2022/11/15 22:38
# @Author :
# @File : client.py
# @Software : PyCharm
import asyncio
import os
import Log
import time


cur_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(cur_path, 'log_client')
if not os.path.exists(log_path):
    os.mkdir(log_path)
log = Log.Log(cur_path, log_path)


async def test(reader, writer):
    try:
        writer.write(b"200")
        for i in range(1, 11):
            print((await reader.read(1024)).decode())
            answer = input("答案")
            writer.write(answer.encode())
            print((await reader.read(1024)).decode())
        print((await reader.read(1024)).decode())
    except asyncio.exceptions.CancelledError:
        print(time.time())


async def tcp_c():
    print(time.time())
    reader, writer = await asyncio.open_connection('192.168.140.1', 7890)
    print(time.time())
    await asyncio.wait_for(test(reader, writer), timeout=10)
    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(tcp_c())
