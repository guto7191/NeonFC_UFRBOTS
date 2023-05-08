import numpy as np
from algorithms.limit_cycle import LimitCycle
import math
from controller.PID_control import PID_W_control, PID_control
from strategy.BaseStrategy import Strategy
from strategy.utils.player_playbook import PlayerPlay, PlayerPlaybook, OnInsideBox, OnNextTo, AndTransition
from commons.math import distance_between_points


class MainPlay(PlayerPlay):
    def __init__(self, match, robot):
        # super().__init__(match, "Main_Attacker", controller=PID_W_control)
        super().__init__(match, robot)

    def get_name(self):
        return f"<{self.robot.get_name()} Main Attacker Planning>"

    def start_up(self):
        super().start_up()
        controller = PID_W_control
        self.robot.strategy.controller = controller(self.robot)

    def start(self):
        self.limit_cycle = LimitCycle(self.match)
        self.field_w, self.field_h = self.match.game.field.get_dimensions()

    def update(self):
        ball = (self.match.ball.x, self.match.ball.y)
        robot = (self.robot.x, self.robot.y)

        if distance_between_points(ball, robot) < 0.1 and not self.behind_ball():
            desired = (1.5, 0.65)
        else:
            self.limit_cycle.set_target(ball)
            self.limit_cycle.add_obstacle(self.get_virtual_obstacle(ball))
            desired = self.limit_cycle.compute(self.robot, fitness=20)

        return desired

    def get_virtual_obstacle(self, target):
        '''
        - m:    angle of the line perpendicular to the line between the ball and
                the center of the goal
        - p:    distance of the virtual obstacles to the ball / radius of the virtual obstacle
        - vo:   virtual obstacle
        - j:    this is the angle between the ball and the center of the goal
        - m:    the normal angle perpendicular to j
        - r:    radius of the ball
        '''
        aim_point = [self.field_w, self.field_h / 2]

        j = math.atan2(aim_point[1] - target[1], aim_point[0] - target[0])
        m = j + math.pi / 2
        p = 0.1

        r = .0427 / 2

        '''
        the terms r*cos(j) and r*sin(j) are subtracted to move
        the center of the obstacles behind the ball instead of its center
        '''
        if self.robot.y < math.tan(j) * (self.robot.x - target[0]) + target[1]:
            virtual_obstacle = (
                target[0] - p * math.cos(m) - r * math.cos(j),
                target[1] - p * math.sin(m) - r * math.sin(j),
                p,
                1
            )
        else:
            virtual_obstacle = (
                target[0] + p * math.cos(m) - r * math.cos(j),
                target[1] + p * math.sin(m) - r * math.sin(j),
                p,
                -1
            )

        if self.behind_ball():
            virtual_obstacle = (
                target[0] - p * math.cos(m) - r * math.cos(j),
                target[1] - p * math.sin(m) - r * math.sin(j),
                2 * p,
                np.sign(target[1] - p * math.sin(m) - r * math.sin(j) - 0.65)
            )

        return virtual_obstacle

    def behind_ball(self):
        # Convert input to numpy arrays for easy calculation
        point_on_line = np.array((self.match.ball.x, self.match.ball.y))
        point_on_normal = np.array((1.5, .65))
        point_to_check = np.array((self.robot.x, self.robot.y))

        # Calculate the normal vector of the line
        normal = point_on_normal - point_on_line

        # Calculate the vector from the point on the line to the point to check
        vector_to_check = point_to_check - point_on_line

        # Calculate the dot product of the normal vector and the vector to check
        dot_product = np.dot(normal, vector_to_check)

        # Check the sign of the dot product to determine if the point is to the right or left of the line
        return dot_product > 0


