import os
import random as r
import time as t
import tkinter as tk
from datetime import *
import numpy as np
import pyglet
import colorsys

def make_rot_matrix(theta):
    theta = np.radians(theta)
    s, c = np.sin(theta), np.cos(theta)
    return np.array(
        [[c,-s],
        [-s,-c]],
        dtype=float
    )

def invert(rgb):
    convert = {
        'SystemButtonFace': '#F0F0ED',
        'black': '#000000'
    }
    if rgb in convert:
        rgb = convert[rgb]
    if rgb == '':
        return ''
    rgb = int(rgb[1:],16)
    rgb = int('FFFFFF',16) - rgb
    rgb = f'#{hex(rgb)[2:].upper():>06}'
    return rgb

# def HSV2RGB(H,S,V):
#     r = colorsys.hsv_to_rgb(H,S,V)
#     r = ''.join([f'{hex(int(i*255))[2:]:02}' for i in r])

#     return r

class Hand:
    def __init__(self, length, width, rot, **kwargs):

        self.length = length
        self.width = width

        rot_matrix = make_rot_matrix(rot)

        self.points = np.array([
            np.array([0,width/2]),
            np.array([length,width/2]),
            np.array([length,-width/2]),
            np.array([0,-width/2])
        ])

        self.points = ORIGIN + np.array([np.dot(rot_matrix,p) for p in self.points])
        self.points = [list(p) for p in self.points]

        self.kwargs = kwargs
        self.rect = clockface.create_polygon(*self.points,**self.kwargs)

    def rotate(self, angle):
        clockface.delete(self.rect)
        self = self.__init__(self.length, self.width, angle, **self.kwargs)

root = tk.Tk()
root.geometry('600x600')
root.title("SoCS O'Day Demo")
root.resizable(0,0)

bg = [root]
fill = []

# Drawing the clock face
CLOCKFACE_POS = {'x':100, 'y':50}
RADIUS = 200
CLOCKFACE_SIDE = RADIUS*2+1
ORIGIN = np.full(2,CLOCKFACE_SIDE//2+1)
LINE_SMALL = 10
LINE_LARGE = 25
CENTER_RADIUS = 5
NUMBER_DIST_FROM_CIRCUMFERENCE = 50

clockface = tk.Canvas(root,bg='#00FF00',width=CLOCKFACE_SIDE,height=CLOCKFACE_SIDE)
bg.append(clockface)
clock_circle = clockface.create_oval(
    *(ORIGIN-(RADIUS-1)),
    *(ORIGIN+RADIUS)
)
fill.append(clock_circle)

# Drawing the marks
numbers = list(range(4,12+1))+list(range(1,3+1))
numbers.reverse()

for i in range(60):

    rot_matrix = make_rot_matrix(i*6)

    circum = np.dot(rot_matrix,np.array([RADIUS,0]))

    if not i%5:
        tick = circum - np.dot(rot_matrix,np.array([LINE_LARGE,0]))

        fill.append(clockface.create_line(
            *list(ORIGIN+circum),
            *list(ORIGIN+tick)
        ))
        tick = circum - np.dot(rot_matrix,np.array([NUMBER_DIST_FROM_CIRCUMFERENCE,0]))
        fill.append(clockface.create_text(
            *list(ORIGIN+tick),
            text = numbers[i//5],
            font = ("Comic Sans MS", "24", "bold italic")
        ))
        continue
        

    tick = circum - np.dot(rot_matrix,np.array([LINE_SMALL,0]))
    fill.append(clockface.create_line(
        *list(ORIGIN+circum+0.5),
        *list(ORIGIN+tick+0.5)
    ))

# Drawing the hour, minute and second hands
hands = []
HourHand = Hand(length=80,width=10,rot=6,fill='#000000')
MinuteHand = Hand(length=160,width=5,rot=9,fill='#3366FF')
SecondHand = Hand(length=175,width=2,rot=420,fill='#EE6622')
hands.append(HourHand)
hands.append(MinuteHand)
hands.append(SecondHand)

# Creating the center dot
CenterDot = clockface.create_oval(
    *(ORIGIN-CENTER_RADIUS),
    *(ORIGIN+CENTER_RADIUS-1),
    fill='#FF0000',
    outline='#FF0000'
    )
fill.append(CenterDot)

clockface.place(**CLOCKFACE_POS)

# Digital Clock Face
pyglet.font.add_file(r"./assets/fonts-DSEG_v046\DSEG7-Modern/DSEG7Modern-BoldItalic.ttf")
digital_font = ("DSEG7 Modern","15")

digital_display_frame = tk.Frame(root)

sep = 45
digitalHour = clockface.create_text(*(ORIGIN-np.array([sep,80])),text='00',font=digital_font)
digitalMinute = clockface.create_text(*(ORIGIN-np.array([0,80])),text='00',font=digital_font)
digitalSecond = clockface.create_text(*(ORIGIN-np.array([-sep,80])),text='00',font=digital_font)
colon1 = clockface.create_text(*(ORIGIN-np.array([sep/2,80])),text=':',font=digital_font)
colon2 = clockface.create_text(*(ORIGIN-np.array([-sep/2,80])),text=':',font=digital_font)

fill.append(digitalHour)
fill.append(digitalMinute)
fill.append(digitalSecond)
fill.append(colon1)
fill.append(colon2)

digital_display_frame.place(x=100,y=100)

# Dark mode
def dark_mode():
    global bg, fill, dark, dark_mode_btn
    dark = not dark
    if dark:
        dark_mode_btn['text'] = 'Light Mode'
    else:
        dark_mode_btn['text'] = 'Dark Mode'
    for item in bg:
        color = item['bg']
        color = invert(color)
        item['bg'] = color
    for item in fill:
        color = clockface.itemcget(item,'fill')
        color = invert(color)
        clockface.itemconfig(item,fill=color)
    for hand in hands:
        color = hand.kwargs['fill']
        color = invert(color)
        hand.kwargs['fill'] = color

dark = False
dark_mode_btn = tk.Button(root,text='Dark Mode',command=dark_mode)
dark_mode_btn.place(x=265,y=500)

# Actually *running* the clock
while 1:

    timenow = t.localtime()
    hour = timenow.tm_hour
    minute = timenow.tm_min
    second = timenow.tm_sec
    second += t.time_ns()/1e9 - t.time_ns()//1e9

    if int(2*second) % 2:
        clockface.itemconfig(colon1,text=' ')
        clockface.itemconfig(colon2,text=' ')
    else:
        clockface.itemconfig(colon1,text=':')
        clockface.itemconfig(colon2,text=':')

    HourHand_degrees = second*0.5/60 + minute*0.5 + hour*30
    MinuteHand_degrees = minute*6 + second/10
    SecondHand_degrees = second*6
    
    clockface.itemconfig(digitalHour,text=f'{hour:02}')
    clockface.itemconfig(digitalMinute,text=f'{minute:02}')
    clockface.itemconfig(digitalSecond,text=f'{int(second):02}')

    HourHand.rotate(-HourHand_degrees+90)
    MinuteHand.rotate(-MinuteHand_degrees+90)
    SecondHand.rotate(-SecondHand_degrees+90)

    clockface.tag_raise(CenterDot)

    root.update()
    root.update_idletasks()