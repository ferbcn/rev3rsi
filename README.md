# Rev3rsi 
Web Programming with Python-Django and JavaScript/CSS.

![Screenshot](https://github.com/ferbcn/rev3rsi/blob/master/rev3rsi.png?raw=true)

## Description
Reversi is a classic board game for two players just like chess, checkers and go...
Rules and details: https://www.yourturnmyturn.com/rules/reversi.php

The Game has been implemented using Django as the backend where games, game states and scores are saved to an sqlite3 data base.

## Features
### Landing Page:
- mobile responsive JS animation using svg objects and D3JS library

### Mobile responsive design:
- using only CSS styling (no images).

### Human vs Machine Game
Players can select different machine players (difficulty) playing against different algorithms.
Easy: Random
Hard: Greedy 
Harder: Greedy with heuristics
Hardest: Minimax with alpha-beta pruning

### Human vs Human Online Match
Arena implements a chat room functionality where players can meet and initiate anew match against an other online player.

### Game History:
- Recover previously initiated games

## Requirements
- Django
- PostgreSQL 
- Redis (for caching matches waiting for opponent)

## Future improvements
- implement alpha-beta algorithm for machine player (will yield a huge increase in performance, and defacto unbeatable by regular players)
- Game statistics, leader board
- Online multiplayer game using sockets
- deploy inside a docker container on aws

## Try it!
http://www.rev3rsi.fun

### Deployment:
- Cloud Instance 
- Docker
- uvicorn