from kivy.uix.widget import Widget
from kivy.uix.image import Image
#from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import BooleanProperty, NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.logger import Logger
from kivy.clock import Clock

class SimpleSprite(Widget):
    color = ObjectProperty(None)
    shape = ObjectProperty(None)
    speed = ObjectProperty(None)
# ------------------------------------------------------    
    def set_variables(self,size,pos,color,speed,shape,size_hint,obstacle):
        self.obstacle = obstacle
        self.speed = speed
        self.color = color
        self.size_hint = size_hint
        if shape != None:
            try:
                self.pos = shape.pos
                self.size = shape.size
                self.shape = shape
            except Exception:
                pass
        else:
            self.size = size
            self.pos = pos
            self.shape = self.default_shape()
# ------------------------------------------------------
    def __init__(self,size=(16,16),pos=(0,0),color=Color(0,0,0,0),speed = 1,shape=None,size_hint = (1,1),obstacle=False):
        super().__init__()
        self.set_variables(size=size,pos=pos,color=color,speed=speed,shape=shape,size_hint=size_hint,obstacle=obstacle)
        self.init_canvas()
        self.post_init()
# ------------------------------------------------------
    def post_init(self):
        pass        
# ------------------------------------------------------
    def init_canvas(self):
        self.canvas.clear()
        self.canvas.add(self.color)
        self.canvas.add(self.shape)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)        
# ------------------------------------------------------
    def update_canvas(self, *args):
        try:
            self.update_shape()
        except Exception:
            print('sprite',self,'failed to update_shape')       
# ------------------------------------------------------
    def update_shape(self):
        self.shape.pos = self.pos
        self.shape.size = self.size
# ------------------------------------------------------
    def default_shape(self):
        s = Rectangle(size=self.size,pos=self.pos) 
        return s
# ------------------------------------------------------
    def move(self,vector,speed=0):
        if speed == 0:
            speed = self.speed
        if (vector != (0,0)) and (speed != 0):
            try:
                dx = vector[0] * speed
                dy = vector[1] * speed
            except Exception:
                dx = 0
                dy = 0
            x = self.pos[0] + dx
            y = self.pos[1] + dy
            self.pos = (x,y)
# ------------------------------------------------------
    def moveTo(self,pos):
        self.pos = (pos)          

# ######################################################
class Cell(SimpleSprite):
# ------------------------------------------------------
    def __init__(self,size=(16,16),pos=(0,0),color=Color(0,0,0,0)):
        super().__init__(size=size,pos=pos,color=color)
      
# ######################################################
class Sprite(Image):
    transparentcolor = ObjectProperty(None) 
    speed = ObjectProperty(None)
    collider = ObjectProperty(None)
    moving = ObjectProperty(None)
# ------------------------------------------------------
    def __init__(self,source,pos,size,size_hint=(None,None),allow_stretch=False,keep_ratio=True,speed=1,altSources=[], **kwargs):
        super().__init__(size=size,pos=pos,source=source,allow_stretch=allow_stretch, keep_ratio=keep_ratio,**kwargs)
        self.sources = altSources
        self.sources.insert(0,source)
        self.transparentcolor = Color(0,0,0,0)
        self.speed = speed
        self.init_collider()  
        self.init_image_animation()    
# ------------------------------------------------------
    def set_animation(self, index):
        if index >= len(self.sources):
            index = 0
        self.source = self.sources[index]

#------------------------------------------------------
    def init_image_animation(self):
        self.moving = False
        self.anim_delay = -1
        self.anim_loop = 0 
# ------------------------------------------------------
    def start_animating(self):
        if self.anim_delay == -1:
            self.anim_delay = .5 / self.speed
            self.anim_loop = 0            
# ------------------------------------------------------
    def stop_animating(self):
        self.anim_delay = -1

# ------------------------------------------------------
    def init_collider(self):
        ##print('initializing collider')
        if self.collider != None:
            self.remove_widget(self.collider)
        self.collider = SimpleSprite(color=self.transparentcolor,speed=self.speed,size_hint=self.size_hint)
        self.add_widget(self.collider)
