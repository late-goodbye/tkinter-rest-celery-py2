import SocketServer
from database_handler import DatabaseHandler
from tasks import add_person, generate_records
import os
import sys
from time import ctime
from shutil import rmtree
import hashlib


class CustomTCPHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        self.data = tuple(self.rfile.readline().strip().split('~'))

        if self.data[0] == 'add':
            self.wfile.write(1 if self.handle_add() else 0)
        elif self.data[0] == 'gen':
            filename = self.handle_gen()
            self.wfile.write(filename)
        elif self.data[0] == 'get':
            try:
                self.handle_get(self.data[1])
            except IndexError:
                print 'No filename in get request'
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
            filepath = os.path.join(
                os.path.join(os.getcwd(), 'records'), filename)
            generate_records(filepath)
            return filename
        except Exception as e:
            raise e
        else:
            return '0'

    def handle_get(self, filename):
        pass

    def handle_unknown(self):
        pass

def clear_directory():
    """
    Remove outdated records text files if they exist
    These files produced by previous runs and not deleted during error
    occured
    """
    records_directory = os.path.join(os.getcwd(), 'records')
    if os.path.isdir(records_directory):
        rmtree(records_directory)
        print 'Records cleared'
    os.mkdir(records_directory)


if __name__ == '__main__':
    clear_directory()

    host, port = 'localhost', 9000
    server = SocketServer.TCPServer((host, port), CustomTCPHandler)
    server.serve_forever()
    server.allow_reuse_address = True
