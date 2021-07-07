from entities.coach.coach import BaseCoach

from entities.coach.larc2020 import Coach as LarcCoach
from entities.coach.iron2021 import Coach as IronCoach
from entities.coach.experiment_astar import Coach as AstarCoach

_coach_list = [
    LarcCoach,
    IronCoach,
    AstarCoach
]


COACHES = {c.NAME: c for c in _coach_list}