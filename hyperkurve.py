#!/usr/bin/python

import sys
import math
import cmath
import random

FPS = 45
TDELTA = 60./float(FPS)

pi = 3.14159265359


P = 7
Q = 3

sgn = [1,-1][P%2]

Sp = math.sin(math.pi/P)
Sq = math.sin(math.pi/Q)
Sh = math.sqrt(1-Sp**2 - Sq**2)/(Sp*Sq)
circumradius = math.asinh(Sh)
apotheme = math.asinh(Sq*Sh)


def D(u,v):
    delta = 2 * abs(u-v)**2 / ((1-abs(u)**2)*(1-abs(v)**2))
    return math.acosh(1+delta)

class Point:
    def __init__(self,p,colour=(255,255,255),label=None):
        if abs(p) >= 1:
            print "ERROR"
            #sys.exit()
        self.v = p
        self.colour = colour
        self.label = label

    def Mobius(self,m):
        alfa,beta = m
        return Point((alfa*self.v + beta)/(beta.conjugate()*self.v + alfa.conjugate()),colour=self.colour,label=self.label)

    def Translator(self):
        beta = self.v
        return (1,beta)

    def translate(self,vec):
        return self.Mobius(vec.Translator())
    
    def __str__(self):
        return str(self.v)

    def x(self):
        return self.v.real
    def y(self):
        return self.v.imag


class Tile:
    def __init__(self,m):
        self.m = m

    def generate(self,d=-1):
        if d < 0:
            d = random.randint(0,P-1)

        return mxm(
                self.m,
                mxm(
                (1,-cmath.exp(2J*pi/float(P)*(d))*R2r(2*apotheme)),
                (1J,0)
                )
                
                
                )

    



def mxm(g,h):
    a,b = g
    r,s = h

    return ( a*r + b * s.conjugate() , a*s + b * r.conjugate())

def R2r(R):
    ch = math.cosh(R)

    return math.sqrt ( (ch-1)/(ch+1) )

def r2R(r):
    return math.acosh(1 + 2* r*r/(1-r*r) )

l = math.log(2)
l2 = math.log(64)

def decomp_noise(c):
    n = int ( r2R(abs(c)) / l)
    m = int ( (math.atan2(c.real,c.imag)+pi) /( 2 * pi )*7*(2**(n))  )
    return (n,m)

def decomp_noise_large(c):
    n = int ( (r2R(abs(c)) + l2/2.) / l2)
    m = int ( (math.atan2(c.real,c.imag)+pi) /( 2 * pi )*(32**(n))  )
    return (n,m)

def ranc(t):
    tmp = random.getstate()
    random.seed(t)
    r = (random.randint(0,125),random.randint(0,125),random.randint(0,125))
    random.setstate(tmp)
    return r

def terrain_color(c):
    c1 = ranc( decomp_noise_large(c))
    c2 = ranc( decomp_noise(c))
    
    

    return tuple ( [ int( c1[i] + c2[i]*0.13 )for i in range(3) ] )


euc_circumradius = R2r(circumradius)
euc_apotheme = R2r(apotheme)

p7 = [ Point(1.*euc_circumradius * cmath.exp(2*pi/float(P) *(i-.5+.5*(P%2))*1J)) for i in range(P)]
p7m = [ Point(1.*euc_apotheme * cmath.exp(2*pi/float(P) *(i+.5*(P%2))*1J)) for i in range(P)]



import pygame
from pygame.locals import *

