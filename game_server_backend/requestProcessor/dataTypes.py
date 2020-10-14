from __future__ import annotations
from typing import Dict, Optional, Set, TYPE_CHECKING, Union
from abc import ABC, abstractmethod
# import sqlite3
# import atexit
if TYPE_CHECKING:
    from .game import AbstractGame


class Player:
    '''
    The Player superclass. Subclass
    this for additional functionality.
    It should keep all data regarding a player
    '''

    __namesUsed: Set[str] = set()

    @classmethod
    def _testClearNamesUsed(cls):
        '''
        Internal function to help with unit testing.
        Do not use in actual code
        '''
        cls.__namesUsed.clear()

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
        '''
        Set the game id of the player's current game.
        '''
        self.__gameID = id
    
    def getPlayerName(self) -> str:
        '''
        Get the player name/id
        '''
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
        abstractmethod.
        Add a player with the given name. Throws an exception if the name exists
        '''
        return NotImplemented
    
    @abstractmethod
    def getPlayer(self, id: str) -> Optional[Player]:
        '''
        abstractmethod.
        Get the Player object corresponding with a player name/id.
        Returns None if not found.
        '''
        return NotImplemented
    
    @abstractmethod
    def getAllPlayersIDs(self) -> Set[str]:
        '''
        abstractmethod.
        Get all player names/ids
        '''
        return NotImplemented


class GameManager(ABC):
    '''
    GameManager is an interface between
    the request processor and any possible
    storage system for the player data.
    '''

    @abstractmethod
    def getGame(self, id: str) -> Optional[AbstractGame]:
        '''
        abstractmethod.
        Get the Game object correspoding to the game id and None if not found.
        '''
        return NotImplemented
    
    @abstractmethod
    def addGame(self, id: str, game: AbstractGame):
        '''
        abstractmethod.
        Add a game together with its game id.
        '''
        return NotImplemented
    
    @abstractmethod
    def removeGame(self, id: str) -> AbstractGame:
        '''
        abstractmethod.
        Remove a game. It is not known if this works, so use with caution
        or avoid all together.
        '''
        return NotImplemented
    
    @abstractmethod
    def getAllGameIDs(self) -> Set[str]:
        '''
        abstractmethod.
        Get all game ids
        '''
        return NotImplemented


class BasicPlayerManager(PlayerManager):
    '''
    The default implementation of PlayerManager
    if no custom implementation is given.
    '''

    def __init__(self) -> None:
        self.__data: Dict[str, Player] = {}
    
    def addPlayer(self, playerId: str) -> Player: 
        if playerId in self.__data:
            raise ValueError(f'Name already exists: {playerId}')
        self.__data[playerId] = Player(playerName=playerId)
        return self.__data[playerId]

    def getPlayer(self, id: str) -> Optional[Player]:
        return self.__data.get(id)
    
    def getAllPlayersIDs(self) -> Set[str]:
        return set(self.__data.keys())
    
    def __len__(self) -> int:
        return len(self.__data)


class BasicGameManager(GameManager):
    '''
    The default implementation of GameManager
    if no custom implementation is given.
    '''

    def __init__(self) -> None:
        self.__data: Dict[str, AbstractGame] = {}

    def getGame(self, id: str) -> Optional[AbstractGame]:
        return self.__data.get(id)
    
    def addGame(self, gameID: str, game: AbstractGame):
        if gameID in self.__data:
            raise ValueError('game already exists')
        self.__data[gameID] = game
    
    def removeGame(self, gameID: str) -> AbstractGame:
        if gameID not in self.__data:
            raise KeyError('GameID not found')
        return self.__data.pop(gameID)
    
    def getAllGameIDs(self) -> Set[str]:
        return set(self.__data.keys())
        
    def __len__(self) -> int:
        return len(self.__data)
