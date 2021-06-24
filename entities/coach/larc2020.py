import algorithms
import strategy
import math
from commons.math import angular_speed, speed, rotate_via_numpy, unit_vector
import json

class Coach(object):
    def __init__(self, match):
        self.match = match
        self.constraints = [
            #estratégia - função eleitora - prioridade
            (strategy.larc2020.GoalKeeper(self.match), self.elect_goalkeeper, 0),
            (strategy.larc2020.Attacker(self.match), self.elect_attacker, 0),
            (strategy.larc2020.MidFielder(self.match), self.elect_midfielder, 0)
        ]
        self.positions = json.loads(open('foul_placements.json', 'r').read())
    
    def decide (self):
        robots = [r.robot_id for r in self.match.robots]
        for strategy, fit_fuction, priority in self.constraints:
            elected = -1
            best_fit = -99999
            for robot_id in robots:
                robot_fit = fit_fuction(self.match.robots[robot_id])
                if (robot_fit > best_fit):
                    best_fit = robot_fit
                    elected = robot_id
            if self.match.robots[elected].strategy is None:
                self.match.robots[elected].strategy = strategy
            elif self.match.robots[elected].strategy.name != strategy.name:
                self.match.robots[elected].strategy = strategy
                self.match.robots[elected].start()
            robots.remove(elected)

    def get_positions(self, foul, team_color):
        foul = self.positions.get(foul)
        replacements = foul.get(team_color, 0)
        if replacements == 0:
            replacements = foul.get("POSITIONS")
        return replacements

    def elect_attacker(self, robot):
        dist_to_ball = math.sqrt(
            (robot.x - self.match.ball.x)**2 + (robot.y - self.match.ball.y)**2
        )
        return 1000 - dist_to_ball

    def elect_goalkeeper(self, robot):
        dist_to_goal = math.sqrt(
            (robot.x - 0)**2 + (robot.y - 0.65)**2
        )
        return 1000 - dist_to_goal

    def elect_midfielder(self, robot):
        return 1