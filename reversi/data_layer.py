#####################
### DB operations ###
#####################

from .models import GameDB, GameState, Rating, User
from django.core.exceptions import ObjectDoesNotExist  # Import the necessary exception
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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

    game_state_entry = GameState(game_id=game_object, board=board_string)
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

    # Return the necessary values directly, avoids redundant assignments
    return game_board, game_object.player1, game_object.player2, game_object.next_player, game_state.id


def load_gamestate_board(game_id):
    # Fetch the GameDB object directly, avoiding unnecessary logic
    try:
        game_state = GameState.objects.filter(game_id=game_id).last()
    except GameDB.DoesNotExist:
        return None

    # Deserialize the board using list comprehension
    board_string = game_state.board
    game_board = [[int(board_string[8 * r + c]) for c in range(8)] for r in range(8)]

    # Return the necessary values directly, avoids redundant assignments
    return game_board


def load_game_object_data(game_id):
    try:
        game_object = GameDB.objects.get(pk=game_id)
    except GameDB.DoesNotExist:
        return None
    return game_object


def get_all_saved_games_for_user(user):
    return reversed(GameDB.objects.all().filter(user=user).order_by("id"))


def get_saved_games_for_user(user, page=1, page_size=10):
    saved_games = GameDB.objects.all().filter(user=user).order_by("id").reverse()
    paginator = Paginator(saved_games, page_size)

    try:
        paginated_saved_games = paginator.page(page)
    except PageNotAnInteger:
        paginated_saved_games = paginator.page(1)
    except EmptyPage:
        paginated_saved_games = paginator.page(paginator.num_pages)

    return paginated_saved_games


def get_last_saved_game_id():
    try:
        game_object = GameDB.objects.filter(game_over=True).last()
        return game_object.id
    except ObjectDoesNotExist:
        return None


def get_rating_for_user(username):
    try:
        user = User.objects.get(username=username)
        rating = Rating.objects.get(user=user)
        return rating.elo
    except ObjectDoesNotExist:
        return None


def create_base_rating_for_user(username):
    try:
        rating = Rating(user=User.objects.get(username=username))
        rating.save()
        print(f"Base rating for User {username} created!")
    except ObjectDoesNotExist:
        user = User.objects.create(username=username, password=username)
        user.save()
        rating = Rating(user=user)
        rating.save()
        print(f"User {username} created with base rating!")
    return rating


def get_ratings_for_all_users():
    all_ratings = reversed(Rating.objects.all().order_by("elo"))
    return all_ratings


def get_ratings_for_user(player_name):
    try:
        rating = Rating.objects.get(user__username=player_name)
        return rating
    except ObjectDoesNotExist:
        return None


def update_ratings_for_user_game(player_name, new_elo, game_end_state):
    try:
        # user_id = User.objects.get(username=user_name).id
        # rating_object = Rating.objects.get(pk=user_id)
        rating_object = Rating.objects.get(user__username=player_name)
        # Update the fields
        rating_object.games_played += 1
        if game_end_state == 1:
            rating_object.wins += 1
        elif game_end_state == -1:
            rating_object.losses += 1
        elif game_end_state == 0:
            rating_object.draws = 1

        rating_object.win_rate = (rating_object.wins / rating_object.games_played) * 100
        rating_object.elo = new_elo

        rating_object.save()  # Save the changes to the database
        return True  # Return True if the function executed successfully
    except ObjectDoesNotExist:
        # You may want to log this exception, depending on your use case
        return False  # Return False or appropriate response when the object doesn't exist

