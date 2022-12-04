# -*- coding = utf-8 -*-
# @Time : 2022/11/15 22:38
# @Author :
# @File : client.py
# @Software : PyCharm
import asyncio
import re
import sys
from tkinter import messagebox
import time
import tkinter as tk




class App:
    def __init__(self):
        self.score = 0
        self.root = tk.Tk()
        self.endTime = 0
        self.v = tk.StringVar()
        self.type_ = ''
        self.question = ''
        self.chose = ''
        self.__create()
        self.__bind()
        self.root.mainloop()
        self.Message = None
        self.label2 = None
        self.Rad1 = None
        self.Rad2 = None
        self.Rad3 = None
        self.Rad4 = None
        self.writer = None
        self.reader = None

    def __create(self):
        self.v.set('0')
        self.root.title("考试客户端")
        self.root.geometry("250x80+600+200")
        self.root.iconphoto(False, tk.PhotoImage(file='./res/考试.png'))
        self.root.resizable(False, False)
        self.Message = tk.Message(self.root, text="学 号:", width=50)
        self.entry1 = tk.Entry(self.root)
        self.btnLogin = tk.Button(self.root, text="登入", command=self.__checkAccount)

    def __bind(self):
        self.Message.grid(row=0, column=0)
        self.btnLogin.grid(row=1, column=3)
        self.entry1.grid(row=0, column=3)

    def __checkAccount(self):
        StuNum = self.entry1.get()
        if re.fullmatch('^[0-9]{12}$', StuNum):
            self.Message.destroy()
            self.entry1.destroy()
            self.btnLogin.destroy()
            self.root.geometry('400x200')
            asyncio.run(self.tcp_c(StuNum))
        else:
            messagebox.showinfo("提醒", "请输入正确的考号")

    async def tcp_c(self, StuNum):
        self.reader, self.writer = await asyncio.open_connection('192.168.140.1', 7890)
        self.writer.write(StuNum.encode())
        await self.writer.drain()
        _time = int((await self.reader.read(1024)).decode())
        self.endTime = int(time.time()) + _time
        self.label2 = tk.Label(self.root, text="1")
        self.label2.grid(row=0, column=3)
        await asyncio.create_task(self.__get_question())
        await asyncio.create_task(self.test())
        await asyncio.create_task(self.keep_update())
        self.writer.close()
        await self.writer.wait_closed()

    async def keep_update(self):
        while True:
            await asyncio.sleep(0)  # 让出cpu资源
            _time = self.endTime - int(time.time())
            minute = str(int(_time / 60))
            second = str(_time % 60)
            if _time:
                self.label2['text'] = "剩余时间:{0}:{1}".format(minute, second)
                self.root.update()
            else:
                messagebox.showinfo("考试结束", f"你的成绩为{str(self.score)!r}")
                self.writer.close()
                await self.writer.wait_closed()
                self.root.destroy()
                sys.exit()

    async def test(self):
        if self.type_ == "chose":
            self.Message = tk.Message(self.root, text=self.question, width=300)
            self.Message.grid(row=0, column=0)
            self.Rad1 = tk.Radiobutton(self.root, text='A' + re.search('A(.*?)!', self.chose).groups()[0],
                                       variable=self.v, value='A')
            self.Rad1.grid(row=1, column=0, sticky='w')
            self.Rad2 = tk.Radiobutton(self.root, text='B' + re.search('B(.*?)!', self.chose).groups()[0],
                                       variable=self.v, value='B')
            self.Rad2.grid(row=2, column=0, sticky='w')
            self.Rad3 = tk.Radiobutton(self.root, text='C' + re.search('C(.*?)!', self.chose).groups()[0],
                                       variable=self.v, value='C')
            self.Rad3.grid(row=3, column=0, sticky='w')
            self.Rad4 = tk.Radiobutton(self.root, text='D' + re.search('D(.*?)!', self.chose).groups()[0],
                                       variable=self.v, value='D')
            self.Rad4.grid(row=4, column=0, sticky='w')
            tk.Button(self.root, text="提交", command=lambda: asyncio.create_task(
                self.__checkAnswer(self.chose[-1], self.v.get()))).grid(row=5, column=0)
        else:
            v = tk.StringVar()
            v.set('0')
            self.Message = tk.Message(self.root, text=self.question, width=300)
            self.Message.grid(row=0, column=0, sticky='w')
            self.Rad1 = tk.Radiobutton(self.root, text='正确', variable=self.v, value='A')
            self.Rad1.grid(row=1, column=0, sticky='w')
            self.Rad2 = tk.Radiobutton(self.root, text='错误', variable=self.v, value='B')
            self.Rad2.grid(row=2, column=0, sticky='w')
            self.Rad3 = tk.Radiobutton(self.root, variable=self.v, value='C')
            self.Rad3.grid(row=3, column=0, sticky='w')
            self.Rad4 = tk.Radiobutton(self.root, variable=self.v, value='D')
            self.Rad4.grid(row=4, column=0, sticky='w')
            self.Rad3.grid_remove()
            self.Rad4.grid_remove()
            tk.Button(self.root, text="提交", command=lambda: asyncio.create_task(
                self.__checkAnswer(self.chose, self.v.get()))).grid(row=5, column=0)

    async def __checkAnswer(self, answer: str, reply: str):
        print(answer)
        if answer == reply:
            self.score += 10
            self.writer.write("T".encode())
            try:
                await asyncio.create_task(self.__get_question())
            except ConnectionResetError:
                messagebox.showinfo("考试结束", f"你的成绩为{str(self.score)!r}")
                sys.exit()
            self.__modify()
        else:
            self.writer.write("F".encode())
            messagebox.showinfo("回答错误", f"本题正确答案为{answer!r}")
            try:
                await asyncio.create_task(self.__get_question())
            except ConnectionResetError:
                messagebox.showinfo("考试结束", f"你的成绩为{str(self.score)!r}")
                sys.exit()
            self.__modify()

    async def __get_question(self):
        self.type_ = (await self.reader.read(1024)).decode()
        if self.type_ == "chose":
            self.writer.write("question".encode())
            await self.writer.drain()
            self.question = (await self.reader.read(1024)).decode()
            self.writer.write("chose".encode())
            await self.writer.drain()
            self.chose = (await self.reader.read(1024)).decode()
        else:
            self.writer.write("question".encode())
            await self.writer.drain()
            self.question = (await self.reader.read(1024)).decode()
            self.writer.write("chose".encode())
            await self.writer.drain()
            self.chose = 'A' if (await self.reader.read(1024)).decode() == '对' else 'B'
        print(self.chose[-1])

    def __modify(self):
        self.v.set('0')
        if self.type_ == "chose":
            self.Message['text'] = self.question
            self.Rad1['text'] = 'A' + re.search('A(.*?)!', self.chose).groups()[0]
            self.Rad2['text'] = 'B' + re.search('B(.*?)!', self.chose).groups()[0]
            self.Rad3['text'] = 'C' + re.search('C(.*?)!', self.chose).groups()[0]
            self.Rad3.grid()
            self.Rad4['text'] = 'D' + re.search('D(.*?)!', self.chose).groups()[0]
            self.Rad4.grid()
        else:
            self.Message['text'] = self.question
            self.Rad1['text'] = "正确"
            self.Rad2['text'] = "错误"
            self.Rad3.grid_remove()
            self.Rad4.grid_remove()


if __name__ == '__main__':
    App()
