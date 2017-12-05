import math

import pyglet
from pyglet import gl
from pyglet.window import key

# constants:
ROTATION_GAIN = 1
ACCELERATION_GAIN = .25

# global game state goes here:
window = pyglet.window.Window()  # game window
batch = pyglet.graphics.Batch()  # batch with all sprites
objects = []  # all game objects
keys = set()  # currently pressed keys


class Spaceship:
    """Main playable thing in the game

    x, y: position
    x_speed, y_speed: speed
    rotation: rotation in degrees
    rotation_speed: rotation speed in degrees per sec
    sprite: pyglet sprite with image
    """
    def __init__(self):
        self.x = window.width // 2
        self.y = window.height // 2
        self.x_speed = 0
        self.y_speed = 0
        self.rotation = 0
        self.rotation_speed = 0
        self.acceleration = 0

        image = pyglet.image.load('images/spaceship.png')
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch=batch)

        objects.append(self)

    def tick(self, dt):
        if key.LEFT in keys:
            self.rotation_speed -= ROTATION_GAIN
        if key.RIGHT in keys:
            self.rotation_speed += ROTATION_GAIN
        if key.DOWN in keys:
            self.acceleration -= ACCELERATION_GAIN
        if key.UP in keys:
            self.acceleration += ACCELERATION_GAIN

        self.x += dt * self.x_speed
        self.y += dt * self.y_speed
        self.rotation = self.rotation + dt * self.rotation_speed

        rotation_radians = math.radians(self.rotation)
        self.x_speed += dt * self.acceleration * math.sin(rotation_radians)
        self.y_speed += dt * self.acceleration * math.cos(rotation_radians)

        self.x %= window.width
        self.y %= window.height

        self.sprite.rotation = self.rotation
        self.sprite.x = self.x
        self.sprite.y = self.y


def tick_all_objects(dt):
    """Ticks all objects in our list"""
    for o in objects:
        o.tick(dt)


def draw_all_objects():
    """Draws our batch"""
    window.clear()
    for x_offset in (-window.width, 0, window.width):
        for y_offset in (-window.height, 0, window.height):
            # Remember the current state
            gl.glPushMatrix()
            # Move everything drawn from now on by (x_offset, y_offset, 0)
            gl.glTranslatef(x_offset, y_offset, 0)

            # Draw
            batch.draw()

            # Restore remembered state (this cancels the glTranslatef)
            gl.glPopMatrix()


def key_pressed(sym, mod):
    """Adds key to the keys set"""
    keys.add(sym)


def key_released(sym, mod):
    """Removes key from the keys set"""
    keys.discard(sym)


pyglet.clock.schedule_interval(tick_all_objects, 1/30)

window.push_handlers(
    on_draw=draw_all_objects,
    on_key_press=key_pressed,
    on_key_release=key_released,
)

spaceship = Spaceship()

pyglet.app.run()
