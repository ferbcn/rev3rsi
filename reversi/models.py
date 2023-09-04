from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class GameDB(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    player1 = models.CharField(max_length=24)
    player2 = models.CharField(max_length=24)
    next_player = models.IntegerField(default=1)
    score_p1 = models.IntegerField(default=0)
    score_p2 = models.IntegerField(default=0)
    game_over = models.BooleanField(default=False)


class GameState(models.Model):
    game_id = models.ForeignKey(GameDB, on_delete=models.CASCADE, related_name="game")
    #prev_state = models.ForeignKey("self", null=True, on_delete=models.CASCADE, related_name="prev_state")
    prev_state = models.IntegerField(default=0, null=True)
    board = models.CharField(max_length=64)
