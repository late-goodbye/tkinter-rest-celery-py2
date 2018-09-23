# coding=utf8
import Tkinter


class Client(object):
    """docstring for Client."""
    def __init__(self):
        super(Client, self).__init__()

        self.root = Tkinter.Tk()

        self.btn_width = 40
        self.gen_btn = Tkinter.Button(
            self.root,
            text=u"Сгенерировать список записей",
            width=self.btn_width)

        self.add_btn = Tkinter.Button(
            self.root,
            text=u"Добавить новую запись",
            width=self.btn_width)

        self.get_btn = Tkinter.Button(
            self.root,
            text=u"Получить список записей",
            width=self.btn_width)

        self.gen_btn.pack()
        self.add_btn.pack()
        self.get_btn.pack()

    def run(self):
        self.root.mainloop()
