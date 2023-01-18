# Web Programming with Python and JavaScript

## Project Name: Rev3rsi

## Description
Reversi is a classic board game for two players just like chess, checkers and go...
Rules and details: https://www.yourturnmyturn.com/rules/reversi.php

The Game has been implemented using Django as the backend where games, game states and scores are saved to an sqlite3 data base.


## Features
### Landing Page:
- mobile responsive JS animation using svg objects and D3JS library

### Mobile responsive design:
- using only CSS styling (no images).

### Machine Player:
Players can select different machine players (difficulty) and therefore play against different algorithms.

### Game History:
- Recover previously initiated games
- Replay last move of finalized games
- Delete own games


## Requirements
- Django


## Future improvements
- implement alpha-beta algorithm for machine player (will yield a huge increase in performance, and defacto unbeatable by regular players)
- Game statistics, leader board
- Online multiplayer game using sockets
- deploy inside a docker container on aws
