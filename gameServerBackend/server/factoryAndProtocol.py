from __future__ import annotations
from gameServerBackend.requestProcessor.interactions import Response
from ..requestProcessor import interactions
from .tokenStorage import TokenStorage

import json
from typing import Callable, Dict, List, Optional, Union

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory # type: ignore
from autobahn.websocket.protocol import ConnectingRequest # type: ignore
from twisted.python import log # type: ignore


class _ServerProtocol(WebSocketServerProtocol):
    '''
    Sending a message of 'Hi' returns two messages, 'Hello' and a json
    that is {'token': token}
    '''

    factory: _ServerFactory

    @property
    def token(self) -> Optional[str]:
        '''
        Returns the token if it exists. A token is generated once
        the websocket enters the open state.
        '''
        try:
            return self.__token
        except AttributeError:
            return None
    
    @property
    def isOpen(self) -> bool:
        try:
            return self.__isOpen
        except AttributeError:
            return False

    def onConnect(self, request: ConnectingRequest):

        log.msg(request.path)
        # print(request.headers)
        # print(request.protocols)

        # debug information
        log.msg('Client connecting: {0}'.format(request.peer))
        self.clientTypeRequest = request.path

    def onOpen(self):
        if not hasattr(self, 'clientTypeRequest'):
            raise RuntimeError("Connected without setting clientTypeRequest, this should never happen")
        clientTypeRequest: str = getattr(self, 'clientTypeRequest')

        # process the type of request
        if clientTypeRequest.startswith('/'):
            # remove the slash if there is one
            clientTypeRequest = clientTypeRequest[1:]

        # tell the factory to remember the connection
        self.__token = self.factory.register(self, clientTypeRequest)

        log.msg('WebSocket connection open')
        self.__isOpen = True

    def onClose(self, wasClean, code, reason):
        log.msg('WebSocket connection closed: {0}'.format(reason))
        self.__isOpen = False

        # tell the factory that this connection is dead
        self.factory.deregister(self)

    def onMessage(self, msg, isBinary):
        msg = msg.decode()

        if msg.lower() == 'hi':
            self.sendMessage(b"hello world")

            msg = json.dumps({'token': self.factory.getToken(self)})
            self.sendMessage(msg)

        elif msg == 'history':
            self.factory.sendHistory(self)

        else:
            self.factory.onMessage(msg, self)
    
    def sendMessage(self, payload: Union[str, bytes], isBinary=False, fragmentSize=None, sync=False, doNotCompress=False):
        if isinstance(payload, str):
            payload = payload.encode()
        return super().sendMessage(payload, isBinary=isBinary, fragmentSize=fragmentSize, sync=sync, doNotCompress=doNotCompress)


