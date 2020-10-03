import pytest
import os
import sys
from gameServerBackend.requestProcessor import interactions

sys.path.append(os.path.abspath(os.curdir))

from gameServerBackend.requestProcessor.requestProcess import RequestProcessor
from gameServerBackend.requestProcessor.dataTypes import BasicPlayerManager, BasicGameManager
import gameServerBackend.requestProcessor.interactions as interactions


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

    helperFailure(x.process(interactions.UnprocessedClientRequest('hello', None)), 'Empty request')
    helperFailure(x.process(interactions.UnprocessedClientRequest('hello', 'r')), 'no joined game')

    resp = x.process(interactions.JoinGameClientRequest('hello', 'game1', None))
    helperFailure(resp, 'game not found')