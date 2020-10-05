'''
An example on how to use this software by making
a simple chat system
'''


import sys
import os
from typing import Dict, Set
sys.path.append(os.path.join(os.curdir, '..'))

from gameServerBackend.requestProcessor import dataTypes, game, interactions, RequestProcessor, Player
from gameServerBackend.server import Server


class ChatSystem(game.AbstractGame):

    def __init__(self) -> None:
        super().__init__()
        self.__players: Set[Player] = set()

    def joinPlayer(self, playerData: Player) -> interactions.Response:
        self.__players.add(playerData)
        return interactions.ResponseSuccess('Joined successfully', playerData, (list(self.__players), f'{playerData.getPlayerName()} joined'))

    def handleRequest(self, playerData: Player, request: str) -> interactions.Response:
        if request.startswith('/'):
            if request == '/h' or request == '/help':
                return interactions.ResponseSuccess('Help not yet implemented', playerData)

        return interactions.ResponseSuccess(None, playerData, (list(self.__players), f'{playerData.getPlayerName()}> {request}'))

    def leavePlayer(self, playerData: Player) -> interactions.ResponseSuccess:
        if playerData in self.__players:
            self.__players.remove(playerData)
            return interactions.ResponseSuccess('You left this group', playerData, (list(self.__players), f'{playerData.getPlayerName()} left'))
        return interactions.ResponseSuccess('Already left this group', playerData)


if __name__ == "__main__":
    gameDB = dataTypes.BasicGameManager()
    playerDB = dataTypes.BasicPlayerManager()

    gameDB.addGame('chat', ChatSystem())

    rp = RequestProcessor(playerDB, gameDB)

    s = Server('localhost', 5000, requestProcessor=rp, config={'USE_SSL': False})

    s.run()

'''
Testing code
function f(r) {
    ws = new WebSocket('ws://127.0.0.1:5000/'+r)
    ws.onerror = (e) => {console.error(e)}
    ws.onopen = (e) => {console.log(e)}
    ws.onclose = (e) => {console.log(e)}
    ws.onmessage = (e) => {console.log(e)}
    return ws
}
ws = f('')
ws = f('tester1')
ws = f('noexist/tester1')
ws = f('noexist/tester1/')
ws = f('noexist/tester1/null')
'''