'''
An example on how to use this software by making
a simple chat system
'''

import sys
import os
from typing import Dict, Set
sys.path.append(os.path.join(os.curdir, '..'))

from gameServerBackend.requestProcessor import dataTypes, game, interactions
from gameServerBackend.requestProcessor.dataTypes import Player


class ChatSystem(game.AbstractGame):
    
    def __init__(self) -> None:
        super().__init__()
        self.__players: Set[Player] = set()
    
    def joinPlayer(self, playerData: Player) -> interactions.Response:
        self.__players.add(playerData)
        return interactions.ResponseSuccess('Joined successfully', playerData, f'{playerData.getPlayerName()} joined')
    
    def handleRequest(self, playerData: Player, request: str) -> interactions.Response:
        return interactions.ResponseSuccess(None, playerData, f'{playerData.getPlayerName()}> {request}')
    
    def leavePlayer(self, playerData: Player) -> interactions.ResponseSuccess:
        if playerData in self.__players:
            self.__players.remove(playerData)
            return interactions.ResponseSuccess('You left this group', playerData, f'{playerData.getPlayerName()} left')
        return interactions.ResponseSuccess('Already left this group', playerData)
