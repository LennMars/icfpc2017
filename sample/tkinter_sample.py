import tkinter
from tkinter import Frame, Canvas
import PIL
from PIL import Image, ImageTk, ImageDraw

width = 200
height = 200

if __name__ == "__main__":
    root = tkinter.Tk()

    frame = Frame(root, bd=2, relief=tkinter.SUNKEN, width=width, height=height)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    canvas = Canvas(frame, bd=0, width=width, height=height)
    canvas.grid(row=0, column=0)
    frame.pack(fill=tkinter.BOTH, expand=1)

    def click(event):
        x, y = event.x, event.y
        print('click {:d} {:d}'.format(x, y))

    def motion(event):
        x, y = event.x, event.y
        print('motion {:d} {:d}'.format(x, y))

    canvas.bind("<Button 1>", click)
    canvas.bind('<Motion>', motion)

    img = PIL.Image.new('RGBA', (width, height))

    # Paint red.
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = (255, 0, 0, 255)

    # Draw crossed white lines.
    draw = ImageDraw.Draw(img)
    draw.line((0, 0) + img.size, fill=128)
    draw.line((0, img.size[1], img.size[0], 0), fill=128)

    pi = PIL.ImageTk.PhotoImage(img)
    sprite = canvas.create_image(100, 100, image=pi)
    canvas.update()

    root.mainloop()
