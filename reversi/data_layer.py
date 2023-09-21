#####################
### DB operations ###
#####################

from .models import GameDB, GameState
from django.core.exceptions import ObjectDoesNotExist  # Import the necessary exception


def save_gamestate_db(board, game_id, prev_id):
    # Flatten the board and convert to string
    board_string = ''.join(str(item) for row in board for item in row)
    # print(board_string)
    # Create and save the new GameState object
    try:
        # Fetch the GameDB object
        game_object = GameDB.objects.get(pk=game_id)
    except GameDB.DoesNotExist:
        # Consider logging the error here if needed
        print(f"No GameDB object found with id: {game_id}")
        return False  # Indicate that the function did not execute successfully

    game_state_entry = GameState(game_id=game_object, board=board_string) #, prev_state=prev_state_id)
    game_state_entry.save()
    return True


def save_game_db(game_id, score_p1, score_p2, next_player, end):
    try:
        game_object = GameDB.objects.get(pk=game_id)
    except ObjectDoesNotExist:
        # You may want to log this exception, depending on your use case
        return False  # Return False or appropriate response when the object doesn't exist

    # Update the fields
    game_object.game_over = end
    game_object.score_p1 = score_p1
    game_object.score_p2 = score_p2
    game_object.next_player = next_player

    game_object.save()  # Save the changes to the database

    return True  # Return True if the function executed successfully


def remove_game_db(game_id, user):
    try:
        # Directly get the GameDB object
        game_object = GameDB.objects.get(pk=game_id)

        # Check if the user is the owner of the game
        if game_object.user != user:
            return False

        # Fetch all game states associated with the game
        all_game_states = GameState.objects.filter(game_id=game_object)

        # Delete the game states and the game
        all_game_states.delete()
        game_object.delete()

        return True
    except GameDB.DoesNotExist:
        return False


def load_gamestate_db(game_id, user, prev=False):
    # Fetch the GameDB object directly, avoiding unnecessary logic
    try:
        game_object = GameDB.objects.get(pk=game_id)
    except GameDB.DoesNotExist:
        return None

    # Check if the user is the owner or one of the players
    if user.username not in [game_object.player1, game_object.player2] and game_object.user != user:
        return None

    # Fetch the game state more efficiently
    if prev:
        # Only filter once
        game_state = GameState.objects.filter(game_id=game_object, prev_state=game_object.prev_state).last()
    else:
        game_state = GameState.objects.filter(game_id=game_object).last()

    # Guard against game_state being None
    if not game_state:
        return None

    # Deserialize the board using list comprehension
    board_string = game_state.board
    game_board = [[int(board_string[8 * r + c]) for c in range(8)] for r in range(8)]

    # Print the log message (consider changing this to a logger if you are using it in a larger application)
    print("Game Board loaded!", game_state)

    # Return the necessary values directly, avoids redundant assignments
    return game_board, game_object.player1, game_object.player2, game_object.next_player, game_state.id


def get_saved_games_for_user(user):
    return reversed(GameDB.objects.all().filter(user=user).order_by("id"))