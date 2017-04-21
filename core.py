import pygame
from util import loadSVG
from olpcgames.svgsprite import SVGSprite

# HAAAAAAAAAAAACK for making game instance global
class Globals():
    game = None 


# the X that the O needs to hit to win a level        
class TheX(object):
    
    def __init__(self,rect,game):
        self.game = game
        self.resetRect = pygame.Rect(rect)
        self.rect = rect
        self.body = self.game.world.add.sensorBox(rect,self.onHit)
        self.body.GetUserData()['type'] = "TheX"
        img = loadSVG("x.svg")
        self.sprite = SVGSprite(svg=img,size=(rect.width,rect.height))
        self.sprite.rect.center = rect.center
        self.sprite.add(game.componentSprites)        
    
    def onHit(self,c):        
        bodies = (c.shape1.GetBody().GetUserData(),c.shape2.GetBody().GetUserData())
        for d in bodies: 
            if d.has_key('type'):
                if d['type'] == "TheO":      
                    self.game.world.run_physics = False
                    break
    def update(self):
        c = self.body.GetPosition()
        self.rect.center = (c.x*self.game.world.ppm,self.game.screen.get_size()[1]-(c.y*self.game.world.ppm))
        self.sprite.rect.center = self.rect.center                 
            
# the O that needs to hit the X to win a level

class TheO(object):
    def __init__(self,rect,game):
        self.game = game
        self.rect = rect
        self.resetRect = pygame.Rect(rect)
        self.body = self.game.world.add.ball(rect.center, self.rect.width/2, dynamic=True, density=2.0)
        self.body.GetUserData()['visible'] = False
        self.body.GetUserData()['type'] = "TheO"
        img = loadSVG("o.svg")
        self.sprite = SVGSprite(svg=img,size=(rect.width,rect.height))
        self.sprite.rect.center = rect.center
        self.sprite.add(game.componentSprites)
    
    def update(self):
        c = self.body.GetPosition()
        self.rect.center = (c.x*self.game.world.ppm,self.game.screen.get_size()[1]-(c.y*self.game.world.ppm))
        self.sprite.rect.center = self.rect.center 
