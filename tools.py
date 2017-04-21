from inspect import getmro
from util import *
import pygame
from olpcgames.svgsprite import SVGSprite
from pygame.locals import *
import math
import components
from core import Globals

# Button superclass -- if it show's up in the sugar menu, it's a button
class Button(object):
    toolTip = "A tooltip"
    icon = "an icon"
    name = "a name"
    order = 1000
    toolBar = "Buttons"

# Tool superclass -- tools are buttons that do more than simply fire off a pygame event
class Tool(Button):
    caption = "A tool's caption"
    toolBar = "Tools"
        
    def handleEvent(self,event):
        pass    
    
    def draw(self):
        pass    
        
    def cancel(self):
        pass


class PlayButton(Button):
    toolTip = "Go!"
    icon = "play"
    name = "playpause"
    order = 1
    toolBar = "Run" 

class ResetButton(Button):
    toolTip = "Reset"
    icon = "reset"
    name = "reset"
    order = 2
    toolBar = "Run"
    
class RevertButton(Button):
    toolTip = "Reset to Original"
    icon = "revert"
    name = "revert"
    order = 3
    toolBar = "Run"
    

class RampTool(Tool):
    # button properties
    toolTip = "Ramp"
    icon = "ramp"
    name = "RampTool"
    order = 10
    toolBar = "Insert"
    # tool properties
    caption = "Ramps don't move, but make good obstacles!"
    
    def __init__(self):
        self.pt1 = self.pt2 = None      
        self.component = components.Ramp
        
    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pt1 = event.pos
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                if self.pt1 and self.pt2:
                    if self.component.amountLeft > 0:
                        Globals.game.userComponents.append(self.component(self.pt1,self.pt2))
                        self.component.amountLeft -= math.ceil(distance(self.pt1,self.pt2)/200)
                self.cancel()                
    
    def draw(self):
        if self.pt1:    
            if self.component.amountLeft > 0:
                self.pt2 = pygame.mouse.get_pos()
                # minimum ramps size of 100
                if distance2(self.pt1,self.pt2,100):
                    # too small! force length of 100
                    theta = getAngle(self.pt1,self.pt2)
                    self.pt2 = (self.pt1[0]+100 * math.cos(theta),self.pt1[1]-100*math.sin(theta))
                    pygame.mouse.set_pos(self.pt2)
                elif not distance2(self.pt1,self.pt2,self.component.amountLeft*200):
                    # you don't have that much ramp left!
                    theta = getAngle(self.pt1,self.pt2)
                    self.pt2 = (self.pt1[0]+(self.component.amountLeft * 200 * math.cos(theta)),self.pt1[1]-(self.component.amountLeft * 200 * math.sin(theta)))
                    pygame.mouse.set_pos(self.pt2)
                pygame.draw.line(Globals.game.screen,(169,129,79),self.pt1,self.pt2,16)
    
    def cancel(self):
        self.pt1 = self.pt2 = None
        
class BouncyBallTool(Tool):
    # button properties
    toolTip = "Bouncy Ball"
    icon = "bouncyball"
    name = "bouncyball"    
    order = 30
    toolBar = "Insert"
    # tool properties
    caption = "Bouncy Balls are small, light, and bouncy!"
    
    def __init__(self):      
        self.component = components.BouncyBall

    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.component.amountLeft > 0:
                    Globals.game.userComponents.append(self.component(event.pos))
                    self.component.amountLeft -= 1
                
                    
    def draw(self):
        if self.component.amountLeft > 0:
            pygame.draw.circle(Globals.game.screen,(105,70,192),pygame.mouse.get_pos(),20,3)

class FutbolTool(Tool):
    # button properties
    toolTip = "Futbol"
    icon = "soccerball"
    name = "futbol"    
    order = 40
    toolBar = "Insert"
    # tool properties
    caption = "Futbols Balls are big, medium weight, and sort of bouncy."
    
    def __init__(self):      
        self.component = components.Futbol

    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.component.amountLeft > 0:
                    Globals.game.userComponents.append(self.component(event.pos))
                    self.component.amountLeft -= 1
                
                    
    def draw(self):
        if self.component.amountLeft > 0:
            pygame.draw.circle(Globals.game.screen,(36,58,139),pygame.mouse.get_pos(),35,3)


class BowlingBallTool(Tool):
    # button properties
    toolTip = "Bowling Ball"
    icon = "bowlingball"
    name = "bowlingball"    
    order = 50
    toolBar = "Insert"
    # tool properties
    caption = "Bowling Balls are big, heavy, and don't bounce much..."
    
    def __init__(self):      
        self.component = components.BowlingBall

    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.component.amountLeft > 0:
                    Globals.game.userComponents.append(self.component(event.pos))
                    self.component.amountLeft -= 1
                
                    
    def draw(self):
        if self.component.amountLeft > 0:
            pygame.draw.circle(Globals.game.screen,(51,51,51),pygame.mouse.get_pos(),40,3) 

