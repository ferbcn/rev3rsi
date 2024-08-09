class Levels:
    def __init__(self):
        self.game_levels = [('', 'dumb'), ('', 'random'), ('', 'greedy'), ('', 'greedy-plus'), ('', 'mini-max')]
        self.admin_game_levels = [('', 'easy'), ('', 'medium'), ('', 'hard'), ('', 'harder'),
                             ('', 'P1-Draw'), ('', 'P1-Win'), ('', 'P1-Lose'), ('', 'P2-Win'), ('', 'P2-Lose'),
                             ('', 'JumpCheck')]

    def get_levels(self):
        return self.game_levels

    def get_admin_levels(self):
        levels = self.get_levels()
        return levels + self.admin_game_levels


