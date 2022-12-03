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
        print(time.time())
        data = (await reader.read(1024)).decode()
        print(time.time())
        address = writer.get_extra_info('peername')
        print(writer.get_extra_info('socket'))
        if data == '200':
            score = 0
            log.info("客户端IP:{0},端口号:{1}连接服务器成功，准备分发试题".format(address[0], address[1]))
            question = await load_question()
            for i, q in enumerate(question):
                if q["type"] == "chose":
                    question = str(q["question"])
                    option1 = str(q["option1"])
                    option2 = str(q["option2"])
                    option3 = str(q["option3"])
                    option4 = str(q["option4"])
                    answer = str(q["answer"])
                    sendContent = str(i + 1) + "/10" + question + option1 + option2 + option3 + option4
                    writer.write(sendContent.encode())
                    await writer.drain()
                    if (await reader.read(1024)).decode() == answer:
                        score += 10
                        writer.write("回答正确,你目前的分数为{}".format(str(score)).encode())
                        await writer.drain()
                    else:
                        writer.write("回答错误，正确答案为{0},你目前的分数为{1}".format(answer, str(score)).encode())
                        await writer.drain()
                else:
                    question = str(i + 1) + "/10" + str(q["question"])
                    answer = str(q["answer"])
                    writer.write(question.encode())
                    await writer.drain()
                    if (await reader.read(1024)).decode() == answer:
                        score += 10
                        writer.write("回答正确,你目前的分数为{}".format(str(score)).encode())
                        await writer.drain()
                    else:
                        writer.write("回答错误，正确答案为{0},你目前的分数为{1}".format(answer, str(score)).encode())
                        await writer.drain()
            log.info("客户端:{0}:{1}考试结束，得分为{2}".format(address[0], address[1], str(score)))
            writer.write("考试结束，总得分为为{}".format(str(score)).encode())
            await writer.drain()
        else:
            log.error("IP:{0},端口号:{1}连接失败".format(address[0], address[1]))
        writer.close()
    except OSError:
        print("error")


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
