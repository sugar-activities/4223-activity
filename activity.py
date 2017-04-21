import tools
import components
import olpcgames
import pygame
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.combobox import ComboBox
from sugar.graphics.toolcombobox import ToolComboBox
from sugar.graphics.objectchooser import ObjectChooser
from sugar.activity import activity
from gettext import gettext as _
import gtk
import os
import pickle
 
class X2OActivity(olpcgames.PyGameActivity):
    game_name = 'x2o'
    game_title = 'x2o'
    game_size = None # olpcgame will choose size

    # setup the toolbar
    def build_toolbar(self):        
        # make a toolbox
        toolbox = activity.ActivityToolbox(self)
         
        # modify the Activity tab
        activity_toolbar = toolbox.get_activity_toolbar()
        activity_toolbar.share.props.visible = False
        self.activity_toolbar = activity_toolbar
         
        # make the toolbars
        toolbars = {}
        for b in tools.allButtons:
            if not toolbars.has_key(b.toolBar):
                toolbars[b.toolBar] = gtk.Toolbar()                               
                
        # make + add the buttons
        self.buttonList = {}
        for c in tools.allButtons:                               
            button = ToolButton(c.icon)
            button.set_tooltip(_(c.toolTip))
            button.connect('clicked',self.buttonClicked)
            toolbars[c.toolBar].insert(button,-1)    
            button.show()            
            self.buttonList[button] = c.name        
        
        # add the toolbars to the toolbox
        for bar in toolbars:
            toolbox.add_toolbar(bar,toolbars[bar])
            toolbars[bar].show()                   
        
        # make the level chooser combo box
        lbl = gtk.Label("Load a level: ")
        lbl.show()
        cmb = ComboBox()
        cmb.connect('changed',self.levelChanged)
        files = os.listdir("levels")        
        for i in files:
            if i[-6:] == ".level":
                f = open("levels/"+i)
                try:
                    n = pickle.load(f)['name']
                except:
                    continue
                f.close()
                cmb.append_item("levels/"+i,n)              
                               
        cmb = ToolComboBox(cmb)
        lbl_ti = gtk.ToolItem()
        lbl_ti.add(lbl)        
        toolbars['Run'].insert(lbl_ti,-1)
        lbl_ti.show()
        toolbars['Run'].insert(cmb,-1)
        cmb.show()
        button = ToolButton("load")
        button.set_tooltip(_("Load your own level"))
        button.connect('clicked',self.loadButtonClicked)
        toolbars['Run'].insert(button,-1)    
        button.show()                          
       
        # add some level saving stuff to the save toolbar

        
        self.quantBox = ComboBox()
        self.quantBox.connect('changed',self.quantBoxChanged)
        self.quantBoxIndexes = {}
        for i in range(26):
            self.quantBox.append_item(i,str(i))
            self.quantBoxIndexes[i] = i
        self.quantBox.append_item(float('inf'),"Infinity")
        self.quantBoxIndexes[float('inf')] = 26
        cmb = ToolComboBox(self.quantBox)
        activity_toolbar.insert(cmb,1)
        cmb.show()                        

        cmb = ComboBox()
        cmb.connect('changed',self.compQuantBoxChanged)
        for c in components.allComponents:
            if c.name != "X" and c.name != "O":
                cmb.append_item(c.name,c.name)
        cmb = ToolComboBox(cmb)
        activity_toolbar.insert(cmb,1)
        cmb.show()

        lbl = gtk.Label(" Component amounts: ")
        lbl.show()
        ti = gtk.ToolItem()
        ti.add(lbl)
        activity_toolbar.insert(ti,1)
        ti.show()


                
        toolbox.show()
        self.set_toolbox(toolbox)
        toolbox.set_current_toolbar(1)
        
        return activity_toolbar
     
    def buttonClicked(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action=self.buttonList[button]))
    
    def compQuantBoxChanged(self,cmb):
        pygame.event.post(olpcgames.eventwrap.Event("UpdateCompQuantBox", action=cmb.props.value))
    
    def quantBoxChanged(self,cmb):
        pygame.event.post(olpcgames.eventwrap.Event("UpdateQuantBox", action=cmb.props.value))        
    
    def levelChanged(self,cmb):
        event = olpcgames.eventwrap.Event(
            type = pygame.USEREVENT,
            code = olpcgames.FILE_READ_REQUEST,
            filename = cmb.props.value,
            metadata = None,
        )
        olpcgames.eventwrap.post( event )
                    
    def loadButtonClicked(self,button):        
        chooser = ObjectChooser('Pick a level', self, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        try:
            result = chooser.run()
            if result == gtk.RESPONSE_ACCEPT:
                jobject = chooser.get_selected_object()
                if jobject and jobject.file_path:
                    event = olpcgames.eventwrap.Event(
                        type = pygame.USEREVENT,
                        code = olpcgames.FILE_READ_REQUEST,
                        filename = jobject.file_path,
                        metadata = jobject.metadata,
                    )
                    olpcgames.eventwrap.post( event )
                    event.block()
        finally:
            chooser.destroy()
            del chooser        
        
        
        