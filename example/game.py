'''
An example on how to use this software by making
a simple chat system
'''


import sys
import os
import time
from typing import List, Optional, Set
sys.path.append(os.path.join(os.curdir, '..'))

from game_server_backend.requestProcessor import dataTypes, game, interactions, RequestProcessor, Player
from game_server_backend.server import Server


class ChatSystem(game.AbstractTimeGame): # AbstractGame

    def __init__(self) -> None:
        super().__init__()
        self.__players: Set[Player] = set()

    def joinPlayer(self, playerData: Player, otherRequestData: Optional[str]) -> interactions.Response:
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

    def listPlayers(self) -> List[Player]:
        return list(self.__players)

    def onTimer(self) -> Optional[interactions.TimerResponse]:
        return interactions.TimerResponse((list(self.__players), f'The current time is: {time.ctime()}'))


lastT: float = 0
def callout():
    global lastT
    t = time.time()
    print(f'{t - lastT} seconds passed')
    lastT = t


if __name__ == "__main__":
    gameDB = dataTypes.BasicGameManager()
    playerDB = dataTypes.BasicPlayerManager()

    gameDB.addGame('chat', ChatSystem())

    rp = RequestProcessor(playerDB, gameDB)

    s = Server('localhost', 5000, requestProcessor=rp, config={'USE_SSL': False, 'verbose': True, 'printAllOutgoing': True})

    s.run(timeout=5, func=callout) # 

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