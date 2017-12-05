import pyglet
from pyglet.window import key


# constants
ACCELERATION = 5


# global game state goes here:
window = pyglet.window.Window()  # game window
batch = pyglet.graphics.Batch()  # batch with all sprites
objects = []  # all game objects
keys = set()  # currently pressed keys


class Spaceship:
    """Main playable thing in the game

    x, y: position
    x_speed, y_speed: speed
    rotation: rotation in degreees
    sprite: pyglet sprite with image
    """
    def __init__(self):
        self.x = window.width // 2
        self.y = window.height // 2
        self.x_speed = 0
        self.y_speed = 0

        image = pyglet.image.load('images/spaceship.png')
        self.sprite = pyglet.sprite.Sprite(image, batch=batch)

        objects.append(self)

    def tick(self, delta):
        if key.LEFT in keys:
            self.x_speed -= 1
        if key.RIGHT in keys:
            self.x_speed += 1
        if key.DOWN in keys:
            self.y_speed -= 1
        if key.UP in keys:
            self.y_speed += 1

        self.x += delta * self.x_speed * ACCELERATION
        self.y += delta * self.y_speed * ACCELERATION
        print(self.x_speed, self.y_speed)

        self.sprite.x = self.x - self.sprite.width // 2
        self.sprite.y = self.y - self.sprite.height // 2


def tick_all_objects(delta):
    """Ticks all objects in our list"""
    for o in objects:
        o.tick(delta)


def draw_all_objects():
    """Draws our batch"""
    window.clear()
    batch.draw()


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