class _ServerFactory(WebSocketServerFactory):
    '''
    Keeps track of all connections and relays data to other clients
    '''

    def __init__(self, url: str, f, serverCallback: Callable[[interactions.UnprocessedClientRequest], interactions.Response], tokenDataStorage: TokenStorage):
        '''
        Initializes the class
        Args:
            url (str): has to be in the format of "ws://127.0.0.1:8008"
            f (file): a writable file for logging
        
        The playerManager should be shared with the GameManager
        '''

        self.file = f

        # self.history = [g.getAsJson()]

        self.serverCallback = serverCallback

        self.__tokenDataStorage: TokenStorage = tokenDataStorage
        self.__connection: Dict[str, _ServerProtocol] = {}

        WebSocketServerFactory.__init__(self, url)
    
    def updateAll(self):
        '''
        Sends the current game state to all players
        '''
        self.broadcastToAll(self.g.getAsJson())
    
    def getToken(self, client: _ServerProtocol) -> str:
        t = client.token
        if t is None:
            raise RuntimeError('client has not yet registered. This error should not occur ever')

        return t
    
    # def sendHistory(self, client):
    #     for msg in self.history:
    #         client.sendMessage(msg.encode())
    #     client.sendMessage(self.g.getAsJson()) # latest state of the board
    
    def onMessage(self, msg: str, client: _ServerProtocol):
        playerID: Optional[str] = self.getToken(client)
        if playerID is None:
            raise RuntimeError('client not in token database. This error should not occur ever')

        request = interactions.UnprocessedClientRequest(playerID=playerID, request=msg)
        self.__handleResponse(self.serverCallback(request))

    def register(self, client: _ServerProtocol, clientTypeRequest: str) -> Optional[str]:
        '''
        Called by any new connecting client to address
        whether they are a new player or a reconnecting one.

        The request line should be 
            /gameID/name/token/...     <- reconnect
            /gameID/name/null/...      <- first connect
        
        but the first / is removed by onConnect
        '''
        token: Optional[str] = None
        name: Optional[str] = None
        gameID: Optional[str] = None
        other: Optional[str] = None

        if len(clientTypeRequest.strip()) == 0:
            log.msg('name missing')
            #client.sendHttpErrorResponse(404, 'Name missing')
            client.sendClose(code=4000, reason='Name missing')
            #client.sendClose()
            return None

        
        tmp: str = clientTypeRequest.strip()
        tmpLs = tmp.split('/')
        del tmp

        l = len(tmpLs)
        if l < 3:
            log.msg('incomplete data')
            client.sendClose(code=4000, reason='Data missing')
            return None
        else:
            gameID = tmpLs[0]
            name = tmpLs[1]
            token = tmpLs[2]

            if token.lower().strip() in ('null', 'none', 'nil'):
                token = None

            if l > 3:
                other = '/'.join(tmpLs[3:])
        

        if name is None or gameID is None:
            raise RuntimeError("Something went wrong in register")

        if token is None:
            token = self.__tokenDataStorage.addPlayerID(playerID=name)

        request = interactions.JoinGameClientRequest(playerID=name, gameId=gameID, otherData=other)
        
        response = self.serverCallback(request)
        self.__handleResponse(response)

        self.__connection[token] = client

        return token
    
    def __handleResponse(self, res: Response):
        if isinstance(res, interactions.ResponseSuccess):
            if res.dataToAll:
                self.broadcastToAll(res.dataToAll)
            if res.dataToSender:
                self.broadcastToPlayer(res.dataToSender, res.sender.getPlayerName)
            if res.dataToSome:
                for player, msg in res.dataToSome.items():
                    self.broadcastToPlayer(msg, playerID=player.getPlayerName)
        
        elif isinstance(res, interactions.ResponseFailure):
            log.msg(f"Error: ResponseFailure: {res.errorMsg}")
            errMsg = json.dumps({'ResponseFailure': res.errorMsg})
            self.broadcastToPlayer(errMsg, res.sender.getPlayerName)

    def deregister(self, client: _ServerProtocol):
        token = client.token
        if token is None:
            log.msg("Player disconnected before assigned token:", token)
        elif token in self.__connection:
            self.__connection.pop(token)
            log.msg("Disconnected player:", token)
        else:
            log.msg("Disconnected player, but token not found?:", token)

    def broadcastToAll(self, msg: str): # sourceConnection: ServerProtocol
        '''
        Sends a message of type `str` to all currently connected
        players
        '''
        self.file.write(msg + '\n')
        self.file.flush()

        encoded = msg.encode()

        for token, connection in self.__connection.items():
            connection.sendMessage(encoded)
    
    def broadcastToSome(self, msg: str, tokenList: List[str]):
        '''
        Sends a message of type `str` to all currently connected
        players whose token is found in the list.
        '''
        
        encoded = msg.encode()
        
        for token in tokenList:
            self.__connection[token].sendMessage(msg)
    
    def broadcastToPlayer(self, msg: str, playerID: str):
        '''
        Sends a message of type `str` to the player
        '''
        token = self.__tokenDataStorage.getTokenbyPlayerID(playerID=playerID)
        if token is None:
            raise RuntimeError('playerID not found')

        self.__connection[token].sendMessage(msg)
