'''
Handles communcation with players with websockets. In order to run
this project, create an instance of `server.Server` and call `.run()`
on it, and it will handle connections until receiving a SIGINT (^C).
'''

from .server import Server
from .tokenStorage import TokenStorage