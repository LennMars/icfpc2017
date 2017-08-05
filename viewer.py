import tkinter
from tkinter import Frame, Label, Canvas, StringVar, Button
import PIL
from PIL import Image, ImageTk, ImageDraw

import punterlib

import json

input = 'map.log'

width = 600
height = 600
scale = 100


def draw_river(sites, rivers, draw):
    for river in rivers:
        source_site = [x for x in sites if x['id'] == river['source']][0]
        target_site = [x for x in sites if x['id'] == river['target']][0]
        sx = source_site['x'] * scale + width / 2
        sy = source_site['y'] * scale + height / 2
        tx = target_site['x'] * scale + width / 2
        ty = target_site['y'] * scale + height / 2

        draw.line((sx,sy,tx,ty), fill=128)

def draw_sites(sites, draw):
    for site in sites:
        id = site['id']
        x = site['x'] * scale + width / 2
        y = site['y'] * scale + height / 2
        size = 10
        xy = ((x - size, y - size), (x + size, y + size))
        print(xy)
        draw.arc(xy=xy, start=0, end=360, fill=(100, 255, 100))
        draw.text(xy=(x, y), text=str(id))



def defineSize(log_map):
    print('TODO')

if __name__ == "__main__":
    log_map = json.load(open(input, 'r'))
    for step in log_map:
        print(step)

    root = tkinter.Tk()

    frame = Frame(root, bd=2, relief=tkinter.SUNKEN, width=width, height=height)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    canvas = Canvas(frame, bd=0, width=width, height=height)
    canvas.grid(row=0, column=0)
    frame.pack(fill=tkinter.BOTH, expand=1)

    img = PIL.Image.new('RGBA', (width, height))
    pi = PIL.ImageTk.PhotoImage(img)

    # Draw crossed white lines.
    # draw = ImageDraw.Draw(img)
    # draw.line((0, 0) + img.size, fill=128)
    # draw.line((0, img.size[1], img.size[0], 0), fill=128)


    # Set step no
    label_buff = StringVar()
    label_buff.set('step:0')

    label = Label(root, textvariable=label_buff)
    label.pack()

    # manage step
    now_step = 0

    def display_step():
        canvas.delete('image')
        label_buff.set('step:' + str(now_step))
        step = log_map[now_step]

        pixels = img.load()
        for y in range(height):
            for x in range(width):
                pixels[x, y] = (100, 100, 255, 255)
        global pi
        draw = ImageDraw.Draw(img)
        draw_sites(step['sites'], draw)
        draw_river(step['sites'],step['rivers'],draw)

        pi = PIL.ImageTk.PhotoImage(img)
        canvas.create_image(width / 2, height / 2, image=pi, tag='image')

    def move_step(pre):
        global now_step
        if (pre == True):
            now_step -= 1
            if (now_step < 0):
                now_step += 1
        if (pre == False):
            now_step += 1
            if (now_step >= len(log_map)):
                now_step -= 1

    # Set Next/Back Button
    def next_step():
        move_step(pre=False)

        display_step()

    def pre_step():
        move_step(pre=True)
        display_step()

    nextButton = Button(root, text='Next', command=lambda: next_step())
    nextButton.pack()
    preButton = Button(root, text='Pre', command=lambda: pre_step())
    preButton.pack()

    display_step()

    root.mainloop()
