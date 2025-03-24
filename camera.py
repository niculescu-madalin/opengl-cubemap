from OpenGL.GL import *
import numpy as np
import math


class FirstPersonCamera:
    def __init__(self, position=[0, 0, 0], yaw=0, pitch=0):
        self.position = np.array(position, dtype='float32')
        self.yaw = yaw
        self.pitch = pitch
        self.speed = 0.2
        self.mouse_sensitivity = 0.2
        self.move_forward = False
        self.move_backward = False
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

    def update(self):
        # Calculate right vector from yaw and pitch
        right = np.array([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ])
        right = right / np.linalg.norm(right)

        # Calculate forward vector
        forward = np.cross(right, [0, 1, 0])
        forward = forward / np.linalg.norm(forward)

        # Calculate up vector
        up = np.cross(forward, right)

        # Movement
        if self.move_forward:
            self.position -= forward * self.speed
        if self.move_backward:
            self.position += forward * self.speed
        if self.move_left:
            self.position -= right * self.speed
        if self.move_right:
            self.position += right * self.speed
        if self.move_up:
            self.position += up * self.speed
        if self.move_down:
            self.position -= up * self.speed

        # Keep camera above ground
        if self.position[1] < 0.5:
            self.position[1] = 0.5

    def look(self):
        glRotatef(-self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glTranslatef(-self.position[0], -self.position[1], -self.position[2])