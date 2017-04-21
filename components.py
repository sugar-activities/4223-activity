from inspect import getmro
from util import *
import util_poly
import pygame
from olpcgames.svgsprite import SVGSprite
from pygame.locals import *
import math
from physics import *

class Component(object):
    amountLeft = float('inf')
    caption = "Unlimited!"
    name = "Component"
    def __init__(self,*args):
        self.args = list(args)
    
    def draw(self):
        pass
    
    def moveBy(self,vec):
        pass
    
    # reset to 'init' point
    def reset(self):
        pass
    
    def kill(self):
        pass
        
    # all components that creat 'things' (rigid bodies / sprites / callbacks / unique ids)
    # should have a kill(self) method that cleans up
    # all the 'things' it created
    # that means in __init__ be sure to keep track of your 'things'

class X(Component):
    name = "X"
    def __init__(self,pt):
        Component.__init__(self,pt)
        center = toWorld(pt)
        self.body = Globals.game.world.addBody(center,self)
        
        boxDef = box2d.b2PolygonDef()
        width = 50/PPM
        height = 50/PPM        
        boxDef.SetAsBox(width,height)
        boxDef.density = 0
        boxDef.restitution = 0.15
        boxDef.friction = 0.5   
        self.shape = self.body.CreateShape(boxDef)
        self.shape = self.shape.asPolygon()   
        self.body.SetMassFromShapes()
        
        # sprite representation
        img = loadSVG("x.svg")
        self.sprite = SVGSprite(svg=img,size=(100,100))
        self.sprite.add(Globals.game.allSprites)
        #Add the callback        
        Globals.game.world.contactListener.connect(self.body,self.handleContact)
    
    def draw(self):        
        self.sprite.rect.center = toScreen(self.body.GetWorldCenter())
    
    def handleContact(self,contactType,point):
        if contactType == "Add":
            b1 = point.shape1.GetBody().GetUserData()
            b2 = point.shape2.GetBody().GetUserData()
            o = None
            if b1['parent'].__class__ == O: 
                o = b1['parent']
            elif b2['parent'].__class__ == O:
                o = b2['parent']
            if o:
                Globals.game.world.run = False
                x,y = toScreen(self.body.GetWorldCenter())
                o.destination = (x,y-75)
                Globals.game.allSounds['ouch.wav'].play()
                
    
    def moveBy(self,vec):
        pt = self.args[0]
        x,y = pt
        mx,my = vec
        x+=mx
        y+=my
        self.args = [(x,y)]
        self.reset()
    
    def reset(self):
        pt = toWorld(self.args[0])
        self.body.SetXForm(box2d.b2Vec2(*pt),0)
        stopBody(self.body)
    
    def kill(self):
        ud = self.body.GetUserData()
        Globals.game.world.contactListener.disconnect(self.body)
        returnID(ud['id'])
        Globals.game.world.world.DestroyBody(self.body)
        self.sprite.kill()
        return None            
        
class O(Component):
    name = "O"
    def __init__(self,pt):
        Component.__init__(self,pt)
        self.body = Globals.game.world.addBody(toWorld(pt),self)
        
        circleDef = box2d.b2CircleDef()
        circleDef.radius = 30 / PPM
        circleDef.localPosition.Set(0.0,0.0)       
        circleDef.density = 3.0
        circleDef.restitution = 0.5
        circleDef.friction = 0.5   
        self.body.CreateShape(circleDef) 
        self.body.SetMassFromShapes()
        
        self.destination = None
        self.center = None
            
    def draw(self):
        if not self.destination:
            self.center = toScreen(self.body.GetWorldCenter())
        else:                        
            self.center = curveValue(self.center[0],self.destination[0],5.0),curveValue(self.center[1],self.destination[1],5.0)
        pygame.draw.circle(Globals.game.screen,(0,0,0),self.center,30,3)
            
       

    def moveBy(self,vec):
        self.args[0] = movePt(self.args[0],vec)
        self.reset()
    
    def reset(self):
        self.destination = None
        pt = toWorld(self.args[0])
        self.body.SetXForm(box2d.b2Vec2(*pt),0)
        stopBody(self.body)        
    
    def kill(self):
        ud = self.body.GetUserData()
        returnID(ud['id'])
        Globals.game.world.world.DestroyBody(self.body)                        
        return None
        
