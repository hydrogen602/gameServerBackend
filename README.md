![Python application](https://github.com/hydrogen602/gameServerBackend/workflows/Python%20application/badge.svg)
# gameServerBackend
A WebSocket based server for web games. Requires at least Python3.7

The objective is to make one websocket server than can track many users and games and know which users is playing what game. 
The goal is to make it so that it can be easily used to make a new game without having to worry about the issues of managing a
websocket server or identifying players, so that the game code can be given just a player and the action the player would like to perform.

## Docs

http://www.jonathanrotter.com/gameServerBackend/

## Notes
- lets have player id be the name

## How to run the example:
- go the the example directory
- run `python3 game.py`
- open the `index.html` page
- enter a name and connect  
Note: Little to no effort has been put into the frontend of the example because it is just for testing purposes
