#All the box2d and physics related code lives here

from core import Globals
import box2d
import random
from math import sqrt


PPM = 50.0
SCREENHEIGHT = None
ITERATIONS = 10

usedIDs = [None]

def getID():
    i = None
    while i in usedIDs:
        i = random.randint(1,10000000)
    usedIDs.append(i)
    return i

def returnID(i):
    usedIDs.remove(i)    
    

def toWorld(vec):   
    x,y = vec
    x /= PPM
    y = SCREENHEIGHT - y
    y /= PPM
    return x,y
    
def toScreen(vec):
    if not isinstance(vec,tuple):
        vec = vec.tuple()
    x,y = vec
    x *= PPM
    y *= PPM     
    y = SCREENHEIGHT - y
    return x,y    

def b2PolyToScreen(shape):
    points = []
    for i in xrange(shape.GetVertexCount()):
        pt = box2d.b2Mul(shape.GetBody().GetXForm(), shape.getVertex(i))
        pt = toScreen(pt)           
        points.append(pt) 
    return points   

def stopBody(body):        
    z = box2d.b2Vec2(0,0)
    body.SetLinearVelocity(z)
    body.SetAngularVelocity(0)

class PhysicsSimulator(object):
    def __init__(self):
        global SCREENHEIGHT
        SCREENHEIGHT = Globals.game.screen.get_size()[1]
        
        # set up box2D    
        worldAABB=box2d.b2AABB()
        worldAABB.lowerBound.Set(-100, -100)
        worldAABB.upperBound.Set(100, 100)
        gravity = box2d.b2Vec2(0, -10)
        self.world = box2d.b2World(worldAABB, gravity, True)
        
        self.timeStep = 1.0/60
        self.run = True
        
        self.contactListener = X2OContactListener()
        self.world.SetContactListener(self.contactListener)
        
        self.makeBoundingBox()
                                
        # callbacks stored as {body id to watch : function to call}
        # function will be passed the contact type as a string and the contact point object
        
    def update(self):
        if self.run:
            self.world.Step(self.timeStep, ITERATIONS)
    
    def addBody(self,pos,parent):
        bodyDef = box2d.b2BodyDef()
        bodyDef.position.Set(*pos)        
        bodyDef.userData = {'parent':parent, 'id':getID()}
        bodyDef.sleepFlag = True
        bodyDef.UserData = {}
        return self.world.CreateBody(bodyDef)
    
    def makeBoundingBox(self):        
                 
        body = self.addBody((0,80),self)
        boxDef = box2d.b2PolygonDef()
        width = 80
        height = 5        
        boxDef.SetAsBox(width,height)
        boxDef.density = 0           
        body.CreateShape(boxDef)
        
        body = self.addBody((0,-80),self)           
        body.CreateShape(boxDef)
        
        body = self.addBody((-80,0),self)
        boxDef = box2d.b2PolygonDef()
        width = 5
        height = 80        
        boxDef.SetAsBox(width,height)
        boxDef.density = 0           
        body.CreateShape(boxDef)
    
        body = self.addBody((80,0),self)     
        body.CreateShape(boxDef)    
    
    def bodiesAtPoint(self,pt,include_static=False,include_sensor=False):
        # modified from the elements source
        # thanks guys!
        
        sx,sy = toWorld(pt)
        f = 0.01
    
        AABB=box2d.b2AABB()
        AABB.lowerBound.Set(sx-f, sy-f);
        AABB.upperBound.Set(sx+f, sy+f);
    
        amount, shapes = self.world.Query(AABB, 2)
    
        if amount == 0:
            return False
        else:
            bodylist = []
            for s in shapes:                
                if s.IsSensor() and not include_sensor: continue
                body = s.GetBody()
                if not include_static:
                    if body.IsStatic() or body.GetMass() == 0.0:
                        continue
                        
                if s.TestPoint(body.GetXForm(), box2d.b2Vec2(sx, sy)):
                    bodylist.append(body)
    
            return bodylist        
        


class X2OContactListener(box2d.b2ContactListener):
    def __init__(self): 
        super(X2OContactListener, self).__init__()
        self.callbacks = {} 
    
    def connect(self,body,cb):
        self.callbacks[body.GetUserData()['id']] = cb
        
    def disconnect(self,body):
        if self.callbacks[body.GetUserData()['id']]:
            del self.callbacks[body.GetUserData()['id']]
    
    def Add(self, point):       
        b1 = point.shape1.GetBody().GetUserData()['id']
        b2 = point.shape2.GetBody().GetUserData()['id']              
        
        if self.callbacks.has_key(b1):                       
            self.callbacks[b1]("Add",point)
        if self.callbacks.has_key(b2):
            self.callbacks[b2]("Add",point) 
        
        # contact sounds
        #if not (point.shape1.IsSensor() or point.shape2.IsSensor()):
        #    vol = sqrt(point.velocity.Length())/30.0
        #    Globals.game.allSounds["pop.ogg"].set_volume(vol)
        #    Globals.game.allSounds["pop.ogg"].play()
            
        
    def Persist(self, point):
        b1 = point.shape1.GetBody().GetUserData()['id']
        b2 = point.shape2.GetBody().GetUserData()['id']              
        
        if self.callbacks.has_key(b1):                       
            self.callbacks[b1]("Persist",point)
        if self.callbacks.has_key(b2):
            self.callbacks[b2]("Persist",point) 
        

        
    def Remove(self, point):
        b1 = point.shape1.GetBody().GetUserData()['id']
        b2 = point.shape2.GetBody().GetUserData()['id']              
        
        if self.callbacks.has_key(b1):                       
            self.callbacks[b1]("Remove",point)
        if self.callbacks.has_key(b2):
            self.callbacks[b2]("Remove",point) 
        
    def Result(self, point):
        b1 = point.shape1.GetBody().GetUserData()['id']
        b2 = point.shape2.GetBody().GetUserData()['id']              
        
        if self.callbacks.has_key(b1):                       
            self.callbacks[b1]("Result",point)
        if self.callbacks.has_key(b2):
            self.callbacks[b2]("Result",point) 

        