#####################
### DB operations ###
#####################

from .models import GameDB, GameState


def save_gamestate_db(board, game_id):
    flat_board = [item for row in board for item in row]
    board_string = ""
    for num in flat_board:
        board_string += str(num)
    print(board_string)
    gameDB_object = GameDB.objects.get(pk=game_id)
    game_state_entry = GameState(game_id=gameDB_object, board=board_string)
    game_state_entry.save()


def save_game_db(game_id, score_p1, score_p2, end):
    gameDB_object = GameDB.objects.get(pk=game_id)
    gameDB_object.game_over = end
    gameDB_object.score_p1 = score_p1
    gameDB_object.score_p2 = score_p2
    gameDB_object.save()
    return True


def remove_game_db(game_id, user):
    gameDB_object = GameDB.objects.get(pk=game_id)
    if gameDB_object.user == user:
        gameDB_object.delete()
        return True
    else:
        return False


def load_gamestate_db(game_id, user):
    gameDB_object = GameDB.objects.get(pk=game_id)
    if not gameDB_object.user == user:
        return None, None, None
    print("Game object: ", gameDB_object)

    # game_state_objects = GameState.objects.all().filter(game_id=gameDB_object)[::-1]
    # game_state = game_state_objects[0]
    game_state = GameState.objects.all().filter(game_id=gameDB_object).last()
    print("Got GameState object from DB:", game_state)

    # deserialize board and save it to session variable
    board_string = game_state.board
    print(board_string)
    game_board = [[0, 0, 0, 0, 0, 0, 0, 0] for x in range(8)]
    cell = 0
    for r in range(8):
        for c in range(8):
            game_board[r][c] = int(board_string[cell])
            cell += 1
    print("Game Board loaded!")
    player1 = gameDB_object.player1
    player2 = gameDB_object.player2

    return game_board, player1, player2