class SeeSawTool(Tool):
    # button properties
    toolTip = "See Saw"
    icon = "seesaw"
    name = "seesaw"   
    order = 20
    toolBar = "Insert"
    # tool properties
    caption = "See-Saws make good catapults!"
    
    def __init__(self):
        self.component = components.SeeSaw
       
    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.component.amountLeft > 0:
                    Globals.game.userComponents.append(self.component(event.pos))
                    self.component.amountLeft -= 1                      
    
    def draw(self):
        if self.component.amountLeft > 0:
            # draw a seesaw
            triangle,rect = self.component.getTriangleAndRect(pygame.mouse.get_pos()) 
            pygame.draw.polygon(Globals.game.screen,(202,17,17),triangle,3)
    	    pygame.draw.rect(Globals.game.screen,(242,218,15),rect,3)
            
class FanTool(Tool):
    # button properties
    toolTip = "Fan"
    icon = "fan"
    name = "fan"    
    order = 30
    toolBar = "Insert"
    # tool properties    
    caption = "Fans push objects up!"

    def __init__(self):
        self.component = components.Fan
        img = loadSVG("fan.svg")
        self.sprite = SVGSprite(svg=img,size=(100,0))
        
            
    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.component.amountLeft > 0:
                    Globals.game.userComponents.append(self.component(event.pos))
                    self.component.amountLeft -= 1     

    def draw(self):
        if self.component.amountLeft > 0:            
            if not self.sprite.alive():
                self.sprite.add(Globals.game.allSprites)                
            self.sprite.rect.center = pygame.mouse.get_pos()
    
    def cancel(self):
        self.sprite.kill()

                        
                        
class UnlockButton(Button):
    # button properties
    toolTip = "Unlock the Level"
    icon = "unlock"
    name = "unlock"
    order = 20
    toolBar = "Modify"

class MoveTool(Tool):
    # button properties
    toolTip = "Move"
    icon = "move"
    name = "MoveTool"
    order = 10
    toolBar = "Modify"
    # tool properties
    caption = "Move objects by dragging them"
    
    def __init__(self):
        self.comp = None
        
    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                bodylist = Globals.game.world.bodiesAtPoint(event.pos,include_static=True)
                if bodylist:
                    for b in bodylist:
                        if b.GetUserData()['parent'] in Globals.game.userComponents:
                            self.comp = b.GetUserData()['parent']
                            break
                    
        elif event.type == MOUSEMOTION:
            if self.comp:
                self.comp.moveBy(event.rel)
        elif event.type == MOUSEBUTTONUP and event.button == 1:                    
            self.cancel()                
    
    
    def cancel(self):
        self.comp = None

class ReomveTool(Tool):
    # button properties
    toolTip = "Remove"
    icon = "remove"
    name = "RemoveTool"
    order = 30
    toolBar = "Modify"
    # tool properties
    caption = "Remove objects by clicking on them"

    def __init__(self):
        self.comp = None
    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                bodylist = Globals.game.world.bodiesAtPoint(event.pos,include_static=True)
                if bodylist:
                    for b in bodylist:
                        if b.GetUserData()['parent'] in Globals.game.userComponents:
                            self.comp = b.GetUserData()['parent']
                            break

        elif event.type == MOUSEBUTTONUP and event.button == 1:
            if self.comp:
                self.comp.__class__.amountLeft += self.comp.kill()                
                Globals.game.userComponents.remove(self.comp)
                self.cancel()


    def cancel(self):
        self.comp = None




# ----------------------------------------------------------------------------------------
def getAllTools():
    this_mod = __import__(__name__)
    all = [val for val in this_mod.__dict__.values() if isinstance(val, type)]
    allComp = []
    for a in all:
        if getmro(a).__contains__(Tool) and a!= Tool: allComp.append(a)
    allComp.sort(lambda x,y:x.order-y.order)
    return allComp

def getAllButtons():
    this_mod = __import__(__name__)
    all = [val for val in this_mod.__dict__.values() if isinstance(val, type)]
    allComp = []
    for a in all:
        if getmro(a).__contains__(Button) and a!= Tool and a!= Button: allComp.append(a)
    allComp.sort(lambda x,y:x.order-y.order)
    return allComp

allTools = getAllTools()                         
allButtons = getAllButtons()
