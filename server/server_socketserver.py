import SocketServer
from database_handler import DatabaseHandler
from tasks import add_person, generate_records
import os
import sys
from time import ctime
import hashlib


class CustomTCPHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        self.data = tuple(self.rfile.readline().strip().split('~'))

        if self.data[0] == 'add':
            self.wfile.write(1 if self.handle_add() else 0)
        elif self.data[0] == 'gen':
            self.wfile.write(self.handle_gen())
        elif self.data[0] == 'get':
            self.handle_get()
        else:
            self.handle_unknown()

    def handle_add(self):
        try:
            return add_person.delay(self.data[1:])
        except Exception as e:
            raise 'Error add record to database: {}'.format(e)
        else:
            return False

    def handle_gen(self):
        h = hashlib.md5()
        h.update(ctime())
        h.update(''.join(str(self.request.getpeername())))
        filename = h.hexdigest()
        print filename
        try:
            # generate_records(filename = 'dsfdsd')
        except Exception as e:
            raise e
        else:
            return '0'

    def handle_get(self):
        pass

    def handle_unknown(self):
        pass


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def clear_directory():
    """
    Remove outdated records text files if they exist
    These files produced by previous runs and not deleted during error
    occured
    """
    files = os.listdir(os.getcwd())
    for file in files:
        if 'records-' in file and '.txt' in file:
            os.remove(os.path.join(os.getcwd(), file))


if __name__ == '__main__':
    clear_directory()

    host, port = 'localhost', 9000
    server = ThreadedTCPServer((host, port), CustomTCPHandler)
    server.serve_forever()
    server.allow_reuse_address = True
