from __future__ import annotations
from os import sendfile
from typing import Dict, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from gameServerBackend.requestProcessor.dataTypes import Player


class UnprocessedClientRequest:
    '''
    `UnprocessedClientRequest` represents a
    request by the client to the server while
    already in a game. If the client would like
    to join a game, use `JoinGameClientRequest`
    '''

    JOIN_GAME = 'JOIN_GAME_REQUEST'

    def __init__(self, playerID: Optional[str], request: Optional[str]):
        self.__playerID: Optional[str] = playerID
        self.__request: Optional[str] = request

    @property
    def playerID(self) -> Optional[str]:
        return self.__playerID

    @property
    def request(self) -> Optional[str]:
        return self.__request

    def setPlayerID(self, pID: str):
        self.__playerID = pID


class JoinGameClientRequest(UnprocessedClientRequest):
    '''
    JoinGameClientRequest should be sent if the player's
    request is to join a game
    '''

    def __init__(self, playerID: Optional[str], gameId: str, otherData: Optional[str]):
        super().__init__(playerID=playerID, request=self.JOIN_GAME)
        self.__gameID: str = gameId
        self.__otherData: Optional[str] = otherData

    @property
    def gameID(self) -> str:
        return self.__gameID

    @property
    def otherData(self) -> Optional[str]:
        return self.__otherData


class Response:

    def __init__(self, sender: Player):
        if type(self) is Response:
            raise TypeError('"Response" is only for subclassing and should not be instantiated')

        self.errorMsg: Optional[str] = None
        self.sender: Player = sender

    def __init_subclass__(cls):
        if cls.isValid is Response.isValid:
            raise TypeError(f'Response subclass "{cls.__name__}" did not implement "isValid"')
        super().__init_subclass__()
    
    @property
    def isValid(self) -> bool:
        return NotImplemented


class ResponseSuccess(Response):
    '''
    Represents if a request was successful. It
    can specify data to send to the client.
    '''
    
    def __init__(self, dataToSender: Optional[str], sender: Player, dataToAll: Optional[str] = None, dataToSome: Optional[Dict[Player, str]] = None):
        self.dataToSender: Optional[str] = dataToSender
        self.dataToAll: Optional[str] = dataToAll
        self.dataToSome: Optional[Dict[Player, str]] = dataToSome
        super.__init__(sender)

    @property
    def isValid(self) -> bool:
        return True


class ResponseFailure(Response):
    '''
    Represents if a request failed. It
    can specify an error message to send to the client.
    '''

    def __init__(self, sender: Player, errMsg: str):
        super.__init__(sender)
        self.errorMsg: str = errMsg

    @property
    def isValid(self) -> bool:
        return False