class Ramp(Component):
    name = "Ramp"
    
    def __init__(self,pt1,pt2):
        Component.__init__(self,pt1,pt2)
        center = (pt1[0]+pt2[0])/2.0,(pt1[1]+pt2[1])/2.0
        center = toWorld(center)
        self.body = Globals.game.world.addBody(center,self)
        
        boxDef = box2d.b2PolygonDef()
        width = (distance(pt1,pt2)/PPM)/2.0
        height = 8/PPM        
        boxDef.SetAsBox(width,height,box2d.b2Vec2(0,0),getAngle(pt1,pt2))
        boxDef.density = 0
        boxDef.restitution = 0.15
        boxDef.friction = 0.5   
        self.shape = self.body.CreateShape(boxDef)
        self.shape = self.shape.asPolygon()   
        self.body.SetMassFromShapes()
        
    def draw(self):
        points = b2PolyToScreen(self.shape)
        pygame.draw.polygon(Globals.game.screen,(169,129,79),points)

    def moveBy(self,vec):
        self.args[0] = movePt(self.args[0],vec)
        self.args[1] = movePt(self.args[1],vec)
        self.reset()

    def reset(self):
        pt1,pt2 = self.args
        center = (pt1[0]+pt2[0])/2.0,(pt1[1]+pt2[1])/2.0
        center = toWorld(center)
        self.body.SetXForm(box2d.b2Vec2(*center),0)
        stopBody(self.body)
    
    def kill(self):
        ud = self.body.GetUserData()
        returnID(ud['id'])
        Globals.game.world.world.DestroyBody(self.body)               
        return math.ceil(distance(*self.args)/200)

class BouncyBall(Component):
    name = "Bouncy Ball"
    
    def __init__(self,pt):
        Component.__init__(self,pt)
        self.body = Globals.game.world.addBody(toWorld(pt),self)
        
        circleDef = box2d.b2CircleDef()
        circleDef.radius = 20 / PPM
        circleDef.localPosition.Set(0.0,0.0)       
        circleDef.density = 1.0
        circleDef.restitution = 0.8
        circleDef.friction = 0.7   
        self.body.CreateShape(circleDef) 
        self.body.SetMassFromShapes()
        
    def draw(self):
       center = toScreen(self.body.GetWorldCenter())
       pygame.draw.circle(Globals.game.screen,(185,70,192),center,20)

    def moveBy(self,vec):
        self.args[0] = movePt(self.args[0],vec)
        self.reset()

    def reset(self):
        pt = toWorld(self.args[0])
        self.body.SetXForm(box2d.b2Vec2(*pt),0)
        stopBody(self.body)

    def kill(self):
        ud = self.body.GetUserData()
        returnID(ud['id'])
        Globals.game.world.world.DestroyBody(self.body)
        return 1

class Futbol(Component):
    name = "Futbol"
    
    def __init__(self,pt):
        Component.__init__(self,pt)
        self.body = Globals.game.world.addBody(toWorld(pt),self)
        
        circleDef = box2d.b2CircleDef()
        circleDef.radius = 35 / PPM
        circleDef.localPosition.Set(0.0,0.0)       
        circleDef.density = 3.5
        circleDef.restitution = 0.6
        circleDef.friction = 0.5   
        self.body.CreateShape(circleDef) 
        self.body.SetMassFromShapes()
        
    def draw(self):
       center = toScreen(self.body.GetWorldCenter())
       pygame.draw.circle(Globals.game.screen,(36,58,139),center,35)

    def moveBy(self,vec):
        self.args[0] = movePt(self.args[0],vec)
        self.reset()

    def reset(self):
        pt = toWorld(self.args[0])
        self.body.SetXForm(box2d.b2Vec2(*pt),0)
        stopBody(self.body)

    def kill(self):
        ud = self.body.GetUserData()
        returnID(ud['id'])
        Globals.game.world.world.DestroyBody(self.body)
        return 1
        