# ------------------------------------------------------
    def check_collision(self,widget,vector):
        newvector = vector
        if newvector != (0,0):
            c = self.collider
            c.speed = self.speed
            c.pos = ((self.pos[0]+2),(self.pos[1]+2))
            c.size = ((self.size[0]-2),(self.size[1]-2))
            # First pass
            newvector = self.get_collision_vector(collider=c, widget=widget, vector=vector, divisor=1)
            # if c.speed > 1 and newvector == (0,0):
            #     # Second pass
            #     newvector = self.get_collision_vector(collider=c, widget=widget, vector=vector, divisor=2)       
        return newvector
# ------------------------------------------------------ 
    def get_collision_vector(self, collider, widget, vector, divisor):
        c = collider
        newvector = ((vector[0] / divisor),(vector[1] / divisor))
        oldpos = c.pos
        c.move(vector=newvector)
        #Logger.debug('Checking collissions with widget {} and vector {}'.format(widget, newvector))
        if (c.collide_widget(widget)):
            #Logger.debug('Collided with {}'.format(widget))
            newvector = (0,(vector[1]/divisor))
            #Logger.debug('Checking collissions with vector {}'.format(newvector))
            c.moveTo(oldpos)
            c.move(vector=newvector)
            if (c.collide_widget(widget)):
                #Logger.debug('Collided with {}'.format(widget))
                newvector = (vector[0]/divisor,0)
                c.moveTo(oldpos)
                c.move(vector=newvector)
                #Logger.debug('Checking collissions with vector {}'.format(newvector))
                if (c.collide_widget(widget)):
                    #Logger.debug('Collided with {}'.format(widget))
                    newvector=(0,0)
                    c.moveTo(oldpos)
        c.moveTo(oldpos)  
        return newvector        

# ------------------------------------------------------        
    def move(self,vector):
        if (vector != (0,0)):
            if len(self.sources) > 1:
                if (vector[0] < 0) or (vector[1] > 0):
                    self.set_animation(0)   # left or up
                else:
                    self.set_animation(1)   # right or down
            s = self.speed
            try:
                dx = vector[0] * s
                dy = vector[1] * s
            except Exception:
                dx = 0
                dy = 0
            x = self.pos[0] + dx
            y = self.pos[1] + dy
            self.pos = (x,y)
            self.moving = True
            self.start_animating()
        else:
            self.moving = False
            self.stop_animating()
# ------------------------------------------------------
    def moveTo(self,pos):
        self.pos = (pos)   

# ######################################################
class Wall(Image):
    blockHoriz = ObjectProperty(None)
    blockVert = ObjectProperty(None)     
# ------------------------------------------------------
    def __init__(self,size=(3,15),pos=(0,0),source=None,allow_stretch=True,keep_ratio=False,obstacle=True):
        super().__init__(source=source,pos=pos,size=size,allow_stretch=allow_stretch,keep_ratio=keep_ratio)
        self.obstacle = obstacle
        self.blockVert = False
        self.blockHoriz = True        

# ######################################################
class Floor(Image):
    blockHoriz = ObjectProperty(None)
    blockVert = ObjectProperty(None) 
# ------------------------------------------------------
    def __init__(self,size=(15,13),pos=(0,0),source=None,allow_stretch=True,keep_ratio=False,obstacle=True):
        super().__init__(source=source,pos=pos,size=size,allow_stretch=allow_stretch,keep_ratio=keep_ratio)
        self.obstacle = obstacle
        self.blockHoriz = False
        self.blockVert = True

# ######################################################
class Ball(Sprite):
    id = ObjectProperty(None)
    def __init__(self,size_hint=(None,None),speed = 2,pos=(0,0), size=(16,16),source=None,**kwargs):
        super().__init__(size_hint=size_hint,speed=speed,pos=pos,size=size,source=source,**kwargs)
        self.id='ball'
        self.anim_delay = -1

# ######################################################
class Goal(Image):  
    id = ObjectProperty(None)
    def __init__(self, size=(16,16),pos=(0,0), source=None, allow_stretch=True, keep_ratio = True):
        super().__init__(size=size,pos=pos,source=source,allow_stretch=allow_stretch, keep_ratio=keep_ratio)
        self.id='goal'
        self.anim_delay = -1
    
    def flash(self, anim_loop = 3, anim_delay = 0.18):
        self.anim_delay = anim_delay
        self.anim_loop = anim_loop




          

