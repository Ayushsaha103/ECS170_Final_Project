
import pygame
import random
import numpy as np
import math
from math_helpers import *
from Constants import *

# this variable adjusts how far ahead the waypoint is of the car
lane_pts_ahead = 14

# waypoints class
class WayPoints():
    # initialization
    def __init__(self, rd):

        self.lanum = 0                  # (initial) lane number to be followed
        l1 = rd.lanes[ rd.lanums[self.lanum][0] ]       # laneline to left of chosen lane
        l2 = rd.lanes[ rd.lanums[self.lanum][1] ]       # laneline to right of chosen lane

        # initial (x,y) coordinate of waypoint
        self.x, self.y = (l1.points[lane_pts_ahead ][0] + l2.points[lane_pts_ahead ][0]) / 2, \
                (l1.points[lane_pts_ahead ][1] + l2.points[lane_pts_ahead ][1]) / 2

    # check if waypoint needs to be updated (occurs if car closes in on waypoint)
    def check_for_update(self, car_pos):
        if distance([self.x, self.y], car_pos) < 5: return True
        return False
    
    # update waypoint position
    def update(self, rd, car):
        # conditionally update the lane which is to be followed
        if random.randint(0,20) == 0:
            if random.randint(0,1) == 0:
                if self.lanum + 2 in rd.lanums:
                    self.lanum += 1
            else:
                if self.lanum - 1 >= 1:
                    self.lanum -= 1
        # get the two surrounding lanelines (l1 & l2) of our chosen lane
        l1 = rd.lanes[ rd.lanums[self.lanum][0] ]
        l2 = rd.lanes[ rd.lanums[self.lanum][1] ]
        my_pos = [self.x, self.y]

        # find closest index of lane lines to current waypoint position
        mindist = 99999; imin = 0
        for i in range(len(l1.points)):
            dist = distance(l1.points[i], my_pos) + distance(l2.points[i], my_pos)
            if dist < mindist:
                mindist = dist
                imin = i

        # choose a next index of lane lines to set waypoint position close to
        target_idx = imin + lane_pts_ahead
        if target_idx >= len(l1.points): target_idx = -1
        self.x, self.y = (l1.points[target_idx ][0] + l2.points[target_idx ][0]) / 2, \
                        (l1.points[target_idx ][1] + l2.points[target_idx ][1]) / 2

    # draw waypoint on screen
    def draw(self, screen, x_trans, y_trans):
        pygame.draw.circle(screen, RED, (self.x + x_trans, self.y + y_trans), 3)  # Draw a single pixel
    