import socket
import thread
from database_handler import DatabaseHandler
from tasks import add_person, generate_records


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
        if self.data[0] == 'add':
            add_person.delay(self.data[1:])
        elif self.data[0] == 'gen':
            print 'Put generate records task to query'
            records = generate_records.delay(addr)
        elif self.data[0] == 'get':
            # self.return_records()
            print 'Return records'
        else:
            print "Wrong command"

        print 'Received: {}'.format(self.data)
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
