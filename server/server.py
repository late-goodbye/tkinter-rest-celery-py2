from celery import Celery
import socket
from database_handler import DatabaseHandler



class Server(object):
    """docstring for Server."""
    def __init__(self, host='127.0.0.1', port=9000):
        super(Server, self).__init__()
        self.host = host
        self.port = port
        self.dh = DatabaseHandler()

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        while True:
            conn, addr = sock.accept()
            print 'Connected by {}'.format(addr)
            self.data = tuple(conn.recv(1024).split('~'))
            if self.data[0] == 'add':
                print 'Add person'
                # self.dh.add_person(self.data[1:])
            elif self.data[0] == 'gen':
                print 'Generate records'
                # self.records = self.dh.generate_records()
            elif self.data[0] == 'get':
                # self.return_records()
                print 'Return records'
            else:
                print "Wrong command"

            print 'Received: {}'.format(self.data)
        sock.close()


app = Celery('tasks', backend='amqp', broker='amqp://')

@app.task
def print_hello():
    print 'Hello there'


if __name__ == '__main__':
    server = Server()
    server.run()
