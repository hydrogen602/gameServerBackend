import pytest
import os
import sys


sys.path.append(os.path.abspath(os.curdir))

import game_server_backend.server.tokenStorage as tokenStorage
from game_server_backend.requestProcessor.dataTypes import Player

def helper(obj):
    t = obj

    assert t.getPlayerIDbyToken("") is None
    assert t.getTokenbyPlayerID("") is None

    tok = t.addPlayerID('name1')
    assert tok != 'name1'
    assert isinstance(tok, str)

    assert tok == t.getTokenbyPlayerID('name1')
    assert 'name1' == t.getPlayerIDbyToken(tok)

    tok2 = t.addPlayerID('name2')
    assert tok2 != tok
    assert isinstance(tok2, str)

    assert tok == t.getTokenbyPlayerID('name1')
    assert 'name1' == t.getPlayerIDbyToken(tok)

    assert tok2 == t.getTokenbyPlayerID('name2')
    assert 'name2' == t.getPlayerIDbyToken(tok2)

    assert t.getTokenbyPlayerID('name') is None

    with pytest.raises(Exception):
        t.addPlayerID('name1')
    
    Player._testClearNamesUsed()
    p = Player('name3')
    tok3 = t.addPlayerID(p)

    assert tok != tok2 != tok3
    assert isinstance(tok3, str)

    assert tok3 == t.getTokenbyPlayerID(p)
    assert p.getPlayerName() == t.getPlayerIDbyToken(tok3)

def test_basicTokenStorage():
    helper(tokenStorage.BasicTokenStorage())

def test_sqliteDB():
    t = tokenStorage.PersistentTokenStorage(':memory:')
    helper(t)
