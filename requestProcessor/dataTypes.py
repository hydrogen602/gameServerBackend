from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from .game import AbstractGame


class Player:
    '''
    The Player superclass. Subclass
    this for additional functionality.
    '''

    def __init__(self):
        self.__gameID: Optional[str] = None

    def getGameID(self) -> Optional[str]:
        '''
        Get the id of the game the player is
        currently a part of. returns None
        if the player is not part of a game.
        '''
        return self.__gameID
    
    def setGameID(self, id: Optional[str]):
        '''
        
        '''
        self.__gameID = id


class PlayerManager(ABC):

    @abstractmethod
    def addPlayer(self) -> Tuple[str, Player]:
        return NotImplemented
    
    @abstractmethod
    def getPlayer(self, id: str) -> Optional[Player]:
        return NotImplemented


class GameManager(ABC):

    @abstractmethod
    def getGame(self, id: str) -> Optional[AbstractGame]:
        return NotImplemented


class DummyDB(PlayerManager):
    def addPlayer(self) -> Tuple[str, Player]: return NotImplemented
    def getPlayer(self, id: str) -> Optional[Player]: return NotImplemented


class DummyDB2(GameManager):
    def getGame(self, id: str) -> Optional[AbstractGame]: return NotImplemented