class WingPlay(PlayerPlay):
    def __init__(self, match, robot):
        super().__init__(match, robot)

        self.BALL_Y_MIN = 0.05
        self.BALL_Y_MAX = 1.25

    def get_name(self):
        return f"<{self.robot.get_name()} Wing Attacker Planning>"

    def start_up(self):
        super().start_up()
        controller = PID_W_control
        self.robot.strategy.controller = controller(self.robot)

    def start(self):
        self.limit_cycle = LimitCycle(self.match)
        self.field_w, self.field_h = self.match.game.field.get_dimensions()

    def update(self):
        target = [self.match.ball.x, self.match.ball.y]
        robot = (self.robot.x, self.robot.y)

        target[1] = min(self.BALL_Y_MAX, target[1])
        target[1] = max(self.BALL_Y_MIN, target[1])

        aim_point = [self.field_w, self.BALL_Y_MAX] if target[1] > .65 else [self.field_w, self.BALL_Y_MIN]

        if distance_between_points(target, robot) < 0.1 and not self.behind_ball(aim_point):
            desired = aim_point
        else:
            self.limit_cycle.set_target(target)
            self.limit_cycle.add_obstacle(self.get_virtual_obstacle(target))
            desired = self.limit_cycle.compute(self.robot, fitness=20)

        return desired

    def get_virtual_obstacle(self, target):
        """
        - m:    angle of the line perpendicular to the line between the ball and
                the center of the goal
        - p:    distance of the virtual obstacles to the ball / radius of the virtual obstacle
        - vo:   virtual obstacle
        - j:    this is the angle between the ball and the center of the goal
        - m:    the normal angle perpendicular to j
        - r:    radius of the ball
        """
        aim_point = [self.field_w, self.BALL_Y_MAX] if target[1] > .65 else [self.field_w, self.BALL_Y_MIN]

        j = math.atan2(aim_point[1] - target[1], aim_point[0] - target[0])
        m = j + math.pi / 2
        p = 0.1

        r = .0427 / 2

        '''
        the terms r*cos(j) and r*sin(j) are subtracted to move
        the center of the obstacles behind the ball instead of its center
        '''
        if self.robot.y < math.tan(j) * (self.robot.x - target[0]) + target[1]:
            virtual_obstacle = (
                target[0] - p * math.cos(m) - r * math.cos(j),
                target[1] - p * math.sin(m) - r * math.sin(j),
                p,
                1
            )
        else:
            virtual_obstacle = (
                target[0] + p * math.cos(m) - r * math.cos(j),
                target[1] + p * math.sin(m) - r * math.sin(j),
                p,
                -1
            )

        return virtual_obstacle

    def behind_ball(self, aim_point):
        # Convert input to numpy arrays for easy calculation
        point_on_line = np.array((self.match.ball.x, self.match.ball.y))
        point_on_normal = np.array(aim_point)
        point_to_check = np.array((self.robot.x, self.robot.y))

        # Calculate the normal vector of the line
        normal = point_on_normal - point_on_line

        # Calculate the vector from the point on the line to the point to check
        vector_to_check = point_to_check - point_on_line

        # Calculate the dot product of the normal vector and the vector to check
        dot_product = np.dot(normal, vector_to_check)

        # Check the sign of the dot product to determine if the point is to the right or left of the line
        return dot_product > 0


class CrossPlay(PlayerPlay):
    def __init__(self, match, robot):
        super().__init__(match, robot)

    def get_name(self):
        return f"<{self.robot.get_name()} Cross Planning>"

    def start_up(self):
        super().start_up()
        controller = PID_W_control
        controller_kwargs = {'V_MAX': 0, 'V_MIN': 0, 'W_MAX': 100000000000}
        self.robot.strategy.controller = controller(self.robot, **controller_kwargs)

    def update(self):
        if self.robot.y > .65:
            ang_diff = self.robot.theta - math.pi/2.1
        else:
            ang_diff = self.robot.theta + math.pi/2.1

        x = self.robot.x + 0.5*math.cos(ang_diff)
        y = self.robot.y + 0.5*math.sin(ang_diff)

        return x, y

    def start(self):
        pass


