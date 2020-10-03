from __future__ import annotations
from typing import Dict, Optional, Set, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from .game import AbstractGame


class Player:
    '''
    The Player superclass. Subclass
    this for additional functionality.
    It should keep all data regarding a player
    '''
    __namesUsed: Set[str] = set()

    def __init__(self, playerName: str):
        self.__gameID: Optional[str] = None
        if playerName in self.__namesUsed:
            raise ValueError(f'Player name already used: {playerName}')
        self.__namesUsed.add(playerName)
        self.__playerName: str = playerName

    def getGameID(self) -> Optional[str]:
        '''
        Get the id of the game the player is
        currently a part of. returns None
        if the player is not part of a game.
        '''
        return self.__gameID
    
    def setGameID(self, id: Optional[str]):
        self.__gameID = id
    
    def getPlayerName(self) -> str:
        return self.__playerName
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, Player):
            return self is o
        else:
            return False
    
    def __hash__(self) -> int:
        return hash(self.__playerName)


class PlayerManager(ABC):
    '''
    PlayerManager is an interface between
    the request processor and any possible
    storage system for the player data.
    '''

    @abstractmethod
    def addPlayer(self, playerId: str) -> Player:
        '''
        Add a player with the given name. Throws an exception if the name exists
        '''
        return NotImplemented
    
    @abstractmethod
    def getPlayer(self, id: str) -> Optional[Player]:
        return NotImplemented


class GameManager(ABC):
    '''
    GameManager is an interface between
    the request processor and any possible
    storage system for the player data.
    '''

    @abstractmethod
    def getGame(self, id: str) -> Optional[AbstractGame]:
        return NotImplemented


class BasicPlayerManager(PlayerManager):
    def __init__(self) -> None:
        self.__data: Dict[str, Player] = {}
    
    def addPlayer(self, playerId: str) -> Player: 
        if playerId in self.__data:
            raise ValueError(f'Name already exists: {playerId}')
        self.__data[playerId] = Player(playerName=playerId)
        return self.__data[playerId]

    def getPlayer(self, id: str) -> Optional[Player]:
        return self.__data.get(id)
    
    def __len__(self) -> int:
        return len(self.__data)


class BasicGameManager(GameManager):
    def __init__(self) -> None:
        self.__data: Dict[str, AbstractGame] = {}

    def getGame(self, id: str) -> Optional[AbstractGame]:
        return self.__data.get(id)
    
    def __len__(self) -> int:
        return len(self.__data)

