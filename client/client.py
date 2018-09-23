# coding=utf8
import Tkinter
import socket


class Client(object):
    """docstring for Client."""
    def __init__(self, host='localhost', port=9000):
        super(Client, self).__init__()
        self.host = host
        self.port = port

        self.root = Tkinter.Tk()

        self.btn_width = 40
        self.gen_btn = Tkinter.Button(
            self.root,
            text=u'Сгенерировать список записей',
            width=self.btn_width)

        self.add_btn = Tkinter.Button(
            self.root,
            text=u'Добавить новую запись',
            width=self.btn_width)

        self.get_btn = Tkinter.Button(
            self.root,
            text=u'Получить список записей',
            width=self.btn_width)

        self.add_btn.bind('<Button-1>', self.open_form)
        self.gen_btn.bind('<Button-1>', self.request_records)
        self.get_btn.bind('<Button-1>', self.receive_records)

        self.gen_btn.pack()
        self.add_btn.pack()
        self.get_btn.pack()

    def open_form(self, event):
        self.form = Tkinter.Tk()
        Tkinter.Label(self.form, text=u'Фамилия').grid(row=0, column=0)
        Tkinter.Label(self.form, text=u'Имя').grid(row=1, column=0)
        Tkinter.Label(self.form, text=u'Отчество').grid(row=2, column=0)
        Tkinter.Label(self.form, text=u'Дата рождения').grid(row=3, column=0)

        self.lastname = Tkinter.Entry(self.form)
        self.lastname.grid(row=0, column=1)

        self.firstname = Tkinter.Entry(self.form)
        self.firstname.grid(row=1, column=1)

        self.middlename = Tkinter.Entry(self.form)
        self.middlename.grid(row=2, column=1)

        self.birth_date = Tkinter.Entry(self.form)
        self.birth_date.grid(row=3, column=1)

        self.save_btn = Tkinter.Button(
            self.form, text=u'Сохранить', command=self.send_data)
        self.save_btn.grid(row=5, column=0)

        self.cancel_btn = Tkinter.Button(
            self.form, text=u'Отмена', command=self.form.destroy)
        self.cancel_btn.grid(row=5, column=1)

    def run(self):
        self.root.mainloop()

    def send(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.sendall(message)
        sock.close()

    def request_records(self, event):
        self.send('gen')

    def receive_records(self, event):
        self.send('get')

    def send_data(self):
        connector = '~'
        message = connector.join([field.get() for field in
            [self.lastname, self.firstname, self.middlename, self.birth_date]])
        self.send('add{}{}'.format(connector, message))
        self.form.destroy()


if __name__ == '__main__':
    client = Client()
    client.run()
