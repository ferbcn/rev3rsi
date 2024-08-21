class Levels:
    def __init__(self):
        self.game_levels = [('', 'first'), ('', 'last'), ('', 'random'), ('', 'worst'),
                            ('', 'greedy'), ('', 'greedy-plus'),
                            ('', 'mini-max'), ('', 'mini-max-2s'), ('', 'mini-max-3s')]
        self.admin_game_levels = (self.game_levels +
                                  [('', 'P1-Draw'), ('', 'P1-Win'), ('', 'P1-Lose'), ('', 'P2-Win'), ('', 'P2-Lose'),
                                    ('', 'JumpCheck')])

    def get_levels(self):
        return self.game_levels

    def get_admin_levels(self):
        levels = self.get_levels()
        return levels + self.admin_game_levels


