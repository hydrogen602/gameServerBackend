from __future__ import annotations

from typing import Tuple, List, Optional, Union, Callable, Dict
import json
from urllib.parse import urlparse, parse_qs

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory # type: ignore
from autobahn.websocket.protocol import ConnectingRequest, ConnectionDeny # type: ignore
from twisted.python import log # type: ignore
from twisted.internet import reactor # type: ignore


class ServerProtocol(WebSocketServerProtocol):
    '''
    Sending a message of 'Hi' returns two messages, 'Hello' and a json
    that is {'token': token}

    Sending a message of 'history' returns all previously send messages
    '''

    factory: ServerFactory

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
        self.factory.unregister(self)

    def onMessage(self, msg, isBinary):
        msg = msg.decode()

        if msg.lower() == 'hi':
            self.sendMessage(b"Hello")

            msg = json.dumps({'token': self.factory.getToken(self)})
            self.sendMessage(msg.encode())

        elif msg == 'history':
            self.factory.sendHistory(self)

        else:
            try:
                obj = json.loads(msg)
                if type(obj) == 'str':
                    raise json.decoder.JSONDecodeError

                log.msg("Got json msg:", obj)

                self.factory.onMessage(obj, self)
                #m = Message(mechanics.PlayerManager.instance.getPlayer(self.token), obj, self.factory)

                #self.factory.callbackHandler(m, self)   
            except json.decoder.JSONDecodeError:
                log.msg("Error: Invalid JSON:", msg)
    
    def sendMessage(self, payload: Union[str, bytes], isBinary=False, fragmentSize=None, sync=False, doNotCompress=False):
        if isinstance(payload, str):
            payload = payload.encode()
        return super().sendMessage(payload, isBinary=isBinary, fragmentSize=fragmentSize, sync=sync, doNotCompress=doNotCompress)


class ServerFactory(WebSocketServerFactory):
    '''
    Keeps track of all connections and relays data to other clients
    '''

    def __init__(self, url, f, g: game.Game, serverCallback: Callable[[dict, ServerProtocol], None]):
        '''
        Initializes the class
        Args:
            url (str): has to be in the format of "ws://127.0.0.1:8008"
            f (file): a writable file for logging
        
        The playerManager should be shared with the GameManager
        '''

        self.g: game.Game = g
        self.playerManager: playerCode.PlayerManager = g.playerManager

        self.file = f

        self.history = [g.getAsJson()]

        self.serverCallback = serverCallback

        WebSocketServerFactory.__init__(self, url)
    
    def updateAll(self):
        '''
        Sends the current game state to all players
        '''
        self.broadcastToAll(self.g.getAsJson())
    
    def getToken(self, client: ServerProtocol) -> str:
        t = client.token
        if t is None:
            raise Exception('client has not yet registered. This error should not occur ever')

        return t
    
    def sendHistory(self, client):
        for msg in self.history:
            client.sendMessage(msg.encode())
        client.sendMessage(self.g.getAsJson()) # latest state of the board
    
    def onMessage(self, obj: dict, client: ServerProtocol):
        self.serverCallback(obj, client)

    def register(self, client: ServerProtocol, clientTypeRequest: str) -> Optional[str]:
        '''
        Called by any new connecting client to address
        whether they are a new player or a reconnecting one.

        The request line should be 
            /name/token/color     <- reconnect
            /name/color           <- first connect
        
        but the first / is removed by onConnect

        In the case that the name or color is missing the method will
        return `None` and trigger a 400 error. Same goes for if
        a token is given that the server does not know.
        '''
        token: Optional[str] = None
        name: Optional[str] = None
        color: Optional[str] = None

        # parsed = urlparse(clientTypeRequest)

        # if parsed.path == 'login':
        #     query: Dict[str, List[str]] = parse_qs(parsed.query)
        #     if not 'name' in query or len(query['name']) != 1:
        #         print('name missing')
        #         client.sendHttpErrorResponse(404, 'Name missing')
        #         #client.sendClose()
        #         return None
            
        #     name = query['name'][0]
            
        #     if 'token' in query or len(query['token']) == 1:
        #         token = query['token'][0]
        # else:

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
        if l == 1:
            # name = tmpLs[0]
            log.msg('color missing')
            client.sendClose(code=4004, reason='Color missing')
            return None
        elif l == 2:
            # first connecting
            name, color = tmpLs
        elif l == 3:
            # reconnect
            name, token, color = tmpLs
        else:
            log.msg('name missing')
            #client.sendHttpErrorResponse(404, 'Name missing')
            client.sendClose(code=4000, reason='Name missing')
            return None
        
        # print('clientTypeRequest =', len(clientTypeRequest.strip().split('/')))

        if name is None or color is None:
            raise RuntimeError("Something went wrong in register")
        
        if token is None:
            if self.g.playerManager.isGameStarted():
                log.msg('game already started, can\'t join')
                #client.sendHttpErrorResponse(403, 'Game already started, can\'t join')
                client.sendClose(code=4001, reason='Game already started, can\'t join')
                return None
            
            pTmp: playerCode.Player
            for pTmp in self.g.playerManager:
                if pTmp.name.lower() == name.lower(): # ignore caps
                    log.msg(f'name already taken: {name}')
                    client.sendClose(code=4003, reason='Name taken')
                    return None

            
            p: playerCode.Player = playerCode.Player(name, client, color)
            log.msg("New player:", p)
            self.g.addPlayer(p)
            self.newNotificationToAll('New Player: ' + p.name)

            self.updateAll()

            return p.token

        else:
            if token in self.playerManager:
                log.msg("Reconnecting player:", token)
                p = self.playerManager[token]
                p.reconnect(client)
                self.newNotificationToAll(f'{p.name} reconnected')
            else:
                log.msg("Unknown token:", token)
                #client.sendHttpErrorResponse(403, 'Unknown token given')
                client.sendClose(code=4002, reason='Unknown token given')
                return None
        
            return p.token

    def unregister(self, client: ServerProtocol):
        token = client.token
        if token is None:
            log.msg("Player disconnected before assigned token:", token)
        elif token in self.playerManager:
            log.msg("Disconnected player:", token)
            self.newNotificationToAll(f'{self.playerManager[token].name} disconnected')
            self.playerManager[token].disconnect()            
        else:
            log.msg("Disconnected player, but token not found?:", token)
    
    def newNotificationToAll(self, msg: str):
        json_msg = { 'type': 'notification', 'content': msg }
        # special messages have a type and content
        self.broadcastToAll(json.dumps(json_msg))
    
    def broadcastToAll(self, msg: str): # sourceConnection: ServerProtocol
        '''
        Sends a message of type `str` to all currently connected
        players
        '''
        self.file.write(msg + '\n')
        self.file.flush()
        self.history.append(msg)

        encoded = msg.encode()

        for p in self.playerManager:
            if p.isConnected() and p.connection.isOpen:
                p.connection.sendMessage(encoded)
    
    def broadcastToSome(self, msg: str, tokenList: List[str], writeToHistory: bool = False):
        '''
        Sends a message of type `str` to all currently connected
        players whose token is found in the list.
        `writeToHistory`  determines whether or not this message should
        be included in the history.
        '''
        if writeToHistory:
            self.file.write(msg + '\n')
            self.file.flush()
            self.history.append(msg)
        
        encoded = msg.encode()
        
        for token in tokenList:
            p = self.playerManager.getPlayer(token)
            if p is not None and p.isConnected() and p.connection.isOpen:
                p.connection.sendMessage(encoded)
