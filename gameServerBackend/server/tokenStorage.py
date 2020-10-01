from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Dict, Optional, TYPE_CHECKING, Union
from secrets import token_urlsafe
if TYPE_CHECKING:
    from ..requestProcessor.dataTypes import Player


class TokenStorage(ABC):

    @abstractmethod
    def getPlayerIDbyToken(self, token: str) -> Optional[str]:
        return NotImplemented
    
    @abstractmethod
    def getTokenbyPlayerID(self, playerID: Union[str, Player]) -> Optional[str]:
        return NotImplemented
    
    @abstractmethod
    def addPlayerID(self, playerID: Union[str, Player]) -> str:
        '''
        Add a player with a player id to the list and
        generate and return a token.
        Raise ValueError if the player id already exists.
        '''
        return NotImplemented


class BasicTokenStorage(TokenStorage):

    def __init__(self, maximum: int = 100):
        self.__tokenBased: Dict[str, str] = {}
        self.__playerIDBased: Dict[str, str] = {}
        self.__maximum: int = maximum
    
    def getPlayerIDbyToken(self, token: str) -> Optional[str]:
        return self.__tokenBased.get(token)
    
    def getTokenbyPlayerID(self, playerID: Union[str, Player]) -> Optional[str]:
        if not isinstance(playerID, str):
            playerID = playerID.getPlayerName()
        return self.__playerIDBased.get(playerID)
    
    def addPlayerID(self, playerID: Union[str, Player]):
        if len(self.__playerIDBased) >= self.__maximum:
            raise RuntimeError(f'Too many players:max is {self.__maximum}')
        if not isinstance(playerID, str):
            playerID = playerID.getPlayerName()
        if playerID in self.__playerIDBased:
            raise ValueError('Player ID taken')
        
        token = token_urlsafe(16)
        while token in self.__tokenBased:
            token = token_urlsafe(16)
        
        self.__playerIDBased[playerID] = token
        self.__tokenBased[token] = playerID

        return token
        


    

