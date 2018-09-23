from celery import Celery
import sqlite3
import socket


class Server(object):
    """docstring for Server."""
    def __init__(self, host='127.0.0.1', port=9000):
        super(Server, self).__init__()
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        conn, addr = sock.accept()
        print 'Connected by {}'.format(addr)
        self.data = tuple(conn.recv(1024).split('~'))
        sock.close()

        print 'Received: {}'.format(self.data)


app = Celery('tasks', backend='amqp', broker='amqp://')

@app.task
def print_hello():
    print 'Hello there'


if __name__ == '__main__':
    server = Server()
    server.run()
