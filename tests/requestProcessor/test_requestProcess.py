from typing import Set
import pytest
import os
import sys


sys.path.append(os.path.abspath(os.curdir))

from gameServerBackend.requestProcessor.requestProcess import RequestProcessor
from gameServerBackend.requestProcessor.dataTypes import BasicPlayerManager, BasicGameManager, Player
from gameServerBackend.requestProcessor import interactions
from gameServerBackend.requestProcessor.game import AbstractGame


class HelperGame(AbstractGame):

    def __init__(self) -> None:
        self._players: Set[Player] = set()
        super().__init__()

    def handleRequest(self, playerData: Player, request: str) -> interactions.Response:
        return interactions.ResponseSuccess('request was: '+ request, playerData, None, None)
    
    def joinPlayer(self, playerData: Player) -> interactions.Response:
        assert playerData not in self._players
        self._players.add(playerData)
        return interactions.ResponseSuccess('', playerData, f'player joined: "{playerData.getPlayerName()}"', None)

    def leavePlayer(self, playerData: Player) -> interactions.ResponseSuccess:
        if playerData in self._players:
            self._players.remove(playerData)
        return interactions.ResponseSuccess(None, playerData, None, None)


def test_creation():
    playerDB = BasicPlayerManager()
    gameDB = BasicGameManager()
    x = RequestProcessor(playerDB, gameDB)
    assert x.gameDatabase is gameDB
    assert x.playerDatabase is playerDB 


def helperFailure(r: interactions.Response, msg: str):
    assert isinstance(r, interactions.ResponseFailure)
    assert msg.lower() in r.errorMsg.lower()


def test_process1():
    playerDB = BasicPlayerManager()
    gameDB = BasicGameManager()
    x = RequestProcessor(playerDB, gameDB)

    assert x.gameDatabase is gameDB
    assert x.playerDatabase is playerDB

    helperFailure(x.process(interactions.UnprocessedClientRequest('hello', None)), 'Empty request')
    helperFailure(x.process(interactions.UnprocessedClientRequest('hello', 'r')), 'no joined game')

    resp = x.process(interactions.JoinGameClientRequest('hello', 'game1', None))
    helperFailure(resp, 'game not found')


def test_processJoinGame():
    Player._testClearNamesUsed()
    playerDB = BasicPlayerManager()
    gameDB = BasicGameManager()
    gameDB.addGame('game1', HelperGame())
    x = RequestProcessor(playerDB, gameDB)

    resp = x.process(interactions.JoinGameClientRequest('player1', 'game1', 'other data'))

    assert x.playerDatabase.getAllPlayersIDs() == {'player1'}
    p = x.playerDatabase.getPlayer('player1')

    assert gameDB.getGame('game1')._players == {p}

    assert resp.isValid
    assert isinstance(resp, interactions.ResponseSuccess)

    assert resp.sender == p
    assert p.getGameID() == 'game1'
    assert resp.errorMsg is None

    resp = x.process(interactions.JoinGameClientRequest('player1', 'game2', 'other data'))

    assert x.playerDatabase.getAllPlayersIDs() == {'player1'}
    p = x.playerDatabase.getPlayer('player1')

    assert not resp.isValid
    assert isinstance(resp, interactions.ResponseFailure)

    assert resp.sender == p
    assert p.getGameID() == 'game1'
    assert resp.errorMsg is not None

    gameDB.addGame('game2', HelperGame())
    resp = x.process(interactions.JoinGameClientRequest('player1', 'game2', 'other data'))

    assert x.playerDatabase.getAllPlayersIDs() == {'player1'}
    p = x.playerDatabase.getPlayer('player1')

    assert resp.isValid
    assert isinstance(resp, interactions.ResponseSuccess)

    assert resp.sender == p
    assert p.getGameID() == 'game2'
    assert resp.errorMsg is None


def test_process2():
    Player._testClearNamesUsed()
    playerDB = BasicPlayerManager()
    gameDB = BasicGameManager()
    gameDB.addGame('game1', HelperGame())
    gameDB.addGame('game2', HelperGame())

    x = RequestProcessor(playerDB, gameDB)

    resp = x.process(interactions.JoinGameClientRequest('player1', 'game1', 'other data'))

    assert resp.isValid

    resp = x.process(interactions.UnprocessedClientRequest('player1', 'some request'))

    assert x.playerDatabase.getAllPlayersIDs() == {'player1'}
    p = x.playerDatabase.getPlayer('player1')

    assert resp.isValid
    assert isinstance(resp, interactions.ResponseSuccess)

    assert resp.sender == p
    assert p.getGameID() == 'game1'
    assert resp.errorMsg is None