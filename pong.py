import pygame
from pygame.locals import*
from math import *
from random import randrange
from threading import Thread
from pygame.locals import *
import numpy as np
from scipy import optimize
from Neural_Nets import*
import time
pygame.init()
fenetre = pygame.display.set_mode((1280,730))
fenetre.fill((0,0,0))
events = []
graphicObjects = []
refreshObjects = []
Balls = []
velocity = 7
BallsNumber = 1
color = [255,255,255]
fond = pygame.font.SysFont(None, 48)
framerate = 0
forward = 0
maxY = 0
NN = Neural_Network()
Trainer = trainer(NN)
count = 0
compteur = 1
error = 0
compteur2 = 0
isTraining = False

def mapper(Pvalue,Pmin,Pmax,Nmin,Nmax):
    oldRange = Pmax - Pmin
    if oldRange == 0:
        NValue = Nmin
    else:
        NRange = Nmax - Nmin
        NValue = (((Pvalue - Pmin) * NRange) / NRange ) + Nmin
    return NValue

def changeColor():
    for x in range(3):
        if randrange(2): color[x] += 3
        else: color[x]-=3
        if color[x] > 255: color[x] = 255
        elif color[x] < 50: color[x] = 50

         
class Graphics(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.name = "Graphic Thread"
        self.turn = True
    def run(self):
        while self.turn:
            time.sleep(0.015)
            changeColor()
            fenetre.fill((0,0,0))
            display_score(fenetre)
          #  try:
            for obj in graphicObjects: obj.show()
            #except: print("OH GOTAGA")
            pygame.display.flip()

class Ball:
    def __init__(self):
        self.pos = vector((1280/2),(720/2),0)
        self.vel = vector(randrange(2000) / 1000-1,randrange(2000)/1000-1,0)
        self.vel.x*=3
        self.vel.y*=3
        self.acc = 0
        self.isMovingLeft = False
        self.bounces = 0
        self.count = 0
        self.count2 = 0
        self.countMovingLeft = 0
        self.X = np.array(([0,0,0]),dtype = float)
        self.y = np.array(([0]),dtype = float)
        
    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

    def edges(self):
        if self.pos.y > 680:
            self.pos.y = 680
            self.vel.y *=-1
            self.bounces += 1
            
        if self.pos.y < 35:
            self.pos.y = 35
            self.vel.y *= -1
            self.bounces+= 1

        if self.pos.x < 35:
            self.pos.x = 35
            self.vel.x *= -1
            self.bounces = 0
            Ia.score+=1
            self.countMovingLeft = 1
            
        if self.pos.x > 1250:
            self.pos.x = 1250
            self.vel.x *= -1
            self.bounces = 0
            player.score+=1
            
        if  self.pos.x < 65 and self.pos.x > 35 and self.pos.y > player.pos.y - 85 and self.pos.y < player.pos.y + 85 :
            self.pos.x = 65
            b = mapper(self.pos.y, player.pos.y - 85, player.pos.y + 85, -pi/3 , pi/3 )
            self.vel.x = cos(b) * 5
            self.vel.y = sin(b) * 5
            self.bounces = 0
            player.catch += 1
            self.countMovingLeft = 1
            
        if self.pos.x > 1215 and self.pos.x < 1230 and self.pos.y > Ia.pos.y - 65 and self.pos.y < Ia.pos.y + 65 and isTraining == False: 
            self.pos.x = 1215
            c = mapper(self.pos.y, Ia.pos.y - 85, Ia.pos.y + 85, -pi/3 , pi/3 )
            self.vel.x = -cos(c) * 5
            self.vel.y = sin(c) * 5
            self.bounces = 0
            Ia.catch += 1
        if self.vel.x > 0:
            self.vel.x += self.bounces/500
            self.vel.y -= self.bounces/500
        else:
            self.vel.x -= self.bounces / 500
            self.vel.y += self.bounces /500
    def direction(self):
        z = position - self.pos.x
        if z <= 0:
            self.isMovingLeft = True
        else: 
             self.isMovingLeft = False
             
    def show(self):
        pygame.draw.circle(fenetre,color,[int(self.pos.x), int(self.pos.y)],20,0)

    def createData(self):
        if self.pos.x >600 and self.pos.x < 610 and self.isMovingLeft:
            
            if self.count == 0 and self.countMovingLeft > 0:
                
                self.X = np.array(([self.pos.y, self.vel.x, self.vel.y]), dtype = float)
                self.count+=1
                self.countMovingLeft = 0
                
            elif self.countMovingLeft > 0:
                
                self.X = np.vstack((self.X, [self.pos.y, self.vel.x, self.vel.y]))
                self.countMovingLeft = 0
                
        if self.pos.x >1215 and self.pos.x < 1225 and self.isMovingLeft:
            
            if self.count2 == 0 and self.countMovingLeft == 0 and self.count >0:
                
                self.y = np.array(([self.pos.y]), dtype= float)
                self.count2 +=1
                self.countMovingLeft = 1
                
            elif self.countMovingLeft == 0 and self.count>0:
                
                self.y = np.vstack((self.y, [self.pos.y]))
                self.countMovingLeft = 1
        

class Player:
    def __init__(self):
        self.keyPressed = []
        self.isMoving = False
        self.isMovingUp = False
        self.pos = vector(720/2,0,0)
        self.score = 0
        self.catch = 1
        

    def update (self):
        if self.isMoving:
            if self.isMovingUp:
                self.pos.y -=velocity
            else:
                self.pos.y += velocity
        if self.pos.y > 620:
            self.pos.y = 620
        if self.pos.y < 100:
            self.pos.y = 100

    def control(self, event):
        if  event.key == K_UP:
            if event.type == KEYDOWN:
                self.isMoving = True
                self.isMovingUp = True
            else:
                self.isMoving = False
                self.isMovingUp = False
        elif event.key == K_DOWN:
            if event.type == KEYDOWN:
                self.isMoving = True
            else:
                self.isMoving = False
    def choose(self):
        for var in Balls:
            if var.pos.x < 400:
                if  not var.isMovingLeft:
                    if var.pos.y < self.pos.y:
                        self.pos.y -= velocity
                    if var.pos.y > self.pos.y:
                        self.pos.y += velocity
        if self.pos.y > 620:
            self.pos.y = 620
        if self.pos.y < 100:
            self.pos.y = 100

    def show(self):
        pygame.draw.rect(fenetre,(255,255,255),[30, int(self.pos.y - 70),20,140],0)
        
class ia:
    def __init__(self):
        self.pos = vector(0,720/2,0)
        self.score = 0
        self.catch = 1

    def update(self):
        if self.pos.y > 620:
            self.pos.y = 620
        if self.pos.y < 100:
            self.pos.y = 100
        
    def show(self):
        pygame.draw.rect(fenetre,(255,255,255),[1230, int(self.pos.y - 70),20,140],0)
    def choose(self):
        for var in Balls:
            if 1280 - var.pos.x < 600:
                if var.isMovingLeft:
                    if forward < self.pos.y:
                        self.pos.y -= velocity
                    if forward > self.pos.y:
                        self.pos.y += velocity
        
class Terrain:
    def __init__(self):
        self.size = vector(1250,680,0)
        self.pos = vector(18,20,0)
    def show(self):
        pygame.draw.rect(fenetre,color,[self.pos.x,self.pos.y,self.size.x,self.size.y],10)
        pygame.draw.line(fenetre,color,[int((self.pos.x + self.size.x)/2),self.pos.y],[int((self.pos.x + self.size.x)/2), self.pos.y+self.size.y],10)
        pygame.draw.circle(fenetre,color,[int((self.pos.x + self.size.x)/2),int((self.pos.y + self.size.y)/2)],130,8)
        pygame.draw.circle(fenetre,(255,0,0),[1215, forward],20,0)
    
class vector:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

for x in range(BallsNumber):
    Balls.append(Ball())
    
for var in Balls:
    graphicObjects.append(var)
player = Player()
Ia = ia()
terrain = Terrain()
graphicObjects.append(player)
graphicObjects.append(Ia)
graphicObjects.append(terrain)
refreshObjects.append(player)
graphics = Graphics()
graphics.start()

def display_score(screen):
        
    player_score = fond.render(str(player.score)+" // catching ratio : " + str(int((player.catch/(player.catch + Ia.score))*100)) + "%", True, (255, 255, 255))
    Ia_score = fond.render(str(Ia.score) + " // catching ratio : " + str(int((Ia.catch/(Ia.catch + player.score))*100)) + "%", True, (255, 255, 255))
    Ia_error = fond.render( " av error : " + str(int(error/compteur)), True, (255, 255, 255))
    screen.blit(Ia_error,(700,100))
    screen.blit(player_score,(100, 70))
    screen.blit(Ia_score,(700, 70))

    
while 1:
    for event in pygame.event.get():
                if event.type in [KEYUP,KEYDOWN]:
                    for obj in refreshObjects: obj.control(event)
    for var in Balls:
        position = var.pos.x
        var.update()
        var.edges()
        var.direction()
        if var.y.shape != (500,1):
            var.createData()
            isTraining = True
    player.choose()
    player.update()
    if Balls[0].y.shape == (500,1):
        compteur2+=1
        Ia.choose()
        Ia.update()
        Ia.choose()
        if count >= 50:
            isTraining = False
        if Balls[0].pos.x >600 and Balls[0].pos.x < 610 and Balls[0].isMovingLeft:
            pretab = [Balls[0].pos.y, Balls[0].vel.x, Balls[0].vel.y]
            pretab = pretab/maxX
            forward = NN.forward(pretab)*maxY

        time.sleep(0.009 )
        if count == 0:
            maxY = np.amax(Balls[0].y, axis=0)
            maxX = np.amax(Balls[0].X, axis=0)
            Balls[0].X = Balls[0].X/maxX
            Balls[0].y = Balls[0].y/maxY
            Player.score = 0
            count+=1
        if count < 50:
            isTraining = True
            Trainer.train(Balls[0].X, Balls[0].y)
            count +=1
            player.score = 0
            Ia.score = 0
        framerate = 0.01
        if forward != 0 and Balls[0].pos.x> 1200 and Balls[0].pos.x<1215 and Balls[0].isMovingLeft :
            error += sqrt((forward - Balls[0].pos.y)**2)
            compteur +=1
                      

    
