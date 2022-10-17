import math
import numpy as np
from entities.visualization import Writer, Parameter
import time
from collections import deque

def angle_adjustment(angle):
        """Adjust angle of the robot when objective is "behind" the robot"""
        phi = angle % math.radians(360)
        if phi > math.radians(180):
            phi = phi - math.radians(360)

        return phi

class PID_control(object):
    def __init__(self, robot, default_fps=60):
        self.vision = robot.game.vision
        self.field_w, self.field_h = robot.game.field.get_dimensions()
        self.robot = robot
        self.desired = [0, 0]

        self.l = self.robot.dimensions.get('L')/2 # half_distance_between_robot_wheels
        self.R = self.robot.dimensions.get('R')   # radius of the wheel

        self.default_fps = default_fps
        self.dt = 1/self.default_fps

        # Control params
        self.K_RHO = .05 # Linear speed gain

        # PID of angular speed
        self.KP = -350 # Parameter(-130, 'pid_tuner', 'kp') # Proportional gain of w (angular speed), respecting the stability condition: K_RHO > 0 and KP > K_RHO
        self.KI = 0 # Parameter(0, 'pid_tuner', 'ki') # Integral gain of w
        self.KD = 0# Parameter(-7.5, 'pid_tuner', 'kd') # Derivative gain of w

        # PID params for error
        self.dif_alpha = 0 # diferential param
        self.int_alpha = 0 # integral param
        self.alpha_old = 0 # stores previous iteration alpha

        # Max speeds for the robot
        self.v_max = 150 # 40 # linear speed
        self.w_max = 550 # math.radians(7200) # angular speed rad/

        self.v_min = 80
        self.control_linear_speed = False
        self.lp = [0, 0]

        # self.pid_writer = Writer('pid',
        #                          {'kp': 'FLOAT',
        #                           'ki': 'FLOAT',
        #                           'kd': 'FLOAT',
        #                           'set_point': 'FLOAT',
        #                           'error': 'FLOAT',
        #                           'w': 'FLOAT'
        #                           })
        self.robot_writer = Writer('robot',
                                   {'x': 'FLOAT',
                                    'y': 'FLOAT'})
    
    def set_desired(self, vector):
        self.desired = vector

    def _update_fps(self):
        if self.vision._fps > 0: 
            self.dt = 1/self.vision._fps
        else:
            self.dt = 1/self.default_fps

    def update(self):
        # Params calculation
        # Feedback errors
        D_x = self.desired[0] - self.robot.x
        D_y = self.desired[1] - self.robot.y

        # RHO distance of the robot to the objective
        rhox = self.robot.x - self.lp[0]
        rhoy = self.robot.y - self.lp[1]
        rho = math.sqrt((rhox**2 + rhoy**2))

        # GAMMA robot's position angle to the objetive
        gamma = angle_adjustment(math.atan2(D_y, D_x))

        # ALPHA angle between the front of the robot and the objective
        alpha = angle_adjustment(gamma - self.robot.theta)


        """Calculate the parameters of PID control"""
        self._update_fps()
        self.dif_alpha = (alpha - self.alpha_old) / self.dt # Difentential of alpha
        self.int_alpha = self.int_alpha + alpha

        """Linear speed (v)"""
        v = min(self.v_min + self.K_RHO*rho, self.v_max) if self.control_linear_speed else self.v_max

        """Objective behind the robot"""
        # if(abs(alpha) > math.pi/2):
        #     v = -v
        #     alpha = angle_adjustment(alpha - math.pi)

        """Angular speed (w)"""
        w = self.KP * alpha + self.KI * self.int_alpha + self.KD * self.dif_alpha
        w = np.sign(w) * min(abs(w), self.w_max)
        
        self.alpha_old = alpha

        """Wheel power calculation"""
        pwr_left = (2 * v - w * self.l)/2 * self.R
        pwr_right = (2 * v + w * self.l)/2 * self.R

        # self.pid_writer.write([self.KP, self.KI, self.KD, gamma, alpha, w])
        self.robot_writer.write([self.robot.x, self.robot.y])

        # print(f"{v=}\n{w=}")

        return v, w
        # return pwr_left * 1000, pwr_right * 1000
