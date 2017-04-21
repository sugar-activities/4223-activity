#!/usr/bin/python
#==================================================================
#                             x2o.activity
#                           By Alex Levenson
#==================================================================
import pygame
from pygame.locals import *
from pygame.color import *
import olpcgames
from util import *
from core import *
import components
import tools
import pickle
import os
import physics
import pygtk,gtk

class X2OGame: 
    def __init__(self,screen):
        Globals.game = self
        self.screen = screen
        
        # get everything set up
        self.clock = pygame.time.Clock()
        self.canvas = olpcgames.ACTIVITY.canvas
        self.font = pygame.font.Font(None, 40) # font object
        
        self.infoBarRect = pygame.Rect(0,0,self.screen.get_size()[0],40)
        self.allSprites = pygame.sprite.Group()
                
        self.toolList = {}
        for c in tools.allTools:                                     
            self.toolList[c.name] = c()
            
        self.componentList = {}
        self.saveQuantities = {}
        for c in components.allComponents:                  
            self.componentList[c.name] = c 
            self.saveQuantities[c.name] = 0
                         
        self.currentTool = self.toolList["RampTool"]
        self.currentSaveComp = None
        
        self.world = physics.PhysicsSimulator()
        self.world.run = False
        
        self.levelData = {}
        self.userComponents = []
        self.levelComponents = []              

        
        # load all the sounds for use throughout the game
        self.allSounds = {"ouch.wav":loadSound("sounds/ouch.wav")}
        #for s in os.listdir("sounds"):
        #    self.allSounds[s] = loadSound("sounds/"+s)
                
    def load(self,event):
        try:
            f = open(event.filename)
        except:
            print "Invalid file"
            return
        # first kill all existing components
        for c in (self.userComponents + self.levelComponents):
            c.kill()
        self.userComponents = []
        self.levelComponents = []        
        for k in self.saveQuantities:
            self.saveQuantities[k] = 0
        
        # load a level stored as a pickle of a dictionary
        
        self.levelData = pickle.load(f)     
        f.close()
        
        self.loadQuantities()
        
        self.loadComponents()                  
    
    def resetLevel(self):
        # resets the level to it's state at load time + user's additions
        
        # call all component's reset command
        for c in (self.userComponents+self.levelComponents):            
            c.reset()
                    
        
               
    def revertLevel(self):
        # resets the level to it's state at load time
        
        # tell the user components to kindly delete themselves (except the x and o)
        xo = []
        for c in self.userComponents:
            if not (c.name == "X" or c.name == "O"):
                c.kill()
            else:
                xo.append(c)                
        self.userComponents = xo
        
        # call all level component's reset command
        for c in (self.levelComponents+self.userComponents):            
            c.reset()
            
        # reset component quantities
        self.loadQuantities()
                    
    
    def loadComponents(self):
        for c in self.levelData['initialComponents']:
            if self.componentList.has_key(c):
                if (c == "X" or c == "O") and not self.levelData['XOLocked']:
                    complist = self.userComponents
                else:
                    complist = self.levelComponents
                for x in self.levelData['initialComponents'][c]:                    
                    complist.append(self.componentList[c](*x))
                                           
                        
    def loadQuantities(self):
        for q in self.levelData['componentQuantities']:
            if self.componentList.has_key(q):
                if hasattr(self.componentList[q],"amountLeft"):
                    self.componentList[q].amountLeft = self.levelData['componentQuantities'][q]
    
    
    def save(self,event):
        self.resetLevel()
        data = {}
        data['name'] = olpcgames.ACTIVITY.activity_toolbar.title.props.text      
        data['componentQuantities'] = self.saveQuantities
        data['initialComponents'] = {}
        for k in components.allComponents:
            data['initialComponents'][k.name] = []
        
        for c in (self.levelComponents + self.userComponents):
            data['initialComponents'][c.name].append(c.args)
        
        data['XOLocked'] = True
        
        f= open(event.filename,"w")        
        pickle.dump(data,f)
        f.close()                                    
    def run(self):         
        class editorEvent:
            filename = "levels/editor.level"
        self.load(editorEvent)                  
        self.running = True    
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    # bye bye! Hope you had fun!
                    self.running = False
                    break
                elif event.type == USEREVENT:
                    if hasattr(event,"action"):                        
                        if self.toolList.has_key(event.action):
                            self.currentTool.cancel()
                            self.currentTool = self.toolList[event.action]
                            self.world.run = False
                            self.resetLevel()
                        elif event.action == "playpause":
                            self.currentTool.cancel()
                            self.world.run = True
                        elif event.action == "reset":
                            self.currentTool.cancel()
                            self.resetLevel()     
                            self.world.run = False                       
                        elif event.action == "revert":
                            self.currentTool.cancel()
                            self.revertLevel()
                            self.world.run = False
                        elif event.action == "unlock":
                            self.userComponents += self.levelComponents
                            self.levelComponents = []
                    elif hasattr(event,"code"):
                        if event.code == olpcgames.FILE_WRITE_REQUEST:
                            self.currentTool.cancel()
                            self.save(event)
                            self.world.run = False 
                        if event.code == olpcgames.FILE_READ_REQUEST:
                            self.currentTool.cancel()
                            self.load(event)
                            self.world.run = False                        
                elif event.type == "UpdateCompQuantBox":
                    self.currentSaveComp = event.action
                    i = olpcgames.ACTIVITY.quantBoxIndexes[self.saveQuantities[self.currentSaveComp]]
                    olpcgames.ACTIVITY.quantBox.set_active(i)
                elif event.type == "UpdateQuantBox":
                    if self.currentSaveComp:
                        self.saveQuantities[self.currentSaveComp] = event.action                          
                            
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.canvas.grab_focus()
                
                # now, if we've made it this far, send the event on to the current tool
                if not self.world.run: self.currentTool.handleEvent(event)
            
            
            # Clear Display
            self.screen.fill((255,255,255))
                   
            # Update & Draw World
            self.world.update()
            
            for c in (self.userComponents + self.levelComponents):
                c.draw()
            
            self.allSprites.draw(self.screen)            
           
            # draw the current tool's effects
            if not self.world.run:
                self.currentTool.draw()
            
            # draw the 'info' bar
            self.screen.fill((100,100,255),self.infoBarRect)
            caption = self.currentTool.caption
            if hasattr(self.currentTool,"component"):
                caption +=" " + str(round(self.currentTool.component.amountLeft))
            text = self.font.render(caption, True, (255,255,255))
            textpos = text.get_rect(left=0,top=7)
            self.screen.blit(text,textpos)  
            
            # Flip Display
            pygame.display.flip()  
            
            # Try to stay at 30 FPS
            self.clock.tick(30) # originally 50    
        
def main():

    toolbarheight = 75
    tabheight = 45
    pygame.init()
    pygame.display.init()
    x,y  = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode((x,y-toolbarheight-tabheight))
    # create an instance of the game
    game = X2OGame(screen)    
    # start the main loop
    game.run()

# function for loading sounds (mostly borrowed from Pete Shinners pygame tutorial)
def loadSound(name):
    # if the mixer didn't load, then create an empy class that has an empty play method
    # this way the program will run if the mixer isn't present (sans sound)
    class NoneSound:
        def play(self): pass
        def set_volume(self): pass
    if not pygame.mixer:
        return NoneSound()
    try:
        sound = pygame.mixer.Sound(name)
    except:
        print "error with sound: " + name
        return NoneSound()
        
    return sound

# make sure that main get's called
if __name__ == '__main__':
    main()

