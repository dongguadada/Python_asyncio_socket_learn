# -*- coding = utf-8 -*-
# @Time : 2022/11/15 22:38
# @Author :
# @File : server.py
# @Software : PyCharm
import json
import os
import time

import Log
import random
import asyncio
import aiofiles  # pip install aiofiles

time = '3600'


async def load_question() -> list:
    d = list()
    async with aiofiles.open(file="./res/question.json", encoding='utf-8') as fp:
        json_str = await fp.read()
        json_data = json.loads(json_str)
        s = set()
        while True:
            s.add(random.randint(0, 99))
            if len(s) > 9:
                break
        for n in s:
            d.append(json_data[str(n).zfill(3)])
    return d


async def do(reader, writer):
    try:
        data = (await reader.read(1024)).decode()
        address = writer.get_extra_info('peername')
        writer.write(time.encode())
        await writer.drain()
        score = 0
        log.info("客户端IP:{0},端口号:{1},学号{2}连接服务器成功，准备分发试题".format(address[0], address[1], data))
        question = await load_question()
        for i, q in enumerate(question):
            if q["type"] == "chose":
                # 发送类型
                writer.write("chose".encode())
                await writer.drain()
                question = str(q["question"])
                # 发送问题
                (await reader.read(1024)).decode()
                writer.write(question.encode())
                await writer.drain()
                # 发送选项加答案
                (await reader.read(1024)).decode()
                option1 = str(q["option1"]) + '!'
                option2 = str(q["option2"]) + '!'
                option3 = str(q["option3"]) + '!'
                option4 = str(q["option4"]) + '!'
                answer = str(q["answer"])
                chose = option1 + option2 + option3 + option4 + "answer" + answer
                writer.write(chose.encode())
                await writer.drain()

                # 接收是否正确
                t = (await reader.read(1024)).decode()
                if t == 'T':
                    score += 10
                    print(score)
            else:
                # 发送类型
                writer.write("judge".encode())
                await writer.drain()
                question = str(q["question"])
                # 发送问题
                (await reader.read(1024)).decode()
                writer.write(question.encode())
                await writer.drain()
                # 发送选项加答案
                (await reader.read(1024)).decode()
                answer = str(q["answer"])
                writer.write(answer.encode())
                await writer.drain()

                # 接收是否正确
                t = (await reader.read(1024)).decode()
                if t == 'T':
                    score += 10
                    log.info("客户端:{0}:{1},学号{2}当前得分为{3}".format(address[0], address[1], data, str(score)))
        writer.write("finish".encode())
        await writer.drain()
        log.info("客户端:{0}:{1},学号{2}考试结束，得分为{3}".format(address[0], address[1], data, str(score)))
        async with aiofiles.open('score.txt', 'a', encoding='utf-8') as fp:
            await fp.write("学号{0}考试结束，得分为{1}".format(data, str(score)))
        writer.close()
    except OSError:
        log.error("连接失败")


async def main(host: str, port: int):
    server = await asyncio.start_server(do, host=host, port=port)
    address = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    log.info(f"Serving on {address}")
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    cur_path = os.path.dirname(os.path.realpath(__file__))
    log_path = os.path.join(cur_path, 'log_server')
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log = Log.Log(cur_path, log_path)
    asyncio.run(main("192.168.140.1", 7890))