class BowlingBall(Component):
    name = "Bowling Ball"
    
    def __init__(self,pt):
        Component.__init__(self,pt)
        self.body = Globals.game.world.addBody(toWorld(pt),self)
        
        circleDef = box2d.b2CircleDef()
        circleDef.radius = 40 / PPM
        circleDef.localPosition.Set(0.0,0.0)       
        circleDef.density = 10.0
        circleDef.restitution = 0.05
        circleDef.friction = 0.2   
        self.body.CreateShape(circleDef) 
        self.body.SetMassFromShapes()
        
    def draw(self):
       center = toScreen(self.body.GetWorldCenter())
       pygame.draw.circle(Globals.game.screen,(51,51,51),center,40)    

    def moveBy(self,vec):
        self.args[0] = movePt(self.args[0],vec)
        self.reset()

    def reset(self):
        pt = toWorld(self.args[0])
        self.body.SetXForm(box2d.b2Vec2(*pt),0)
        stopBody(self.body)

    def kill(self):
        ud = self.body.GetUserData()
        returnID(ud['id'])
        Globals.game.world.world.DestroyBody(self.body)             
        return 1  

class SeeSaw(Component):
    name = "See Saw"
        
    @classmethod
    def getTriangleAndRect(self,pt):
        x,y = pt
        triangle = (
        (x-50,y+0.866025*100),
        (x+50,y+0.866025*100),
        (x,y)
        )
        rect = pygame.Rect(x-200,y-26,400,26)
        return triangle,rect
    
    def __init__(self,pt):       
        Component.__init__(self,pt)
        self.triangle,self.rect = SeeSaw.getTriangleAndRect(pt)
        
        # fulcrum       
        center = toWorld(util_poly.calc_center(self.triangle))
        self.base = Globals.game.world.addBody(center,self) 
        self.base.GetUserData()['parent'] = self                                       
        triangle = [(-1,-0.577),(1,-0.577),(0,1.155)]                                                
        polyDef = box2d.b2PolygonDef()
        polyDef.setVertices_tuple(triangle)        
        polyDef.density = 0
        polyDef.restitution = 0.15
        polyDef.friction = 0.5   
        self.baseShape = self.base.CreateShape(polyDef)
        self.baseShape = self.baseShape.asPolygon()   
        self.base.SetMassFromShapes()
        
        # box
        center = toWorld(self.rect.center)        
        self.box = Globals.game.world.addBody(center,self)
        self.box.GetUserData()['parent'] = self
        boxDef = box2d.b2PolygonDef()
        width = (self.rect.width/PPM)/2.0
        height = (self.rect.height/PPM)/2.0        
        boxDef.SetAsBox(width,height)
        boxDef.density = 2.0
        boxDef.restitution = 0.15
        boxDef.friction = 0.5   
        self.boxShape = self.box.CreateShape(boxDef)
        self.boxShape = self.boxShape.asPolygon()   
        self.box.SetMassFromShapes()
        
        
        #box's joint        
        jointDef = box2d.b2RevoluteJointDef()
        jointDef.Initialize(Globals.game.world.world.GetGroundBody(), self.box, box2d.b2Vec2(*toWorld(self.rect.midbottom)))       
        self.joint=Globals.game.world.world.CreateJoint(jointDef).getAsType()                                  
    
    def draw(self):
        points = b2PolyToScreen(self.baseShape)
        pygame.draw.polygon(Globals.game.screen,(202,17,17),points)
        points = b2PolyToScreen(self.boxShape)
        pygame.draw.polygon(Globals.game.screen,(242,218,15),points)

    def moveBy(self,vec):
        self.args[0] = movePt(self.args[0],vec)
        self.reset()

    def reset(self):
        self.triangle, self.rect = self.getTriangleAndRect(self.args[0])
        pt = toWorld(util_poly.calc_center(self.triangle))
        self.base.SetXForm(box2d.b2Vec2(*pt),0)
        stopBody(self.base)
        pt = toWorld(self.rect.center)
        self.box.SetXForm(box2d.b2Vec2(*pt),0)
        stopBody(self.box)   
        Globals.game.world.world.DestroyJoint(self.joint)
        jointDef = box2d.b2RevoluteJointDef()
        jointDef.Initialize(Globals.game.world.world.GetGroundBody(), self.box, box2d.b2Vec2(*toWorld(self.rect.midbottom)))       
        self.joint=Globals.game.world.world.CreateJoint(jointDef).getAsType()            

    def kill(self):
        ud = self.base.GetUserData()
        returnID(ud['id'])
        Globals.game.world.world.DestroyBody(self.base)               
        ud = self.box.GetUserData()
        returnID(ud['id'])
        Globals.game.world.world.DestroyBody(self.box)
        return 1
                 