class Manager:

        def __init__(self,width=640,height=640):
                pygame.init()
                self.width = width
                self.height = height
                self.screen = pygame.display.set_mode((width,height))
                self.clock = pygame.time.Clock()

                self.points = []# [ Point(.5*cmath.exp((0.1+0.5J)*(i))) for i in range(-20,5) ]

                self.points.append(Point(0,colour=(255,255,255),label="0"))

                for i in range(2,7):
                    R = i * math.log(8)
                    K = (math.cosh(R)+1)/2
                    r = math.sqrt(K/(K+1))
                    n = 8**(i-2)
                    #for j in range(n):
                    #    self.points.append(Point(cmath.exp(2J*pi/float(n)*j)*r,  (random.randint(0,255),125,125)))

                self.tiles = []

                self.tiles.append(Tile((1,0)))


                self.view = (1,0)


        def gameLoop(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()

            keys=pygame.key.get_pressed()
            if keys[K_LEFT]:
                self.view = mxm(
                        (cmath.exp(0.02J*TDELTA),0),
                        self.view
                        )

            if keys[K_RIGHT]:
                self.view = mxm(
                        (cmath.exp(-0.02J*TDELTA),0)
                        ,self.view)

            if keys[K_UP]:
           #     self.view = (self.view[0],Point(self.view[1]).Mobius((1,self.view[0]*0.01J)).v)
                self.view = mxm(
                        (1,0.006J*TDELTA),
                        self.view)
           
            if keys[K_DOWN]:
                self.view = mxm(
                        (1,-0.006J*TDELTA),
                        self.view)

            if abs(self.view[1]/self.view[0])>R2r(15):
                self.view = mxm(
                        self.view,
                        (1,-self.view[1]/self.view[0] * 0.02)
                        )

            if random.randint(0,20)== 0:
                self.points.append(Point(-self.view[1]/self.view[0]))

            if random.randint(0,1) == 0:
             self.tiles.sort(key = lambda t: D(-self.view[1]/self.view[0],t.m[1]/t.m[0].conjugate()))
             for cc in range(20):
                index = random.randint(0,len(self.tiles)-1)
                if random.randint(0,2)==0:
                    index = random.randint(0,int((len(self.tiles)-1)/4))

                t = self.tiles[index]
                nm = t.generate(random.randint(0,7))
                already = False
                for tt in self.tiles:
                    if D(-nm[1]/nm[0].conjugate(),0) > 15:
                        already = True
                        continue
                    if D(-nm[1]/nm[0].conjugate(), -tt.m[1]/tt.m[0].conjugate()) < 0.01:
                       # print "overlap"
                        already = True
                if not already:
                    self.tiles.append(Tile(nm))

            #todel = i
            #for i in reversed(range(len(self.tiles))):
            #    t = self.tiles[i]
            #    if R2r( D(-t.m[1]/t.m[0],-self.view[1]/self.view[0]) ) > 0.95:
            #        print "cleanup"
            #        del self.tiles[i]
            self.tiles = filter( lambda t:
                    D(Point(t.m[1]/t.m[0].conjugate()).Mobius(self.view).v, 0) < 3.5,
                    self.tiles)

        def c2screen(self,c):
            return (int(self.width/2 * (1+c.real)), int(self.width/2 *(1+c.imag)))

        def drawtiles(self):
            
            #sys.exit()
            for t in self.tiles:
                plist = []
                for i in range(P):
                    p = p7[i]
                    pm = p7m[i]
                    np = p.Mobius(t.m)
                    npm = pm.Mobius(t.m)
                    np = np.Mobius(self.view)
                    npm = npm.Mobius(self.view)
                    plist.append(self.c2screen(np.v))
                    plist.append(self.c2screen(npm.v))

                #C = (int( D(Point(t.m[1]/t.m[0].conjugate(), -self.view[1]/self.view[0])*20),50,0)
                C = terrain_color(t.m[1]/t.m[0].conjugate())

                pygame.draw.polygon(self.screen,C,plist,0)


        def drawdot(self,p,colour=(255,255,255),size=3):
            rr = size*(1-p.x()**2 - p.y()**2)
            pygame.draw.circle(self.screen,colour,(int(self.width/2*(1+p.x())),int(self.width/2*(1+p.y()))),int(rr),0)

            if rr<0.1:
                if p.label != None:
                    s = (1+1J + p.v/abs(p.v)*0.99) * self.width/2
                    
                    RR = Rect(int(s.real - 5),int(s.imag-5),10,10)
                    pygame.draw.rect(self.screen,colour,RR,0)

        def drawboundary(self,radius):
            K = (math.cosh(radius)+1)/2
            p = math.sqrt(K/(K+1))
            p1 = Point(p*1J)
            p2 = Point(-p*1J)
            p3 = Point(p*1)

            p1 = p1.Mobius(self.view)
            p2 = p2.Mobius(self.view)
            p3 = p3.Mobius(self.view)

            D = 2 * (
                    p1.x() * (p2.y()-p3.y()) + 
                    p2.x() * (p3.y() - p1.y()) + 
                    p3.x() * (p1.y() - p2.y())
                    
                    )

            cx = ( abs(p1.v)**2 * (p2.y()-p3.y()) + abs(p2.v)**2 * (p3.y()-p1.y()) + abs(p3.v)**2 *(p1.y()-p2.y())) / D
            cy = ( abs(p1.v)**2 * (p3.x()-p2.x()) + abs(p2.v)**2 * (p1.x()-p3.x()) + abs(p3.v)**2 *(p2.x()-p1.x())) / D


            c = Point(cx+cy*1J)
            r = abs(p1.v-c.v)

            pygame.draw.circle(self.screen,(125,0,0),(int(self.width/2*(1+c.x())),int(self.width/2*(1+c.y()))),int(self.width/2*r),2)


        def draw(self,view=(1,0)):
            self.screen.fill((0,0,0))

            self.drawtiles()

            for p in self.points:
                np = p.Mobius(view)
                self.drawdot(np,p.colour)

            self.drawboundary(15)

            pygame.draw.circle(self.screen,(255,255,255),(self.width/2,self.width/2),self.width/2,3)
            
            pygame.display.flip()


        def mainLoop(self):
            while 1:
                self.gameLoop()
                self.draw(self.view)
                self.clock.tick(FPS)


manager = Manager(1000,1000)

manager.mainLoop()
