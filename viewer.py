import json
import sys
import tkinter
from tkinter import Frame, Label, Canvas, StringVar, Button
import PIL
from PIL import Image, ImageTk, ImageDraw, ImageFont

import punterlib

width = 600
height = 600
scale = 100

def to_draw_x(site):
    return site['x'] * scale + width / 2


def to_draw_y(site):
    return site['y'] * scale + height / 2


def draw_edge(source_site, target_site, fill, draw):
    sx = to_draw_x(source_site)
    sy = to_draw_y(source_site)
    tx = to_draw_x(target_site)
    ty = to_draw_y(target_site)

    draw.line((sx, sy, tx, ty), fill=fill, width=3)


def draw_river(sites, rivers, draw):
    for river in rivers:
        source_site = [x for x in sites if x['id'] == river['source']][0]
        target_site = [x for x in sites if x['id'] == river['target']][0]

        draw_edge(source_site, target_site, (0, 0, 0), draw)


def draw_site(site, draw, fill):
    id = site['id']
    x = to_draw_x(site)
    y = to_draw_y(site)
    size = 10
    xy = ((x - size, y - size), (x + size, y + size))
    draw.arc(xy=xy, start=0, end=360, fill=fill)
    draw.text(xy=(x, y), text=str(id), fill=(0, 0, 0), align='center')


def draw_sites(sites, draw):
    for site in sites:
        draw_site(site, draw, (100, 100, 100))


def draw_mines(sites, mines, draw):
    mine_sites = [x for x in sites if x['id'] in mines]
    for mine in mine_sites:
        draw_site(mine, draw, (255, 100, 100))


def draw_body(sites, body, punter_num, draw):
    # とりあえず数決め打ち
    punter_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    if len(punter_colors) < punter_num:
        print('[Warning] punter color is circulated', file=sys.stderr)
    for source_id in range(0, len(body) - 1):
        source_site = [x for x in sites if x['id'] == source_id][0]
        for target_id_str in body[source_id].keys():
            target_id = int(target_id_str)
            target_site = [x for x in sites if x['id'] == target_id][0]
            punter_id = body[source_id][target_id_str]
            color_id = punter_id % len(punter_colors)
            draw_edge(source_site, target_site, punter_colors[color_id], draw)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python viewer.py <MapLog>')
        sys.exit(1)
    with open(sys.argv[1]) as fp:
        log_map = json.load(fp)

    now_step = 0

    root = tkinter.Tk()

    frame = Frame(root, bd=2, relief=tkinter.SUNKEN, width=width, height=height)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    canvas = Canvas(frame, bd=0, width=width, height=height)
    canvas.grid(row=0, column=0)
    frame.pack(fill=tkinter.BOTH, expand=1)

    # Set step no
    label_buff = StringVar()
    label_buff.set('step: 0')

    label = Label(root, textvariable=label_buff)
    label.pack()


    def display_step():
        canvas.delete('image')
        label_buff.set('step: {:d}'.format(now_step))
        step = log_map[now_step]

        img = PIL.Image.new('RGBA', (width, height))
        pixels = img.load()
        for y in range(height):
            for x in range(width):
                pixels[x, y] = (250, 250, 250, 255)
        draw = ImageDraw.Draw(img)
        num_punters = step['num_punters']
        draw_river(step['sites'], step['rivers'], draw)
        draw_body(step['sites'], step['body'], num_punters, draw)
        draw_sites(step['sites'], draw)
        draw_mines(step['sites'], step['mines'], draw)

        global pi
        pi = PIL.ImageTk.PhotoImage(img)
        canvas.create_image(width / 2, height / 2, image=pi, tag='image')


    def move_step(pre):
        global now_step
        if pre:
            now_step = max(0, now_step - 1)
        else:
            now_step = min(len(log_map) - 1, now_step + 1)


    # Set Next/Back Button
    def next_step():
        move_step(pre=False)
        display_step()


    def pre_step():
        move_step(pre=True)
        display_step()


    nextButton = Button(root, text='Next', command=lambda: next_step())
    preButton = Button(root, text='Pre', command=lambda: pre_step())
    nextButton.pack()
    preButton.pack()

    display_step()

    root.mainloop()
