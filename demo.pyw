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

def HSV2RGB(H,S,V):
    r = colorsys.hsv_to_rgb(H,S,V)
    r = ''.join([f'{hex(int(i*255))[2:]:0>2}' for i in r])

    return r

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
root.wm_attributes("-transparentcolor", 'grey')

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
clockface.create_oval(
    *(ORIGIN-(RADIUS-1)),
    *(ORIGIN+RADIUS)
)

# Drawing the marks
numbers = list(range(4,12+1))+list(range(1,3+1))
numbers.reverse()

for i in range(60):

    rot_matrix = make_rot_matrix(i*6)

    circum = np.dot(rot_matrix,np.array([RADIUS,0]))

    if not i%5:
        tick = circum - np.dot(rot_matrix,np.array([LINE_LARGE,0]))

        clockface.create_line(
            *list(ORIGIN+circum),
            *list(ORIGIN+tick)
        )
        tick = circum - np.dot(rot_matrix,np.array([NUMBER_DIST_FROM_CIRCUMFERENCE,0]))
        clockface.create_text(
            *list(ORIGIN+tick),
            text = numbers[i//5],
            font = ("Comic Sans MS", "24", "bold italic")
        )
        continue
        

    tick = circum - np.dot(rot_matrix,np.array([LINE_SMALL,0]))
    clockface.create_line(
        *list(ORIGIN+circum+0.5),
        *list(ORIGIN+tick+0.5)
    )

# Drawing the hour, minute and second hands
HourHand = Hand(80,10,60)
MinuteHand = Hand(130,5,90,fill='#3366FF')
SecondHand = Hand(175,2,-162,fill='#EE6622')

# Creating the center dot
CenterDot = clockface.create_oval(
    *(ORIGIN-CENTER_RADIUS),
    *(ORIGIN+CENTER_RADIUS-1),
    fill='#FF0000',
    outline='#FF0000'
    )

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

digital_display_frame.place(x=100,y=100)

# Actually *running* the clock
c = 0
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
    c += 1