class Wait(PlayerPlay):
    def __init__(self, match, robot):
        super().__init__(match, robot)

    def get_name(self):
        return f"<{self.robot.get_name()} Position Planning>"

    def start_up(self):
        super().start_up()
        controller = PID_control
        controller_kwargs={'V_MIN': 0, 'K_RHO': 75}
        self.robot.strategy.controller = controller(self.robot, **controller_kwargs)

    def update(self):
        print(self.position())
        return self.position()

    def start(self):
        pass

    def position(self):
        a = (.35, 1.1)
        b = (.35, 0.2)

        c = (self.robot.x, self.robot.y)
        d = [(r.x, r.y) for r in self.match.robots if r.strategy.name == "Shadow_Attacker"][0]

        # Calculate the distances between each robot and each fixed point
        distance_c_a = math.sqrt((c[0] - a[0]) ** 2 + (c[1] - a[1]) ** 2)
        distance_c_b = math.sqrt((c[0] - b[0]) ** 2 + (c[1] - b[1]) ** 2)
        distance_d_a = math.sqrt((d[0] - a[0]) ** 2 + (d[1] - a[1]) ** 2)
        distance_d_b = math.sqrt((d[0] - b[0]) ** 2 + (d[1] - b[1]) ** 2)

        # Assign the robots to the closer fixed point
        if distance_c_a + distance_d_b < distance_c_b + distance_d_a:
            return a
        else:
            return b


class LookAtBall(PlayerPlay):
    def __init__(self, match, robot):
        super().__init__(match, robot)

    def get_name(self):
        return f"<{self.robot.get_name()} Looking at the ball>"

    def start_up(self):
        super().start_up()
        controller = PID_W_control
        controller_kwargs = {'V_MIN': 0, 'V_MAX': 0}
        self.robot.strategy.controller = controller(self.robot, **controller_kwargs)

    def update(self):
        return self.match.ball.x, self.match.ball.y

    def start(self):
        pass


class MainStriker(Strategy):
    def __init__(self, match, name="Main_Attacker"):
        super().__init__(match, name, controller=PID_W_control)

        self.playerbook = None

    def start(self, robot=None):
        super().start(robot=robot)

        field_dim = self.match.game.field.get_dimensions()

        # Criando Player Playbook: A maquina de estados do jogador
        self.playerbook = PlayerPlaybook(self.match.coach, self.robot)

        main = MainPlay(self.match, self.robot)
        main.start()
        wing = WingPlay(self.match, self.robot)
        wing.start()
        cross = CrossPlay(self.match, self.robot)
        cross.start()
        defensive = Wait(self.match, self.robot)
        defensive.start()
        angle = LookAtBall(self.match, self.robot)

        self.playerbook.add_play(main)
        self.playerbook.add_play(wing)
        self.playerbook.add_play(cross)
        self.playerbook.add_play(defensive)
        self.playerbook.add_play(angle)

        on_wing = OnInsideBox(self.match, [0, 0.3, 1.5, 0.7], True)
        on_cross_region = OnInsideBox(self.match, [1.4, 0, .15, 1.3])
        on_near_ball = OnNextTo(self.match.ball, self.robot, 0.1)
        on_defensive_box = OnInsideBox(self.match, [-.2, .3, .35, .7])
        on_positon_1 = OnNextTo([.35, 1.1], self.robot, 0.1)
        on_positon_2 = OnNextTo([.35, .2], self.robot, 0.1)

        main.add_transition(on_wing, wing)
        main.add_transition(AndTransition([on_near_ball, on_cross_region, on_wing]), cross)
        main.add_transition(on_defensive_box, defensive)

        main.add_transition(AndTransition([on_positon_1, on_defensive_box]), angle)
        main.add_transition(AndTransition([on_positon_2, on_defensive_box]), angle)

        # Estado inicial
        self.playerbook.set_play(main)

    def decide(self):
        res = self.playerbook.update()
        return res
