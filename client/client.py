# coding=utf8
import Tkinter
import socket
import thread
from time import sleep


class Client(object):
    """docstring for Client."""
    def __init__(self, host='localhost', port=9000):
        super(Client, self).__init__()
        self.host = host
        self.port = port
        self.records_requested_flag = False
        self.records_generated_flag = False
        self.records_request_sent_flag = False

        self.root = Tkinter.Tk()

        self.btn_width = 50
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
        self.get_btn['state'] = 'disabled'

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
        pass

    def process_records(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.sendall('gen')
        # data = tuple(sock.recv(1024).split('~'))
        state = ''
        while True:
            data = tuple(sock.recv(1024).split('~'))
            print data
            if not data[0]:
                break
            elif data[0] == 'state':
                state = data[1]
                if state == 'SUCCESS':
                    self.get_btn['state'] = 'active'
                    self.gen_btn['text'] = (
                        u'Сгенерировать список записей (Готово)')
                    sock.sendall('ok')
                elif state != 'SUCCESS':
                    self.gen_btn['text'] = (
                        u'Сгенерировать список записей (Запрос обрабатывается)')
                    print 'sending state request'
                    sock.sendall('state?')
            elif state != 'SUCCESS':
                print 'sending state request'
                sock.sendall('state?')
            elif self.records_requested_flag:
                print 'sending get signal'
                sock.sendall('get')
                self.records_requested_flag = False
            elif data[0] == 'rec':
                sock.send('go')
                with open('records.txt', 'w') as records:
                    data = sock.recv(1024)
                    # print data
                    while data:
                        records.write(data)
                        data = sock.recv(1024)
                    else:
                        print 'Bye, {}:{}'.format(self.host, self.port)
                        break
            else:
                sock.sendall('ok')


        sock.close()

    def request_records(self, event):
        if self.gen_btn['state'] == 'active':
            thread.start_new_thread(self.process_records, tuple())
            self.gen_btn['state'] = 'disabled'

    def receive_records(self, event):
        if self.get_btn['state'] == 'active':
            self.records_requested_flag = True
            self.get_btn['state'] = 'disabled'

    def send_data(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))

        connector = '~'
        message = connector.join([field.get() for field in
            [self.lastname, self.firstname, self.middlename, self.birth_date]])
        sock.sendall('add{}{}'.format(connector, message))
        sock.close()

        self.form.destroy()

if __name__ == '__main__':
    client = Client()
    client.run()
