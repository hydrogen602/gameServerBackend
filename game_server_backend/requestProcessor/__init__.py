'''
Handles the game interface part and some data structures.
'''

from .dataTypes import Player, PlayerManager, GameManager
from .errors import ActionError
from .game import AbstractGame
from .interactions import Response, ResponseFailure, ResponseSuccess, UnprocessedClientRequest, JoinGameClientRequest
from .requestProcess import RequestProcessor