# simulator/game_processing.py
from reversi.models import GameDB
from reversi.game_logic import *
from reversi.data_layer import *


def process_game(game_data):
    # get players
    user = game_data['user']
    ai1_name = game_data['ai1_name']
    ai2_name = game_data['ai2_name']
    player1, player2 = (ai1_name, ai2_name) if random.choice([True, False]) else (ai2_name, ai1_name)

    # create game
    new_game = Game(player1, player2, "auto-match", board=None)
    scores = get_scores(new_game.board)
    game_db_entry = GameDB(user=user, score_p1=scores[0], score_p2=scores[1], player1=player1, player2=player2, next_player=1, game_over=False)
    game_db_entry.save()
    game_id = game_db_entry.id

    save_gamestate_db(new_game.board, game_id, 0)
    board, player1_name, player2_name, next_player, state_id = load_gamestate_db(game_id, user)

    game_over = False

    # Setup players
    player1_maker = AiMachinePlayerMaker(player1_name, 1)
    player1 = player1_maker.get_player()
    player2_maker = AiMachinePlayerMaker(player2_name, 2)
    player2 = player2_maker.get_player()

    while not game_over:
        next_player_instance = player1 if next_player == 1 else player2
        next_move, board = machine_move(board, next_player_instance)
        next_player = get_opponent(next_player)
        save_gamestate_db(board, game_id, state_id)

        if len(get_possible_moves(board, next_player)) == 0:
            next_player = get_opponent(next_player)
            if len(get_possible_moves(board, next_player)) == 0:
                game_over = True

    scores = get_scores(board)
    winner_role = 0 if scores[0] == scores[1] else (1 if scores[0] > scores[1] else 2)
    message = "It's a draw!" if winner_role == 0 else f"Player{winner_role} ({player1_name if winner_role == 1 else player2_name}) has won!"

    save_game_db(game_id, scores[0], scores[1], winner_role, game_over)

    # Calculate elo rating
    elo_player1 = get_rating_for_user(player1_name)
    if elo_player1 is None:
        create_base_rating_for_user(player1_name)
        elo_player1 = get_rating_for_user(player1_name)
    elo_player2 = get_rating_for_user(player2_name)
    if elo_player2 is None:
        create_base_rating_for_user(player2_name)
        elo_player2 = get_rating_for_user(player1_name)

    new_elo_p1 = max(1, int(elo_player1 + (scores[0] - scores[1]) * (elo_player2/elo_player1)))
    new_elo_p2 = max(1, int(elo_player2 + (scores[1] - scores[0]) * (elo_player1/elo_player2)))

    update_ratings_for_user_game(player1_name, new_elo_p1, 1 if winner_role == 1 else -1)
    update_ratings_for_user_game(player2_name, new_elo_p2, 1 if winner_role == 2 else -1)

    print(f"### Game ended, {message}!")
    print(f"Final Score: {scores[0]} - {scores[1]}")
    # print in columns
    print(f"{'':<20} {player1_name:<20}{player2_name:<20}")
    print(f"{'Curr. ELO:':<20} {elo_player1:<20}{elo_player2:<20}")
    print(f"{'New ELO:':<20} {new_elo_p1:<20}{new_elo_p2:<20}")

    print(f"Current ELO-ratings: Player1 ({player1_name}): {elo_player1}, Player2 ({player2_name}): {elo_player2}")
    print(f"New ELO-ratings: Player1 ({player1_name}): {new_elo_p1}, Player2 ({player2_name}): {new_elo_p2}")

