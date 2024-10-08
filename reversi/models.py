from django.db import models
from django.contrib.auth.models import User
from reversi.game_logic import get_scores_from_string


# Create your models here.
class GameDB(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    player1 = models.CharField(max_length=24)
    player2 = models.CharField(max_length=24)
    next_player = models.IntegerField(default=1)
    score_p1 = models.IntegerField(default=0)
    score_p2 = models.IntegerField(default=0)
    game_over = models.BooleanField(default=False)
    def __str__(self):
        return f"Game ID: {self.id} by user [{self.user.username}] between [{self.player1}] and [{self.player2}]"


class GameState(models.Model):
    game_id = models.ForeignKey(GameDB, on_delete=models.CASCADE, related_name="game")
    #prev_state = models.ForeignKey("self", null=True, on_delete=models.CASCADE, related_name="prev_state")
    #prev_state = models.IntegerField(default=0, null=True)
    board = models.CharField(max_length=64)

    def __str__(self):
        return f"Game ID: {self.game_id.id}, State ID: {self.id} Scores: {get_scores_from_string(self.board)}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="elo_user")
    elo = models.IntegerField(default=1000)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    win_rate = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.username