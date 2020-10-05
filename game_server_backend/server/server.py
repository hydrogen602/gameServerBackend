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

from .factoryAndProtocol import _ServerFactory, _ServerProtocol
from .tokenStorage import TokenStorage, BasicTokenStorage
from ..requestProcessor import interactions, RequestProcessor

class Server:

    def __init__(self, ip: str, port: int, 
            requestProcessor: RequestProcessor,
            playerTokenStorage: TokenStorage = BasicTokenStorage(),
            config: Optional[Dict[str, object]] = None
            ):
        '''
        A class for managing the code for running the server.
        To setup the server, run `s = Server()`,
        and then run `s.run()` to start it.

        Requires keyword argument `callbackFunc` which should
        be of type `Callable[[interactions.UnprocessedClientRequest],
        interactions.Response]`. This is
        for handling incoming messages and should return
        a status update to clients.

        Config options are:
        USE_SSL: bool
        verbose: bool
        key: str
        cert: str


        key & cert are only needed if USE_SSL==True
        '''

        if config is None:
            config = self.__getConfig()


        tmp = config['USE_SSL']
        assert isinstance(tmp, bool)
        USE_SSL: bool = tmp

        verbose: bool
        if 'verbose' in config:
            tmp = config['verbose']
            assert isinstance(tmp, bool)
            verbose = tmp
        else:
            verbose = False
        

        regex = r'([0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3})|localhost'

        if re.fullmatch(regex, ip) is None:
            raise ValueError(f'Invalid ip: {ip}')

        self.ip: str = ip
        self.port: int = port

        self.__requestProcessor: RequestProcessor = requestProcessor

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
        self.server = _ServerFactory(
            u'{}://{}:{}'.format(protocol, ip, port), 
            self.logFile, 
            serverCallback=self.callback,
            tokenDataStorage=playerTokenStorage,
            playerDB=self.__requestProcessor.playerDatabase,
            verbose=verbose
            )

        self.server.protocol = _ServerProtocol

        print(f'WebSocket server on {self.ip}:{self.port}')

        if USE_SSL:
            reactor.listenSSL(self.port, self.server, self.contextFactory) # pylint: disable=no-member
        else:
            # setup listening server
            reactor.listenTCP(self.port, self.server) # pylint: disable=no-member

    @staticmethod
    def __getConfig() -> Dict[str, object]:
        data = None
        try:
            f = open('config.json')
            data = f.read()
            f.close()
        except FileNotFoundError as e:
            print('Could not find config file: {e}. Either provide a config.json or pass it in')
            raise

        return json.loads(data)

    def callback(self, re: interactions.UnprocessedClientRequest) -> interactions.Response:
        '''
        Handles messages from players
        '''
        return self.__requestProcessor.process(re)
        

    def run(self):
        '''
        Run the server. This method will not return
        until the server is ended by an Exception like ^C.

        init_msgs are for messages that should be send to the player
        immediately, like the game map for example.
        '''
        log.startLogging(sys.stdout, setStdout=True)

        logFile = logfile.LogFile.fromFullPath('twistedLog.log')
        log.addObserver(log.FileLogObserver(logFile).emit)

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
