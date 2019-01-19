import pyglet
from pyglet import font
from pyglet.gl import glEnable, glBindTexture, glPushAttrib, GL_COLOR_BUFFER_BIT, GL_BLEND, glTexParameteri, \
    GL_TEXTURE_MAG_FILTER, GL_NEAREST
from pyglet.text import Label

font.add_file("./data/fonts/PressStart2P-Regular.ttf")


class SpeechBubble(object):

    def __init__(self, x, y, message):
        image_paths = [
            "./data/images/text_bubble/bottom.png",
            "./data/images/text_bubble/bottom_left.png",
            "./data/images/text_bubble/bottom_right.png",
            "./data/images/text_bubble/left.png",
            "./data/images/text_bubble/right.png",
            "./data/images/text_bubble/top.png",
            "./data/images/text_bubble/top_left.png",
            "./data/images/text_bubble/top_right.png",
            "./data/images/text_bubble/white_pixel.png"
        ]
        b, bl, br, l, r, t, tl, tr, wp = map(pyglet.image.load, image_paths)

        max_length = 450
        width = min(len(message) * 18, max_length)
        height = 20 * (len(message) * 22 // max_length + 1)

        self.label = Label(text=message, font_name='Press Start 2P', font_size=14, x=x + 40, y=y + 40,
                           color=(0, 0, 0, 255), width=max_length, height=height, multiline=(height > 1),
                           anchor_x='left', anchor_y='bottom')

        self.top_left = pyglet.sprite.Sprite(img=tl, x=x + 0, y=y + 40 + height)
        self.bottom_left = pyglet.sprite.Sprite(img=bl, x=x + 0, y=y + 0)

        self.top = pyglet.sprite.Sprite(img=t, x=x + 40, y=y + 40 + height)
        self.top.update(scale_x=width / 4)
        self.bottom = pyglet.sprite.Sprite(img=b, x=x + 40, y=y + 0)
        self.bottom.update(scale_x=width / 4)

        self.top_right = pyglet.sprite.Sprite(img=tr, x=x + 40 + width, y=y + 40 + height)
        self.bottom_right = pyglet.sprite.Sprite(img=br, x=x + 40 + width, y=y + 0)

        self.right = pyglet.sprite.Sprite(img=r, x=x + 40 + width, y=y + 40)
        self.right.update(scale_y=height / 4)
        self.left = pyglet.sprite.Sprite(img=l, x=x + 0, y=y + 40)
        self.left.update(scale_y=height / 4)

        self.white_pixel = pyglet.sprite.Sprite(img=wp, x=x + 40, y=y + 40)
        self.white_pixel.update(scale_x=width, scale_y=height)

    def draw(self):
        self.bottom.draw()
        self.bottom_left.draw()
        self.bottom_right.draw()
        self.left.draw()
        self.right.draw()
        self.top_right.draw()
        self.top_left.draw()
        self.top.draw()
        self.white_pixel.draw()
        self.label.draw()


if __name__ == "__main__":
    window = pyglet.window.Window()

    guy_image = pyglet.image.load("./data/images/guymouthshapes/AHH.png")
    glEnable(guy_image.texture.target)
    glBindTexture(guy_image.texture.target, guy_image.texture.id)
    glPushAttrib(GL_COLOR_BUFFER_BIT)
    glEnable(GL_BLEND)
    glTexParameteri(guy_image.texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    guy = pyglet.sprite.Sprite(img=guy_image, x=15, y=10)

    guy.update(scale_x=4, scale_y=4)

    bubbles = [
        # SpeechBubble(30, 350, "Hello, World!"),
        # SpeechBubble(30, 260, "Wow this is a longer one!"),
        # SpeechBubble(30, 170, "short!"),
        SpeechBubble(80, 40, "Bananas")
    ]


    @window.event
    def on_draw():
        window.clear()
        guy.draw()
        for b in bubbles:
            b.draw()


    pyglet.app.run()
