from django.contrib import admin

from .models import GameDB, GameState

# Register your models here.
admin.site.register(GameDB)
admin.site.register(GameState)
