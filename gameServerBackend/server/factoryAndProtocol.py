from __future__ import annotations
from gameServerBackend.requestProcessor.interactions import Response
from gameServerBackend.requestProcessor.dataTypes import PlayerManager
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
        # print(request.headers)
        # print(request.protocols)

        # debug information
        log.msg(f'Client connecting: "{request.peer}" with path "{request.path}"')
        self.clientTypeRequest = request.path

        self.__isOpen = False

    def onOpen(self):
        if not hasattr(self, 'clientTypeRequest'):
            raise RuntimeError("Connected without setting clientTypeRequest, this should never happen")
        clientTypeRequest: str = getattr(self, 'clientTypeRequest')

        self.__isOpen = True

        # process the type of request
        if clientTypeRequest.startswith('/'):
            # remove the slash if there is one
            clientTypeRequest = clientTypeRequest[1:]

        # tell the factory to remember the connection
        self.__token = self.factory.register(self, clientTypeRequest)

        if self.__token is None:
            log.msg('WebSocket connection rejected in register')
        else:
            log.msg('WebSocket connection open')
            

            self.sendMessage(json.dumps({'token': self.__token}))
        
        

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
        if not self.isOpen:
            log.msg('Attempting to send to closed connection! ' + str(payload))
            return
        if isinstance(payload, str):
            payload = payload.encode()
        return super().sendMessage(payload, isBinary=isBinary, fragmentSize=fragmentSize, sync=sync, doNotCompress=doNotCompress)


class _ServerFactory(WebSocketServerFactory):
    '''
    Keeps track of all connections and relays data to other clients
    '''

    def __init__(self, url: str, f, serverCallback: Callable[[interactions.UnprocessedClientRequest], interactions.Response], tokenDataStorage: TokenStorage, playerDB: PlayerManager, verbose: bool = False):
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

        self.__backlog: Dict[str, List[str]] = {}

        self.__playerDB: PlayerManager = playerDB

        self.__verbose: bool = verbose

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
        token: Optional[str] = self.getToken(client)
        if token is None:
            raise RuntimeError('No token assigned to player?')

        playerID = self.__tokenDataStorage.getPlayerIDbyToken(token)
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
            #log.msg('name missing')
            #client.sendHttpErrorResponse(404, 'Name missing')
            client.sendClose(code=4000, reason='Name missing') # send close reason is logged
            #client.sendClose()
            return None

        
        tmp: str = clientTypeRequest.strip()
        tmpLs = tmp.split('/')
        del tmp

        l = len(tmpLs)
        if l < 3:
            #log.msg('incomplete data')
            client.sendClose(code=4000, reason='Login data incomplete')
            return None
        else:
            gameID = tmpLs[0]
            name = tmpLs[1]
            token = tmpLs[2]

            if len(name) == 0:
                client.sendClose(code=4000, reason='Name missing')
                return None

            if token.lower().strip() in ('null', 'none', 'nil'):
                token = None

            if l > 3:
                other = '/'.join(tmpLs[3:])
        

        if name is None or gameID is None:
            raise RuntimeError("Something went wrong in register")
        
        if token is None:
            tmp2: Optional[str] = self.__tokenDataStorage.getTokenbyPlayerID(name)
            if tmp2 is not None:
                client.sendClose(code=4000, reason='Name taken')
                return None
        else:
            result = self.__tokenDataStorage.getPlayerIDbyToken(token)
            if result is None:
                client.sendClose(code=4000, reason='Token unknown')
                return None
            if result != name:
                client.sendClose(code=4000, reason='Name taken')
                return None
            name = result

        preJoinGameID: Optional[str]
        playerData = self.__playerDB.getPlayer(name)
        if playerData is not None and playerData.getGameID() == gameID:
            preJoinGameID = playerData.getGameID()
        else:
            preJoinGameID = None
        
        if self.__verbose: log.msg('building JoinGameClientRequest')

        request = interactions.JoinGameClientRequest(playerID=name, gameId=gameID, otherData=other)

        response = self.serverCallback(request)

        if response.isValid:
            if self.__verbose: log.msg('got a successful response')
            if token is None:
                token = self.__tokenDataStorage.addPlayerID(playerID=name)
            self.__connection[token] = client # __handleResponse depends on __connection

            if preJoinGameID is not None and preJoinGameID == gameID:
                # same game, send backLog
                log.msg(f"Reconnecting: {token}: {name}")
                if token and token in self.__backlog:
                    for msg in self.__backlog[token]:
                        self.broadcastToPlayer(msg, playerID=name)
                    #self.__backlog[token].clear() this happens next line anyway

            self.__backlog[token] = []
            if self.__verbose: log.msg('send response')
            self.__handleResponse(response)
        else:
            if self.__verbose: log.msg('got a failed response')
            client.sendClose(code=4000, reason=json.dumps({'ResponseFailure': response.errorMsg}))
            return None

        return token

    def __handleResponse(self, res: Response):
        if isinstance(res, interactions.ResponseSuccess):
            if res.dataToAll:
                players, data = res.dataToAll

                def requireHelper(x: Optional[str]) -> str:
                    if x is not None:
                        return x
                    raise RuntimeError('player id not found. This shouldnt happen')

                tokens = [requireHelper(self.__tokenDataStorage.getTokenbyPlayerID(p.getPlayerName())) for p in players]
                self.broadcastToSome(data, tokens)
            if res.dataToSender:
                self.broadcastToPlayer(res.dataToSender, res.sender.getPlayerName())
            if res.dataToSome:
                for player, msg in res.dataToSome.items():
                    self.broadcastToPlayer(msg, playerID=player.getPlayerName())

        elif isinstance(res, interactions.ResponseFailure):
            log.msg(f"Error: ResponseFailure: {res.errorMsg}")
            errMsg = json.dumps({'ResponseFailure': res.errorMsg})
            self.broadcastToPlayer(errMsg, res.sender.getPlayerName())

    def deregister(self, client: _ServerProtocol):
        token = client.token
        if token is None:
            log.msg("Player disconnected before assigned token:", token)
        elif token in self.__connection:
            self.__connection.pop(token)
            log.msg("Disconnected player:", token)
        else:
            log.msg("Disconnected player, but token not found?:", token)

    # def broadcastToAll(self, msg: str): # sourceConnection: ServerProtocol
    #     '''
    #     Sends a message of type `str` to all currently connected
    #     players.
    #     Due to supporting multiple games, this has no use
    #     '''
    #     self.file.write(msg + '\n')
    #     self.file.flush()

    #     encoded = msg.encode()

    #     for token, connection in self.__connection.items():
    #         connection.sendMessage(encoded)
    
    def broadcastToSome(self, msg: str, tokenList: List[str]):
        '''
        Sends a message of type `str` to all currently connected
        players whose token is found in the list.
        '''
        
        encoded = msg.encode()
        
        for token in tokenList:
            if token not in self.__connection:
                self.__backlog[token].append(msg)
            else:
                self.__connection[token].sendMessage(encoded)
    
    def broadcastToPlayer(self, msg: str, playerID: str):
        '''
        Sends a message of type `str` to the player
        '''
        token = self.__tokenDataStorage.getTokenbyPlayerID(playerID=playerID)
        if token is None:
            raise RuntimeError('playerID not found')
        
        if token not in self.__connection:
            self.__backlog[token].append(msg)
        else:
            self.__connection[token].sendMessage(msg)
