import socket
import thread
from time import sleep
from database_handler import DatabaseHandler
from tasks import add_person, generate_records
import os
import sys


class Server(object):
    """
    Server is independent class working in infinite cycle.
    It uses the DatabaseHandler to operate sqlite3 database.
    Host and port parameters may be defined during initializing the instance.
    Default values for host and port are 'localhost' and 9000 respectively.
    """
    def __init__(self, host='localhost', port=9000):
        super(Server, self).__init__()
        self.host = host
        self.port = port
        self.dh = DatabaseHandler()

    def process_connection(self, conn, addr):
        """
        The main working loop.
        It works synchronized with an Client instance by transfering short
        messages.
        The both instances send messages to each other every 1 second.
        If the message consists of several words the words divided by a '~' char.
        The first word of the message is a command.
        If message contains new record then it starts with 'add' command
        This command executes in short way without infinite loop

        'gen' command starts records file generation task with celery.
        If the task started the client sends request for task status
        The server responses to these requests. If the task status becomes
        'SUCCESS' the client stops requesting task status.

        'get' command starts sending the file cycle
        During this phase, the servet notifies the client about sending
        After server has got response from the client it sends all records
        from the records file to the client. After this connection will close.

        After closing the connection the records file will be removed
        """
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
        """
        Remove outdated records text files if they exist
        These files produced by previous runs and not deleted during error
        occured
        """
        files = os.listdir(os.getcwd())
        for file in files:
            if 'records-' in file and '.txt' in file:
                os.remove(os.path.join(os.getcwd(), file))

    def run(self):
        """
        The entry point to start work
        The ifinite loop producing new thread in case of connection accepted
        """
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
