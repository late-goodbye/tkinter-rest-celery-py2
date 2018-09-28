# coding=utf8
import Tkinter
import socket
import sys
import datetime

class Client(object):
    """docstring for Client."""
    def __init__(self, host='localhost', port=9000):
        super(Client, self).__init__()
        self.host = host
        self.port = port

        self.connector = '~'
        self.records_filename = ''

        self.create_main_window()

    def create_main_window(self):
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

        self.add_btn.bind('<Button-1>', self.open_form)
        self.gen_btn.bind('<Button-1>', self.request_records)
        self.get_btn.bind('<Button-1>', self.receive_records)

        self.gen_btn.pack()
        self.add_btn.pack()
        self.get_btn.pack()

    def open_form(self, event):
        self.form = Tkinter.Toplevel()
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
            self.form, text=u'Сохранить', command=self.send_person_data)
        self.save_btn.grid(row=5, column=0)

        self.cancel_btn = Tkinter.Button(
            self.form, text=u'Отмена', command=self.form.destroy)
        self.cancel_btn.grid(row=5, column=1)

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            self.log('Error creating socket', e)

        try:
            self.sock.connect((self.host, self.port))
        except socket.gaierror, e:
            self.log('Address-related error connecting to server', e)
        except socket.error, e:
            self.log('Connection error', e)

    def send_person_data(self):
        self.connect_to_server()
        message = self.connector.join([field.get() for field in
            [self.lastname, self.firstname, self.middlename, self.birth_date]])
        self.form.destroy()
        print 'message: {}'.format(message)
        try:
            self.sock.sendall('add{}{}\n'.format(self.connector, message))
        except socket.error, e:
            self.log('Error sending data', e)
        print 'message has been sent'

        try:
            res = self.sock.recv(1)
            print res
        except socket.error, e:
            res = False
            self.log('Error receiving data', e)
        finally:
            self.sock.close()
            self.show_add_person_result(success=res)

    def request_records(self, event):
        self.connect_to_server()
        try:
            self.sock.sendall('gen\n')
        except socket.error, e:
            self.log('Error sending data', e)

        try:
            self.records_filename = self.sock.recv(1024)
        except socket.error, e:
            self.log('Error receiving data', e)

        print 'Records filename: {}'.format(self.records_filename)


    def receive_records(self, event):
        pass

    def show_add_person_result(event, success):
        print success
        result_window = Tkinter.Toplevel()
        label_text = u'Успешно' if success else u'Ошибка'
        print label_text
        label = Tkinter.Label(result_window, text=label_text)
        ok_btn = Tkinter.Button(
            result_window, text=u'OK', command=result_window.destroy)
        label.pack()
        ok_btn.pack()


    def log(self, desc, e):
        """ Adds information into log file in case of exception catched """
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = '{} -- {}, {}'.format(time, desc, e)
        with open('log.txt', 'a') as log:
            log.write('{}\n'.format(message))
        self.show_error(message)
        sys.exit(1)

    def load_logs(self, event):
        """ Clears text box in log window and fills it with all logs """
        self.text_box['state'] = 'normal'
        self.text_box.delete('1.0', Tkinter.END)
        with open('log.txt', 'r') as log:
            for record in log:
                self.text_box.insert('end', record)
        self.text_box['state'] = 'disabled'

    def show_error(self, message):
        """
        Shows last exception in new window
        If logs requested by pressing a button, shows all catched exceptions
        """
        self.error_window = Tkinter.Toplevel()
        self.text_box = Tkinter.Text(self.error_window, wrap='word')
        self.text_box.insert('end', message)
        self.text_box['state'] = 'disabled'
        self.text_box.pack(side='left')

        self.scrollbar = Tkinter.Scrollbar(self.error_window)
        self.scrollbar.pack(side='right')
        self.scrollbar['command'] = self.text_box.yview
        self.text_box['yscrollcommand'] = self.scrollbar.set

        self.log_btn = Tkinter.Button(self.error_window, text=u'Вывести логи')
        self.log_btn.bind('<Button-1>', self.load_logs)
        self.log_btn.pack(side='bottom')

    def run(self):
        """ The entry point """
        self.root.mainloop()


if __name__ == '__main__':
    client = Client()
    client.run()
