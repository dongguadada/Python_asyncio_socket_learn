# -*- coding = utf-8 -*-
# @Time : 2022/11/15 22:38
# @Author :
# @File : __init__.py
# @Software : PyCharm

import tkinter as tk
from tkinter import messagebox


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.createWidget()

    def createWidget(self):
        self.label1 = tk.Label(self, text="用户名", width=10, height=2).pack()
        self.v1 = tk.StringVar()
        self.entry1 = tk.Entry(self,textvariable=self.v1, show="*").pack()
        self.btn = tk.Button(self, text="点我", command=self.__click).pack()
        self.btnquick = tk.Button(self, text="退出", command=self.master.destroy).pack()


    def __click(self):
        messagebox.showinfo("Message", self.v1.get())


if __name__ == '__main__':
    root = tk.Tk()
    root.title("考试客户端")
    root.geometry("500x300+200+300")
    app = Application(master=root)
    root.mainloop()
