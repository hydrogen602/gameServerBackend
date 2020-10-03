from typing import Type
import pytest
import os
import sys

sys.path.append(os.path.abspath(os.curdir))

from gameServerBackend.requestProcessor import dataTypes

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
