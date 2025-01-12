# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 12:38:54 2017

@author: cz
"""

import sys
import math

class State():
    def __init__(self, x, y, theta, robot = None):
        self.x = x
        self.y = y
        self.vxp = 0 # vx prime, updated in controller
        self.vyp = 0 # vy prime, updated in controller
        self.theta = theta
        self.robot = robot



    def propagate(self, control):
        if self.robot == None:
            sys.exit("State: attribute robot is None")
        dt = self.robot.scene.dt
        l = self.robot.l
        v1, v2 = control()
        self.x += math.cos(self.theta) * dt / 2 * (v1 + v2)
        self.y += math.sin(self.theta) * dt / 2 * (v1 + v2)
        self.theta += 1 / l * dt * (v2 - v1)


    def transform(self):
        # For feedback linearization
        self.xp = self.x
        self.yp = self.y
        self.thetap = self.theta

    def distancepTo(self, other):
        dxp = self.xp - other.xp
        dyp = self.yp - other.yp
        return (dxp**2 + dyp**2)**0.5







