from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from .dataTypes import Player
from . import interactions


class AbstractGame(ABC):
    '''
    Games should derive from AbstractGame.
    It provides a few necessary methods for games to
    interact with the game managing code.
    Remember to call super().__init__() in
    the __init__ methods of any subclass.

    _hasGameStarted: bool tracks if the game has started
    '''
    
    def __init__(self):
        self._hasGameStarted: bool = False
    
    @property
    def hasGameStarted(self) -> bool:
        '''
        Returns if a game has started or not
        '''
        return self._hasGameStarted
    
    def startGame(self):
        '''
        starts the game. This sets
        _hasGameStarted to True. If the game
        has already started, it throws a ValueError.
        '''
        if self._hasGameStarted:
            raise ValueError('Game already started')
        self._hasGameStarted = True

    @abstractmethod
    def joinPlayer(self, playerData: Player, otherRequestData: Optional[str]) -> interactions.Response:
        '''
        abstractmethod.
        Called when a player wants to join a Game.
        otherRequestData is extra data that can be send by joining players to the game
        '''
        return NotImplemented
    
    @abstractmethod
    def leavePlayer(self, playerData: Player) -> interactions.ResponseSuccess:
        '''
        abstractmethod.
        Called when a player exits the game.
        If the player doesn't exist, ignore.
        '''
        return NotImplemented
    
    @abstractmethod
    def listPlayers(self) -> List[Player]:
        '''
        abstractmethod.
        Get a list of all players in game
        '''
        return NotImplemented
    
    @abstractmethod
    def handleRequest(self, playerData: Player, request: str) -> interactions.Response:
        '''
        abstractmethod.
        Called when a player makes a request or action. The string `request`
        is unmodified from what was received.
        '''
        return NotImplemented