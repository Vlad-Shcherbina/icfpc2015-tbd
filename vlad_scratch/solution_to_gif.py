import os
import json
import itertools

from PIL import Image
from PIL import ImageDraw

from production import game
from production import utils
from production import interfaces


def produce_frames(g, commands, thinning):
    for c in commands:
        try:
            g.execute_string(c)
            if (len(g.history) - 1) % thinning:
                continue
        except interfaces.GameEnded as e:
            pass

        lines = str(g).splitlines()
        img = Image.new(
            'RGB',
            (len(lines[0]) + 1, len(lines) * 2 + 5 + 12 * 15),
            (20, 20, 20))
        pixels = img.load()

        for i, line in enumerate(lines):
            for j, cell in enumerate(line):
                if cell == ' ':
                    continue
                color = {
                    '.' : (0, 0, 0),
                    '*': (255, 255, 255),
                    '?': (255, 255, 0),
                    }[cell]
                x = j
                y = 2 * i
                pixels[x, y] = pixels[x, y + 1] = \
                pixels[x + 1, y] = pixels[x + 1, y + 1] = color

        draw = ImageDraw.Draw(img)
        y = 2 * len(lines) + 5
        h = ''.join(g.history)
        for phrase in interfaces.POWER_PHRASES:
            cnt = utils.count_substrings(h, phrase)
            if cnt == 0:
                continue
            draw.text((2, y), '{:5}'.format(cnt), fill=(160, 230, 160))
            draw.text((6, y), '     ' + phrase, fill=(170, 170, 190))
            y += 12

        yield img


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def motion_blur(frames, scale):
    for batch in grouper(frames, scale):
        img = batch[0]
        for i, img2 in enumerate(batch[1:], 2):
            if img2 is None:
                break
            img = Image.blend(img, img2, 1.0 / i)
        yield img


def main():
    solution_file = os.path.join(
        utils.get_project_root(), 'vlad_scratch/solution24.json')
    with open(solution_file) as fin:
        solution = json.load(fin)

    input_file = 'qualifier/problem_{}.json'.format(solution['problemId'])
    path = os.path.join(utils.get_data_dir(), input_file)
    with open(path) as fin:
        data = json.load(fin)

    g = game.Game(data, solution['seed'])

    frames = produce_frames(g, solution['solution'], thinning=600)
    #frames = motion_blur(frames, 10)

    frame = 0
    for img in frames:
        img.save('images/{:05}.png'.format(frame))
        frame += 1
        print(frame)

    # Then to generate GIF:
    #   convert -layers optimizeplus -fuzz 30 -delay 100 images/00000.png -delay 2 images/*.png -delay 100 images/02331.png solution.gif
    #   gifsicle -O3 --colors 6 <solution.gif >solution_optimized.gif

if __name__ == '__main__':
    main()
