import math
import random

import pyglet
from pyglet import gl
from pyglet.window import key

# constants:
ROTATION_GAIN = 1
ACCELERATION_GAIN = .25
RAND_ROT_LIMIT = 150
RAND_SPEED_LIMIT = 150
RELOAD_TIME = .3
LASER_SPEED = 500
LASER_AGE = .8
ASTEROID_SIZES = ('big', 'med', 'small')

# global game state goes here:
window = pyglet.window.Window()  # game window
batch = pyglet.graphics.Batch()  # batch with all sprites
objects = []  # all game objects
keys = set()  # currently pressed keys


class SpaceObject:
    """Movable thing in the game

    x, y: position
    radius: radius of the object if we simplify it as circle
    x_speed, y_speed: speed
    rotation: rotation in degrees
    rotation_speed: rotation speed in degrees per sec
    acceleration: forward acceleration
    sprite: pyglet sprite with image
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_speed = 0
        self.y_speed = 0
        self.rotation = 0
        self.rotation_speed = 0
        self.acceleration = 0

        image = pyglet.image.load(self.image())
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self.sprite = pyglet.sprite.Sprite(image, batch=batch)

        self.radius = (image.width + image.height) // 4

        objects.append(self)

    def update_sprite(self):
        self.sprite.rotation = self.rotation
        self.sprite.x = self.x
        self.sprite.y = self.y

    def draw_circle(self):
        draw_circle(self.x, self.y, self.radius)

    def tick(self, dt):
        self.x += dt * self.x_speed
        self.y += dt * self.y_speed
        self.rotation += dt * self.rotation_speed

        rotation_radians = math.radians(self.rotation)
        self.x_speed += dt * self.acceleration * math.sin(rotation_radians)
        self.y_speed += dt * self.acceleration * math.cos(rotation_radians)

        self.x %= window.width
        self.y %= window.height

        self.update_sprite()

    def hit_by_spaceship(self, spaceship):
        # does nothing
        pass

    def hit_by_laser(self, laser):
        # does nothing
        pass

    def delete(self):
        self.sprite.delete()
        objects.remove(self)


class Spaceship(SpaceObject):
    """The playable object

    last_shot: when was last shot fired
    """
    def __init__(self):
        super().__init__(x=window.width // 2,
                         y=window.height // 2)
        self.last_shot = 0

    def image(self):
        return 'images/spaceship.png'

    def handle_keys(self):
        if key.LEFT in keys:
            self.rotation_speed -= ROTATION_GAIN
        if key.RIGHT in keys:
            self.rotation_speed += ROTATION_GAIN
        if key.DOWN in keys:
            self.acceleration -= ACCELERATION_GAIN
        if key.UP in keys:
            self.acceleration += ACCELERATION_GAIN
        if key.SPACE in keys:
            self.attempt_shoot()

    def shoot(self):
        Laser(self)
        self.last_shot = RELOAD_TIME

    def attempt_shoot(self):
        if self.last_shot <= 0:
            self.shoot()

    def check_collisions(self):
        for o in objects:
            if o == self:
                continue
            if overlaps(self, o):
                o.hit_by_spaceship(self)

    def tick(self, dt):
        self.handle_keys()
        super().tick(dt)
        self.check_collisions()
        self.last_shot -= dt


class Laser(SpaceObject):
    """Shot laser. It only last for some time.

    age: how old is this laser (time elapsed from shot)
    """
    def __init__(self, origin):
        super().__init__(origin.x, origin.y)
        self.rotation = origin.rotation
        self.x_speed = origin.x_speed
        self.y_speed = origin.y_speed

        rotation_radians = math.radians(self.rotation)
        self.x_speed += LASER_SPEED * math.sin(rotation_radians)
        self.y_speed += LASER_SPEED * math.cos(rotation_radians)
        self.age = 0

    def image(self):
        return 'images/laser.png'

    def check_collisions(self):
        for o in objects:
            if o == self:
                continue
            if overlaps(self, o):
                o.hit_by_laser(self)

    def tick(self, dt):
        super().tick(dt)
        self.check_collisions()
        self.age += dt
        if self.age > LASER_AGE:
            self.delete()


class Asteroid(SpaceObject):
    """The enemy object"""
    def __init__(self, origin=None):
        if origin:
            self.split_from(origin)
        else:
            self.first()
        self.rotation_speed = random.randint(-RAND_ROT_LIMIT, RAND_ROT_LIMIT)
        self.x_speed = random.randint(-RAND_SPEED_LIMIT, RAND_SPEED_LIMIT)
        self.y_speed = random.randint(-RAND_SPEED_LIMIT, RAND_SPEED_LIMIT)

    def first(self):
        flip = random.randint(0, 1)
        if flip == 1:
            x = window.width // 2
            y = 0
        else:
            x = 0
            y = window.height // 2
        self.size = random.choice(ASTEROID_SIZES)
        super().__init__(x=x, y=y)

    def split_from(self, origin):
        self.size = ASTEROID_SIZES[ASTEROID_SIZES.index(origin.size) + 1]
        super().__init__(x=origin.x, y=origin.y)

    def image(self):
        images = 2
        if self.size == 'big':
            images = 4
        number = random.randint(1, images)
        return 'images/asteroid_{}{}.png'.format(self.size, number)

    def hit_by_spaceship(self, spaceship):
        spaceship.delete()

    def hit_by_laser(self, laser):
        laser.delete()
        self.delete()
        if self.size != ASTEROID_SIZES[-1]:
            Asteroid(self)
            Asteroid(self)


def tick_all_objects(dt):
    """Ticks all objects in our list"""
    for o in objects:
        o.tick(dt)


def draw_circle(x, y, radius):
    iterations = 20
    s = math.sin(2*math.pi / iterations)
    c = math.cos(2*math.pi / iterations)

    dx, dy = radius, 0

    gl.glBegin(gl.GL_LINE_STRIP)
    for i in range(iterations+1):
        gl.glVertex2f(x+dx, y+dy)
        dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    gl.glEnd()


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
            for o in objects:
                o.draw_circle()
            batch.draw()

            # Restore remembered state (this cancels the glTranslatef)
            gl.glPopMatrix()


def key_pressed(sym, mod):
    """Adds key to the keys set"""
    keys.add(sym)


def key_released(sym, mod):
    """Removes key from the keys set"""
    keys.discard(sym)


def distance(a, b, wrap_size):
    """Distance in one direction (x or y)"""
    result = abs(a - b)
    if result > wrap_size / 2:
        result = wrap_size - result
    return result


def overlaps(a, b):
    """Returns true iff two space objects overlap"""
    distance_squared = (distance(a.x, b.x, window.width) ** 2 +
                        distance(a.y, b.y, window.height) ** 2)
    max_distance_squared = (a.radius + b.radius) ** 2
    return distance_squared < max_distance_squared


pyglet.clock.schedule_interval(tick_all_objects, 1/30)

window.push_handlers(
    on_draw=draw_all_objects,
    on_key_press=key_pressed,
    on_key_release=key_released,
)

Spaceship()
Asteroid()
Asteroid()

pyglet.app.run()
