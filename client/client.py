# coding=utf8
import Tkinter
from Tkinter import END
import socket
import sys
import thread
from time import sleep
import datetime


class Client(object):
    """
    Client is independent class working in infinite loop with gui.
    During an instance initiation host and port have to be defined.
    The default values are 'localhost' and 9000
    Main window contains three buttons

    To prevent a user from wrong actions the buttons may be activated and
    deactivated.

    The app contains three additional windows:
    * adding record to specify new record's information
    * watch records received from a server
    * watch error has been occured
    """
    def __init__(self, host='localhost', port=9000):
        super(Client, self).__init__()
        self.host = host
        self.port = port
        self.records_requested_flag = False

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
        """
        Window for adding new record
        After form filled and Save button pushed a thread with new connection
        will be created to send data on the server. Server will close this
        connection then the data received
        The cancel button just destroys the window without any changes
        """
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
        """ The entry point """
        self.root.mainloop()

    def process_records(self):
        """
        The main work infinte loop for generation and receiving records
        These functions performed by transfering short messages to and from
        the server
        To control current state the variable records_requested_flag is used
        Then it's value becomes True get request will be sent to server
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            self.log('Error creating socket', e)

        try:
            sock.connect((self.host, self.port))
        except socket.gaierror, e:
            self.log('Address-related error connecting to server', e)
        except socket.error, e:
            self.log('Connection error', e)

        try:
            sock.sendall('gen')
        except socket.error, e:
            self.log('Error sending data', e)

        state = ''
        while True:
            try:
                data = tuple(sock.recv(1024).split('~'))
            except socket.error, e:
                self.log('Error receiving data', e)
            print data
            if not data[0]:
                break
            elif data[0] == 'state':
                state = data[1]
                if state == 'SUCCESS':
                    self.get_btn['state'] = 'active'
                    self.gen_btn['state'] = 'active'
                    self.gen_btn['text'] = (
                        u'Сгенерировать список записей (Готово)')
                    try:
                        sock.sendall('ok')
                    except socket.error, e:
                        self.log('Error sending data', e)
                elif state != 'SUCCESS':
                    self.gen_btn['text'] = (
                        u'Сгенерировать список записей (Запрос обрабатывается)')
                    print 'sending state request'
                    try:
                        sock.sendall('state?')
                    except socket.error, e:
                        self.log('Error sending data', e)
            elif state != 'SUCCESS':
                print 'sending state request'
                try:
                    sock.sendall('state?')
                except socket.error, e:
                    self.log('Error sending data', e)
            elif self.records_requested_flag:
                print 'sending get signal'
                try:
                    sock.sendall('get')
                except socket.error, e:
                    self.log('Error sending data', e)
                self.records_requested_flag = False
            elif data[0] == 'rec':
                try:
                    sock.send('go')
                except socket.error, e:
                    self.log('Error sending data', e)
                try:
                    data = sock.recv(1024)
                except socket.error, e:
                    self.log('Error receiving data', e)
                records = ''
                while data:
                    records += data
                    try:
                        data = sock.recv(1024)
                    except socket.error, e:
                        self.log('Error receiving data', e)
                else:
                    records = records.strip().split('\n')
                    print records
                    print 'Bye, {}:{}'.format(self.host, self.port)
                    break
            else:
                try:
                    sock.sendall('ok')
                except socket.error, e:
                    self.log('Error sending data', e)
        sock.close()
        if records:
            self.show_records(records)

    def show_records(self, records):
        """ Shows records from list on new window """
        records_window = Tkinter.Toplevel()
        text_box = Tkinter.Text(records_window, wrap='word')
        scrollbar = Tkinter.Scrollbar(records_window)

        scrollbar['command'] = text_box.yview
        text_box['yscrollcommand'] = scrollbar.set

        text_box.pack(side='left')
        scrollbar.pack(side='right')
        for record in records:
            text_box.insert('end', '{}\n'.format(record))
        text_box['state'] = 'disabled'
        self.gen_btn['text'] = u'Сгенерировать список записей'

    def request_records(self, event):
        """ Starts new thread for records transfering and controls buttons """
        if self.gen_btn['state'] == 'active':
            thread.start_new_thread(self.process_records, tuple())
            self.gen_btn['state'] = 'disabled'

    def receive_records(self, event):
        """ Changes the flag to sent request for records list """
        if self.get_btn['state'] == 'active':
            self.records_requested_flag = True
            self.get_btn['state'] = 'disabled'

    def send_data(self):
        """ Creates short connection to send new record on server """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            self.log('Error creating socket', e)

        try:
            sock.connect((self.host, self.port))
        except socket.gaierror, e:
            self.log('Address-related error connecting to server', e)
        except socket.error, e:
            self.log('Connection error', e)

        connector = '~'
        message = connector.join([field.get() for field in
            [self.lastname, self.firstname, self.middlename, self.birth_date]])

        try:
            sock.sendall('add{}{}'.format(connector, message))
        except socket.error, e:
            self.log('Error sending data', e)
        
        sock.close()
        self.form.destroy()

    def log(self, desc, e):
        """ If an exception catched adds information into log file and resets gui"""
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = '{} -- {}, {}'.format(time, desc, e)
        with open('log.txt', 'a') as log:
            log.write('{}\n'.format(message))
        self.reset_gui()
        self.show_error(message)
        sys.exit(1)

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

    def load_logs(self, event):
        """ Clears text box in log window and fills it with all logs """
        self.text_box['state'] = 'normal'
        self.text_box.delete('1.0', END)
        with open('log.txt', 'r') as log:
            for record in log:
                self.text_box.insert('end', record)
        self.text_box['state'] = 'disabled'

    def reset_gui(self):
        """ Set main menu buttons into default state """
        self.gen_btn['text'] = u'Сгенерировать список записей'
        self.get_btn['state'] = 'disabled'
        self.gen_btn['state'] = 'active'

if __name__ == '__main__':
    client = Client()
    client.run()
