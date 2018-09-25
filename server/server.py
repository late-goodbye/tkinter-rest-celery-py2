import socket
import thread
from time import sleep
from database_handler import DatabaseHandler
from tasks import add_person, generate_records
import os
import sys


class Server(object):
    """docstring for Server."""
    def __init__(self, host='localhost', port=9000):
        super(Server, self).__init__()
        self.host = host
        self.port = port
        self.dh = DatabaseHandler()

    def process_connection(self, conn, addr):
        print 'Process {} started'.format(thread.get_ident())
        print 'Connected by {}'.format(addr)
        self.data = tuple(conn.recv(1024).split('~'))
        state = ''
        if self.data[0] == 'add':
            add_person.delay(self.data[1:])
            print 'Received: {}'.format(self.data)
        else:
            while True:
                print self.data
                if not self.data[0]:
                    break
                elif self.data[0] == 'state?':
                    if task:
                        state = task.state
                    else:
                        state = 'Not started'
                    conn.sendall('~'.join(['state', state]))
                elif self.data[0] == 'gen':
                    print 'Put generate records task to query'
                    conn.sendall('ok')
                    task = generate_records.delay(addr)
                    print task.ready()
                    print task.state
                elif self.data[0] == 'get':
                    if os.path.isfile(os.path.join(
                        os.getcwd(),
                        'records-{}-{}.txt'.format(addr[0], addr[1]))):
                        conn.send('rec')
                        response = conn.recv(10)
                        if response == 'go':
                            with open(
                                'records-{}-{}.txt'.format(addr[0], addr[1]), 'r'
                            ) as records_file:
                                for line in records_file:
                                    conn.send(line)
                                break
                    else:
                        print 'The records are not generated yet'
                        print 'records-{}-{}.txt'.format(addr[0], addr[1])
                        conn.sendall('ok')
                else:
                    conn.sendall('ok')
                sleep(1)
                self.data = tuple(conn.recv(1024).split('~'))
        os.remove('records-{}-{}.txt'.format(addr[0], addr[1]))
        print 'Bye, {}:{}'.format(addr[0], addr[1])
        conn.close()

    def clear_directory(self):
        files = os.listdir(os.getcwd())
        for file in files:
            if 'records-' in file and '.txt' in file:
                os.remove(os.path.join(os.getcwd(), file))

    def run(self):
        self.clear_directory()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        while True:
            conn, addr = sock.accept()
            thread.start_new_thread(self.process_connection, (conn, addr))
        sock.close()


if __name__ == '__main__':
    server = Server()
    server.run()
