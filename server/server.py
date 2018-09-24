import socket
import thread
from time import sleep
from database_handler import DatabaseHandler
from tasks import add_person, generate_records
import os


class Server(object):
    """docstring for Server."""
    def __init__(self, host='127.0.0.1', port=9000):
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
                print self.data[0]
                if not self.data[0]:
                    print 'close connection'
                    break
                elif self.data[0] == 'state?':
                    if records:
                        state = records.state
                    else:
                        state = 'Not started'
                    print 'sending state'
                    conn.sendall('~'.join(['state', state]))
                elif self.data[0] == 'gen':
                    if not os.path.isfile(
                        'records-{}-{}'.format(addr[0], addr[1])):
                        print 'Put generate records task to query'
                        conn.sendall('ok')
                        records = generate_records.delay(addr)
                        print records.ready()
                        print records.state
                    else:
                        conn.sendall('ok')
                        print 'Already generated'
                elif self.data[0] == 'get':
                    if os.path.isfile('records-{}-{}.txt'.format(addr[0], addr[1])):
                        # self.return_records()
                        conn.sendall('begin')
                        with open(
                            'records-{}-{}.txt'.format(addr[0], addr[1]), 'r'
                        ) as records_file:
                            for line in records_file.readlines():
                                conn.send(line.strip())
                                response = conn.recv(1024)
                            conn.send('end')
                    else:
                        print 'The records are not generated yet'
                        print 'records-{}-{}.txt'.format(addr[0], addr[1])
                        conn.sendall('ok')
                else:
                    conn.sendall('ok')
                sleep(1)
                self.data = tuple(conn.recv(1024).split('~'))
                # print 'Received: {}'.format(self.data)
        conn.close()

    def run(self):
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
