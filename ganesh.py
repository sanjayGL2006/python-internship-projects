"""
Python Color Sketch Drawing - Ganesh
Run:  python ganesh_sketch.py
"""

# pyrefly: ignore [missing-import]
import cv2
import numpy as np
import turtle

image_path = 'ganesh.jpg'
img = cv2.imread(image_path)

if img is None:
    print("Error: 'ganesh.png' nahi mili! Check karein ki photo sahi folder me hai.")
    exit()

# Setup screen box to cover 80% of monitor screen
screen = turtle.Screen()
screen.setup(width=0.8, height=0.8)
screen.bgcolor("black")
screen.title("Python Color Sketch Drawing - Ganesh")
turtle.colormode(255)

# Dynamically scale sketch image size relative to window dimensions
window_w = screen.window_width()
window_h = screen.window_height()
draw_size = int(min(window_w, window_h) * 0.85)
width, height = draw_size, draw_size

# ---- Prepare the image: resize, get edges, and edge colors ----
resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

# Smooth slightly before edge detection to reduce noisy speckling
blurred = cv2.GaussianBlur(gray, (3, 3), 0)
edges = cv2.Canny(blurred, 40, 120)

# Collect edge pixel coordinates (row, col) in raster order
ys, xs = np.where(edges != 0)

# ---- Draw with turtle ----
artist = turtle.Turtle()
artist.hideturtle()
artist.speed(0)
artist.penup()
screen.tracer(0, 0)   # turn off auto-refresh for fast, smooth drawing

step = 1               # increase (e.g. 2 or 3) to draw faster / coarser
dot_size = 2

for i in range(0, len(xs), step):
    x = xs[i]
    y = ys[i]
    r, g, b = rgb[y, x]
    artist.color((int(r), int(g), int(b)))
    artist.goto(x - width / 2, height / 2 - y)
    artist.dot(dot_size)
    if i % 400 == 0:      # periodic refresh so you can watch it "sketch"
        screen.update()

screen.update()
print(f"Done! Plotted {len(xs)} edge points.")
screen.exitonclick()