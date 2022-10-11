import algorithms
import math
import controller
from controller.PID import Robot_PID
from controller.simple_LQR import TwoSidesLQR, SimpleLQR
from strategy.BaseStrategy import Strategy
from commons.math import unit_vector
import json
import numpy as np

class Goalkeeper(Strategy):
    def __init__(self, match, plot_field=False):
        super().__init__(match, "asdgasad", controller=TwoSidesLQR)

    def start(self, robot=None):
        super().start(robot=robot)
        self.field = algorithms.fields.PotentialField(
            self.match,
            name="{}|FieldBehaviour".format(self.__class__)
        )

        self.calm = algorithms.fields.PotentialField(
            self.match,
            name="{}|CalmBehaviour".format(self.__class__)
        )

        self.edge = algorithms.fields.PotentialField(
            self.match,
            name="{}|EdgeBehaviour".format(self.__class__)
        )

        self.test = algorithms.fields.PotentialField(
            self.match,
            name="{}|TestBehaviour".format(self.__class__)
        )

        def set_boundaries(m):
            x = 0.04
            g_hgr = 0.83
            g_lwr = 0.45

            x_rob = x + 0.075/2
            if m.ball.vx == 0:
                if m.ball.y > g_hgr:
                    y = g_hgr
                elif m.ball.y < g_lwr:
                    y = g_lwr
                else:
                    y = m.ball.y
                return (x, y)
            
            y = (m.ball.vy/m.ball.vx)*(x_rob-m.ball.x) + m.ball.y
            #y = m.ball.y + m.ball.vy*(4/30)

            mp = (0.65+m.ball.y)/2

            if m.ball.y > g_hgr:
                y = g_hgr
            elif m.ball.y < g_lwr:
                y = g_lwr
            else:
                if y > g_hgr or y < g_lwr:
                    if m.ball.y < 0.65:
                        y = ((mp-m.ball.y)/m.ball.x)*(x_rob-m.ball.x) + m.ball.y
                    elif m.ball.y > 0.65:
                        y = ((m.ball.y-mp)/m.ball.x)*(x_rob-m.ball.x) + m.ball.y
            return x, y

        def edging_point(m):
            x = 0.045
            g_hgr = 0.87
            g_lwr = 0.5

            if m.ball.y > g_hgr:
                y = g_hgr
            elif m.ball.y < g_lwr:
                y = g_lwr
            else:
                y = m.ball.y

            y -= .15

            return x, y

        #campo potencial para seguir a posição/projeção da bola
        self.field.add_field(
            algorithms.fields.LineField(
                self.match,
                target = edging_point,
                theta = 0,
                line_size = 1.5,
                line_dist = .9,
                decay = lambda x: x**2,
                multiplier = 0.5,
            )
        )

        self.test.add_field(
            algorithms.fields.PointField(
                self.match,
                target = edging_point,
                radius = 0.8,
                decay = lambda x: x**7,
                multiplier = 0.25
            )
        )


    def reset(self, robot=None):
        super().reset()
        if robot:
            self.start(robot)


    def decide(self):

        behaviour = None

        # if self.match.ball.x > 1.2:
        #     behaviour = self.calm
        # elif self.match.ball.x < 0.15:
        #     behaviour = self.edge
        # else:

        behaviour = self.field
        # print(behaviour.field_childrens[0].target(self.match))

        # print(f"{self.match.ball.y=}")
        print(self.robot.x, self.robot.y)

        return behaviour.compute([self.robot.x, self.robot.y])
