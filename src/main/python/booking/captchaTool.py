import string
import speech_recognition
import cv2

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


class CaptchaAudio(object):
    def __init__(self, audio_file):
        self.audio = audio_file

    def convert_to_text(self):
        r = speech_recognition.Recognizer()
        with speech_recognition.AudioFile(self.audio) as source:
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.record(source)

        text = r.recognize_google(audio, language='zh-tw')
        return text


class CaptchaImage(object):
    def __init__(self, file, flag=cv2.IMREAD_COLOR):
        self.image = cv2.imread(file, flag)
        print(self.image.shape)

    def threshold(self):
        retval, self.image = cv2.threshold(self.image, 115, 255, cv2.THRESH_BINARY_INV)

    def blurred(self):
        self.image = cv2.GaussianBlur(self.image, (3, 3), 0)

    def morphology(self):
        # kernel = np.ones((2, 2), np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        self.image = cv2.morphologyEx(self.image, cv2.MORPH_CLOSE, kernel)

    def gray(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def denoise_by_threshold(self):
        for col in range(3):
            count = 0
            for i in range(len(self.image)):
                for j in range(len(self.image[i])):
                    if self.image[i, j, col] == 255:
                        count = 0
                        for k in range(-2, 3):
                            # print(k)
                            for l in range(-2, 3):
                                try:
                                    if self.image[i + k, j + l, col] == 255:
                                        count += 1
                                except IndexError:
                                    pass
                                # 這裡 threshold 設 4，當周遭小於 4 個點的話視為雜點
                    if count <= 4:
                        self.image[i, j, col] = 0

    def edge(self):
        self.image = cv2.Canny(self.image, 30, 150)

    def show(self, title=''):
        cv2.imshow(title, self.image)

    @staticmethod
    def destroy():
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def split_axis(image, axis):
        splits = []
        if axis == 'x':
            for i in range(image.shape[1]):
                if sum(image[:, i, 0]) != 0:
                    splits.append(i)

        elif axis == 'y':
            for i in range(image.shape[0]):
                if sum(image[i, :, 0]) != 0:
                    splits.append(i)

        return splits

    def divide_char(self):
        x_splits = self.split_axis(self.image, 'x')

        divide_x = []
        tmp_x = [x_splits[0]]
        for i in range(1, len(x_splits)):
            if x_splits[i] - x_splits[i-1] > 3:
                divide_x.append(tmp_x)
                tmp_x = [x_splits[i]]
            else:
                tmp_x.append(x_splits[i])
        divide_x.append(tmp_x)

        divide_images = []
        for x in divide_x:
            tmp_image = self.image[:, min(x):max(x), :]
            y = self.split_axis(tmp_image, 'y')
            char_image = tmp_image[min(y):max(y), :, :]
            divide_images.append(char_image)

        return divide_images


if __name__ == '__main__':
    pass
