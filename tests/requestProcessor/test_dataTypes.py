import pytest
import os
import sys

sys.path.append(os.path.abspath(os.curdir))

from game_server_backend.requestProcessor import dataTypes

def test_player1():
    p = dataTypes.Player('test')
    assert p.getPlayerName() == 'test'
    
    assert p.getGameID() is None
    p.setGameID('g1')
    assert p.getGameID() == 'g1'
    p.setGameID(None)
    assert p.getGameID() is None

    with pytest.raises(Exception):
        dataTypes.Player('test') # already used
    
    p2 = p
    assert p is p2

def test_abc1():
    with pytest.raises(TypeError):
        class TestCls(dataTypes.GameManager):
            pass
        TestCls()
    
    with pytest.raises(TypeError):
        class TestCls(dataTypes.PlayerManager):
            pass
        TestCls()

def helper_playerManager(obj):
    d = obj

    assert d.getAllPlayersIDs() == set()

    assert d.getPlayer('player1') is None

    p = d.addPlayer('player1')

    assert d.getAllPlayersIDs() == {p.getPlayerName()}
    assert d.getPlayer('player1') == p

    with pytest.raises(Exception):
        d.addPlayer('player1')
    
    assert d.getPlayer('player2') is None

def test_basic1():
    helper_playerManager(dataTypes.BasicPlayerManager())

def helper_gameManger(obj):
    d = obj
    assert d.getAllGameIDs() == set()

    with pytest.raises(Exception):
        d.removeGame('test')
    
    assert d.getGame('test2') is None
    d.addGame('g1', None)

    assert d.getAllGameIDs() == {'g1'}
    assert d.getGame('g1') is None
    
    with pytest.raises(Exception):
        d.addGame('g1', None)
    
    assert d.removeGame('g1') is None
    assert d.getAllGameIDs() == set()
    
def test_basic2():
    d = dataTypes.BasicGameManager()
    helper_gameManger(d)