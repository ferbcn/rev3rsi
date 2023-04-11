#####################
### DB operations ###
#####################

from .models import GameDB, GameState


def save_gamestate_db(board, game_id, prev_state_id):
    flat_board = [item for row in board for item in row]
    board_string = ""
    for num in flat_board:
        board_string += str(num)
    # print(board_string)
    gameDB_object = GameDB.objects.get(pk=game_id)
    game_state_entry = GameState(game_id=gameDB_object, board=board_string, prev_state=prev_state_id)
    game_state_entry.save()


def save_game_db(game_id, score_p1, score_p2, next_player, end):
    gameDB_object = GameDB.objects.get(pk=game_id)
    gameDB_object.game_over = end
    gameDB_object.score_p1 = score_p1
    gameDB_object.score_p2 = score_p2
    gameDB_object.next_player = next_player
    gameDB_object.save()
    return True


def remove_game_db(game_id, user):
    gameDB_object = GameDB.objects.get(pk=game_id)
    all_game_states = GameState.objects.all().filter(game_id=gameDB_object)
    if gameDB_object.user == user:
        gameDB_object.delete()
        all_game_states.delete()
        return True
    else:
        return False


def load_gamestate_db(game_id, user, prev=False):
    gameDB_object = GameDB.objects.get(pk=game_id)
    # Only allow players or the owner of the game
    players = [gameDB_object.player1, gameDB_object.player2]
    if not user.username in players:
        if not gameDB_object.user == user:
            return None

    # Get Game DB object
    game_state = GameState.objects.all().filter(game_id=gameDB_object).last()

    if prev:
        game_state = GameState.objects.all().filter(game_id=gameDB_object, prev_state=game_state.prev_state)


    # deserialize board
    board_string = game_state.board
    # print(board_string)
    game_board = [[0, 0, 0, 0, 0, 0, 0, 0] for x in range(8)]
    cell = 0
    for r in range(8):
        for c in range(8):
            game_board[r][c] = int(board_string[cell])
            cell += 1

    print("Game Board loaded!", game_state)
    player1 = gameDB_object.player1
    player2 = gameDB_object.player2
    next_player = gameDB_object.next_player

    return game_board, player1, player2, next_player, game_state.id

def get_saved_games_for_user(user):
    return reversed(GameDB.objects.all().filter(user=user).order_by("id"))