import pytest
import os
import sys

sys.path.append(os.path.abspath(os.curdir))

from gameServerBackend.requestProcessor.dataTypes import Player
from gameServerBackend.requestProcessor import interactions

def test_request():
    x = interactions.UnprocessedClientRequest('test', 'sample')

    assert x.playerID == 'test'
    assert x.request == 'sample'

    with pytest.raises(AssertionError):
        x = interactions.UnprocessedClientRequest(None, 'sample2')

def test_request2():
    
    x = interactions.JoinGameClientRequest('name1234', 'game1', None)
    assert x.gameID == 'game1'
    assert x.playerID == 'name1234'
    assert x.otherData is None

    with pytest.raises(AssertionError):
        x = interactions.JoinGameClientRequest(None, 'game1', None)

    x = interactions.JoinGameClientRequest('name', 'game', 'other data')

    assert x.gameID == 'game'
    assert x.playerID == 'name'
    assert x.otherData == 'other data'

    assert x.request == x.JOIN_GAME

def test_response1():

    with pytest.raises(Exception):
        interactions.Response(Player('name'))
    
def test_response2():
    p = Player('name1')
    p2 = Player('name2')
    x = interactions.ResponseSuccess(None, p)

    assert x.dataToAll == None
    assert x.dataToSender == None
    assert x.dataToSome == None
    assert x.errorMsg == None
    assert x.sender == p
    assert x.isValid

    x2 = interactions.ResponseSuccess('senderData', p, ([p, p2], 'toAll'), {p2: 'specific'})

    assert x2.dataToAll == ([p, p2], 'toAll')
    assert x2.dataToSender == 'senderData'
    assert x2.dataToSome == {p2: 'specific'}
    assert x2.errorMsg == None
    assert x2.sender == p
    assert x2.isValid

    x3 = interactions.ResponseFailure(p, 'err message')

    assert x3.errorMsg == 'err message'
    assert x3.sender == p
    assert not x3.isValid

    