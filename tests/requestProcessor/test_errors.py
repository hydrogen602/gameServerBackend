
import pytest
import os
import sys

sys.path.append(os.path.abspath(os.curdir))

from gameServerBackend.requestProcessor import errors


def test_error():
    with pytest.raises(errors.ActionError):
        raise errors.ActionError
