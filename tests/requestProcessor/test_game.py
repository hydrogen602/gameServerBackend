import pytest
import os
import sys

sys.path.append(os.path.abspath(os.curdir))

from gameServerBackend.requestProcessor.game import AbstractGame

def test_abstract():
    with pytest.raises(Exception):
        AbstractGame()