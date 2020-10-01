'''
Server code for setting up a WebSocket server, handling connections, and verifying
connection details.

This code borrows from an earlier project with the CISS ROV Robotics Team,
but still my code


Required 3rd-party libraries:
`autobahn`
`twisted`
'''
import sys
import json
from typing import Callable, Dict, Optional
import re

from twisted.python import log, logfile # type: ignore
from twisted.internet import reactor, ssl # type: ignore

from .factoryAndProtocol import ServerFactory, ServerProtocol
from ..requestProcessor import interactions


data = None
try:
    f = open('config.json')
    data = f.read()
    f.close()
except FileNotFoundError as e:
    print('Could not find config file:', e)
    raise

config = json.loads(data)

USE_SSL: bool = config['USE_SSL']
assert isinstance(USE_SSL, bool)


class Server:

    def __init__(self, ip: str, port: int, callbackFunc: Callable[[interactions.UnprocessedClientRequest], interactions.Response]):
        '''
        A class for managing the code for running the server.
        To setup the server, run `s = Server()`,
        and then run `s.run()` to start it.

        Requires keyword argument `callbackFunc` which should
        be of type `Callable[[str, dict], str]`. This is
        for handling incoming messages and should return
        a status update to all clients. The return type
        should be type `str` and be json. The
        arguments are a unique id for each player as a `str`
        and the message from that player as a `dict`
        '''

        regex = r'([0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3})|localhost'

        if re.fullmatch(regex, ip) is None:
            raise ValueError(f'Invalid ip: {ip}')

        self.ip: str = ip
        self.port: int = port

        self.__givenCallback: Callable[[interactions.UnprocessedClientRequest], interactions.Response] = callbackFunc

        self.logFile = open('gameMsgLog.log', 'w')

        protocol = 'ws'

        self.contextFactory: Optional[ssl.DefaultOpenSSLContextFactory] = None
        if USE_SSL:
            protocol = 'wss'
            key = config['key']
            cert = config['cert']
            assert isinstance(key, str)
            assert isinstance(cert, str)
            self.contextFactory = ssl.DefaultOpenSSLContextFactory(key, cert)

        # Setup server factory
        self.server = ServerFactory(
            u'{}://{}:{}'.format(protocol, ip, port), 
            self.logFile, 
            serverCallback=self.callback
            )

        self.server.protocol = ServerProtocol

        print(f'WebSocket server on {self.ip}:{self.port}')

        if USE_SSL:
            reactor.listenSSL(self.port, self.server, self.contextFactory) # pylint: disable=no-member
        else:
            # setup listening server
            reactor.listenTCP(self.port, self.server) # pylint: disable=no-member

    def callback(self, re: interactions.UnprocessedClientRequest) -> interactions.Response:
        '''
        Handles messages from players
        '''
        return self.__givenCallback(re)
        

    def run(self):
        '''
        Run the server. This method will not return
        until the server is ended by an Exception like ^C.

        init_msgs are for messages that should be send to the player
        immediately, like the game map for example.
        '''

        try:
            # start listening for and handling connections
            # task.deferLater(reactor, 1, lambda: [self.server.broadcastToAll(msg) for msg in init_msgs])
            reactor.run() # pylint: disable=no-member
        except KeyboardInterrupt:
            print('KeyboardInterrupt')
        finally:
            self.logFile.close()
            # if logs are sent to a file instead of stdout
            # the file should be closed here with f.close()

def main():
    log.startLogging(sys.stdout, setStdout=True)

    logFile = logfile.LogFile.fromFullPath('twistedLog.log')
    log.addObserver(log.FileLogObserver(logFile).emit)

    s = Server()
    s.run()
