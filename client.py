from contextlib import closing
import json
import re
import socket
import sys

import game

BUFSIZE = 1024
TIMEOUT = 10

class Communicator():
    def __init__(self, host, port, punter):
        self.host = host
        self.port = port
        self.punter = punter
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[DEBUG] set socket timeout {} -> {} sec'.format(self.sock.gettimeout(), TIMEOUT))
        self.sock.settimeout(TIMEOUT)
        print('[INFO] communicator init:', self.host, self.port, self.punter.get_name(), self.sock)

    def send_wrap(self, x):
        body = json.dumps(x)
        length = len(body)
        sent = '{:d}:{}'.format(length, body)
        self.sock.send(sent.encode())

    def start(self):
        print('[INFO] communicator start')
        with closing(self.sock):
            print('[INFO] connect socket')
            self.sock.connect((self.host, self.port))
            print('[INFO] send hanshake')
            self.send_wrap({'me': self.punter.get_name()})
            is_reading_size = True
            is_finished = False
            buf = ''
            while not is_finished:
                print('[DEBUG] recv, is_reading_size: {}, buf: "{}"'.format(is_reading_size, buf))
                if is_reading_size:
                    m = re.match('(\d+):', buf)
                    if m:
                        size = int(m.group(1))
                        print('[DEBUG] buf truncate, "{}" -> "{}"'.format(buf, buf[m.end() :]))
                        buf = buf[m.end() :]
                        is_reading_size = False
                    else:
                        buf += self.sock.recv(BUFSIZE).decode('ascii')
                elif len(buf) >= size:
                    msg = json.loads(buf[: size])
                    is_finished = self.respond(msg)
                    print('[DEBUG] buf truncate, "{}" -> "{}"'.format(buf, buf[size :]))
                    buf = buf[size :]
                    is_reading_size = True
                else:
                    buf += self.sock.recv(BUFSIZE).decode('ascii')

    def respond(self, msg):
        print('respond to:', msg)
        if 'you' in msg:
            print('[INFO] reponse: handshake')
            return False
        elif 'map' in msg:
            print('[INFO] reponse: setup')
            self.punter.exec_setup(msg)
            self.send_wrap({'ready': self.punter.punter_id})
            return False
        elif 'move' in msg:
            print('[INFO] reponse: gameplay')
            prev_moves = msg['move']['moves']
            my_move = self.punter.get_move(prev_moves)
            self.send_wrap(my_move)
            return False
        elif 'stop' in msg:
            print('[INFO] reponse: scoring')
            print('[INFO] result:', msg)
            return True
        else:
            assert(False)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python {} <port>'.format(sys.argv[0]))
        sys.exit(0)
    port = int(sys.argv[1])
    punter = game.EagerPunter()
    comm = Communicator('punter.inf.ed.ac.uk', port, punter)
    comm.start()
