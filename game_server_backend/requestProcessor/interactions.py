from __future__ import annotations
from typing import Dict, List, Optional, TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from game_server_backend.requestProcessor.dataTypes import Player


class UnprocessedClientRequest:
    '''
    `UnprocessedClientRequest` represents a
    request by the client to the server while
    already in a game. If the client would like
    to join a game, use `JoinGameClientRequest`
    '''

    JOIN_GAME = 'JOIN_GAME_REQUEST'

    def __init__(self, playerID: str, request: Optional[str]):
        assert playerID is not None
        self.__playerID: str = playerID
        self.__request: Optional[str] = request

    @property
    def playerID(self) -> str:
        return self.__playerID

    @property
    def request(self) -> Optional[str]:
        return self.__request


class JoinGameClientRequest(UnprocessedClientRequest):
    '''
    JoinGameClientRequest should be sent if the player's
    request is to join a game
    '''

    def __init__(self, playerID: str, gameId: str, otherData: Optional[str]):
        super().__init__(playerID=playerID, request=self.JOIN_GAME)
        assert gameId is not None
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
    Unfortunately, dataToAll needs to be given a list
    of all players in the game, as the websocket code
    won't be able to figure it out otherwise
    '''
    
    def __init__(self, dataToSender: Optional[str], sender: Player, dataToAll: Optional[Tuple[List[Player], str]] = None, dataToSome: Optional[Dict[Player, str]] = None):
        self.dataToSender: Optional[str] = dataToSender
        self.dataToAll: Optional[Tuple[List[Player], str]] = dataToAll
        self.dataToSome: Optional[Dict[Player, str]] = dataToSome
        super().__init__(sender)

    @property
    def isValid(self) -> bool:
        return True


class ResponseFailure(Response):
    '''
    Represents if a request failed. It
    can specify an error message to send to the client.
    '''

    def __init__(self, sender: Player, errMsg: str):
        super().__init__(sender)
        self.errorMsg: str = errMsg

    @property
    def isValid(self) -> bool:
        return False
