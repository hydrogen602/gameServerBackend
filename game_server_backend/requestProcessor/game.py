from __future__ import annotations
from abc import ABC, abstractmethod
from .dataTypes import Player
from . import interactions


class AbstractGame(ABC):
    '''
    Games should derive from AbstractGame.
    It provides a few necessary methods for games to
    interact with the game managing code.
    Remember to call super().__init__() in
    the __init__ methods of any subclass.

    _hasGameStarted tracks if the game has started
    '''
    
    def __init__(self):
        self._hasGameStarted: bool = False
    
    @property
    def hasGameStarted(self) -> bool:
        return self._hasGameStarted
    
    def startGame(self):
        if self._hasGameStarted:
            raise ValueError('Game already started')
        self._hasGameStarted = True

    @abstractmethod
    def joinPlayer(self, playerData: Player) -> interactions.Response:
        '''
        Called when a player wants to join a Game.
        '''
        return NotImplemented
    
    @abstractmethod
    def leavePlayer(self, playerData: Player) -> interactions.ResponseSuccess:
        '''
        Called when a player exits the game.
        If the player doesn't exist, ignore.
        '''
        return NotImplemented
    
    @abstractmethod
    def handleRequest(self, playerData: Player, request: str) -> interactions.Response:
        '''
        Called when a player makes a request or action. The string `request`
        is unmodified from what was received.
        '''
        return NotImplemented