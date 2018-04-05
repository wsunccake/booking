import string
from random import randint, choices
from PIL import Image, ImageDraw, ImageFont


class Rect(object):
    def __init__(self):
        self.size = (randint(5, 21), randint(5, 21))
        self.location = (randint(1, 199), randint(1, 59))
        self.luoverlay = True if randint(1, 10) > 6 else False
        self.rdoverlay = False if self.luoverlay else True if randint(1, 10) > 8 else False
        self.lucolor = 0 if randint(0, 1) else 255
        self.rdcolor = 0 if self.lucolor == 255 else 255
        self.ludrawn = False
        self.rddrawn = False
        self.pattern = randint(0, 1)

    def draw(self, image, overlay):
        if (overlay or not self.luoverlay) and not self.ludrawn:
            self.ludrawn = True
            stp = self.location
            transparent = int(255 * 0.45 if self.lucolor == 0 else 255 * 0.8)
            color = (self.lucolor, self.lucolor, self.lucolor, transparent)
            uline = Image.new("RGBA", (self.size[0], 1), color)
            lline = Image.new("RGBA", (1, self.size[1]), color)
            image.paste(uline, stp, uline)
            image.paste(lline, stp, lline)

        if (overlay or not self.rdoverlay) and not self.rddrawn:
            self.rddrawn = True
            dstp = (self.location[0], self.location[1] + self.size[1])
            rstp = (self.location[0] + self.size[0], self.location[1])
            transparent = int(255 * 0.45 if self.rdcolor == 0 else 255 * 0.8)
            color = (self.rdcolor, self.rdcolor, self.rdcolor, transparent)
            dline = Image.new("RGBA", (self.size[0], 1), color)
            rline = Image.new("RGBA", (1, self.size[1]), color)
            image.paste(dline, dstp, dline)
            image.paste(rline, rstp, rline)


class CaptchaText:
    def __init__(self, priority, offset):
        self.char = ''.join(choices(string.ascii_letters + string.digits, k=1))
        # self.char = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(1))
        self.color = [randint(10, 140) for _ in range(3)]
        self.angle = randint(-55, 55)
        self.priority = priority
        self.offset = offset
        self.next_offset = 0
        self.fonts = ["./fonts/times-bold.ttf", "./fonts/courier-bold.ttf"]

    def draw(self, image):
        color = (self.color[0], self.color[1], self.color[2], 255)
        font = ImageFont.truetype(self.fonts[randint(0, 1)], randint(25, 27) * 10)
        text = Image.new("RGBA", (150, 300), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text)
        text_draw.text((0, 0), str(self.char), font=font, fill=color)
        text = text.rotate(self.angle, expand=True)
        text = text.resize((int(text.size[0] / 10), int(text.size[1] / 10)))
        base = int(self.priority * (200 / 6))
        rand_min = (self.offset - base - 2) if (self.offset - base - 2) >= -15 else -15
        rand_min = 0 if self.priority == 0 else rand_min
        rand_max = (33 - text.size[0]) if self.priority == 5 else (33 - text.size[0] + 10)

        try:
            displace = randint(rand_min, rand_max)
        except:
            displace = rand_max

        location = (base + displace, randint(3, 23))
        self.next_offset = location[0] + text.size[0]
        image.paste(text, location, text)

    def set_fonts(self, fonts):
        self.fonts = fonts

    def set_char_type(self, char_type):
        if char_type:
            char_types = char_type.split(',')

        ch = ''
        if 'num' in char_types:
            ch += string.digits
        if 'upper' in char_types:
            ch += string.ascii_uppercase
        if 'lower' in char_types:
            ch += string.ascii_lowercase

        self.char = ''.join(choices(ch, k=1))


if __name__ == '__main__':
    answer = ""
    random_chars = []
    background_colors = [randint(180, 250) for _ in range(3)]
    captcha_image = Image.new('RGBA', (200, 60), (background_colors[0], background_colors[1], background_colors[2], 255))
    rects = [Rect() for _ in range(32)]

    for obj in rects:
        obj.draw(image=captcha_image, overlay=False)

    offset = 0
    for i in range(6):
        new_text = CaptchaText(i, offset)
        new_text.draw(image=captcha_image)
        offset = new_text.next_offset
        answer += str(new_text.char)

    for obj in rects:
        obj.draw(image=captcha_image, overlay=True)

    captcha_image.convert("RGB").save(answer + ".jpg", "JPEG")
