from entities.coach.coach import BaseCoach
from entities import plays

class Coach(BaseCoach):
    NAME = "LARC_2021"
    def __init__(self, match):
        super().__init__(match)

        self.playbook = plays.Playbook(self)

        main_play = plays.larc2021.MainPlay(self)
        
        self.playbook.add_play(main_play)
        self.playbook.set_play(main_play)
    
    def get_positions(self, foul, team_color):
        return None

    def decide (self):
        self.playbook.update()

    