class Fan(Component):
    name = "Fan"
   
    def __init__(self,pt):
        Component.__init__(self,pt)     
        center = toWorld(pt)
        self.body = Globals.game.world.addBody(center,self)
        
        boxDef = box2d.b2PolygonDef()
        width = 50/PPM
        height = 13/PPM        
        boxDef.SetAsBox(width,height)
        boxDef.density = 0
        boxDef.restitution = 0.15
        boxDef.friction = 0.5   
        self.baseShape = self.body.CreateShape(boxDef)
        self.baseShape = self.baseShape.asPolygon()

        # sprite representation
        img = loadSVG("fan.svg")
        self.sprite = SVGSprite(svg=img,size=(100,0))
        self.sprite.add(Globals.game.allSprites)

        boxDef = box2d.b2PolygonDef()        
        boxDef.SetAsBox(50/PPM,200/PPM,box2d.b2Vec2(0,200/PPM),0)
        boxDef.density = 0     
        boxDef.isSensor = True      
        self.sensorShape = self.body.CreateShape(boxDef)
        self.sensorShape = self.sensorShape.asPolygon()        
        self.body.SetMassFromShapes()
        Globals.game.world.contactListener.connect(self.body,self.handleContact)
        #self.channel = None
        #self.active = False
        
    def draw(self):
        self.sprite.rect.center = toScreen(self.body.GetWorldCenter())
        """
        if self.active:
            if not self.channel:
                self.channel = Globals.game.allSounds['fan.wav'].play(-1)
            if not self.channel.get_busy(): self.channel.play(Globals.game.allSounds['fan.wav'],-1)
        else:
            if self.channel:
                self.channel.stop()
        """        

    def handleContact(self,contactType,point):                 
        #self.active = False
        if contactType == "Add" or contactType == "Persist":            
            if point.shape1.GetBody().GetUserData()['id'] == self.body.GetUserData()['id']:
                body = point.shape2.GetBody()
            else:
                body = point.shape1.GetBody()            
            force = (1-((point.position.y - self.body.GetWorldCenter().y) / (400 / PPM))) * 200
            force = box2d.b2Vec2(0.0,force)
            body.ApplyForce(force,point.position)
            #self.active = True 
                      
    def moveBy(self,vec):
        self.args[0] = movePt(self.args[0],vec)
        self.reset()
    

    def reset(self):
        pt = toWorld(self.args[0])
        self.body.SetXForm(box2d.b2Vec2(*pt),0)
        stopBody(self.body)
        

    def kill(self):
        ud = self.body.GetUserData()
        returnID(ud['id'])
        Globals.game.world.contactListener.disconnect(self.body)
        Globals.game.world.world.DestroyBody(self.body)
        self.sprite.kill()                  
        return 1

# -----------------------------------------                               
def getAllComponents():
    this_mod = __import__(__name__)
    all = [val for val in this_mod.__dict__.values() if isinstance(val, type)]
    allComp = []
    for a in all:
        if getmro(a).__contains__(Component) and a!= Component: allComp.append(a)
    return allComp

allComponents = getAllComponents()                         
