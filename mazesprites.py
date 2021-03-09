from kivy.uix.widget import Widget
from kivy.uix.image import Image
#from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import BooleanProperty, NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.logger import Logger
from kivy.clock import Clock

import concurrent.futures as cf

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
        if self.collider != None:
            self.remove_widget(self.collider)
        self.collider = SimpleSprite(color=self.transparentcolor,speed=self.speed,size_hint=self.size_hint)
        self.collider.pos = self.pos #((self.pos[0]+4),(self.pos[1]+4))
        self.collider.size = self.size #((self.size[0]-4),(self.size[1]-4))
        self.add_widget(self.collider)
# ------------------------------------------------------        
    def move(self,vector,obstacles=[]):
        if vector == (None,None):
            return
        # multiply vector times speed
        s = self.speed
        dx = vector[0] * s
        dy = vector[1] * s
        adjvector = (dx,dy)
        # check for obstacles
        newvector = self.check_collisions(adjvector,obstacles)
        Logger.debug('move: newvector={}'.format(newvector))
        if (newvector != (0,0)):
            # handle animation if any
            self.select_animation(newvector)
            dx = newvector[0]
            dy = newvector[1]
            x = self.pos[0] + dx
            y = self.pos[1] + dy
            self.pos = (x,y)
            self.collider.pos = (x,y)
            self.moving = True
            self.start_animating()
        else:
            self.moving = False
            self.stop_animating()
# ------------------------------------------------------
    def moveTo(self,pos):
        self.pos = (pos)
# ------------------------------------------------------
    def select_animation(self, vector):
        if len(self.sources) > 1:
            if (vector[0] < 0) or (vector[1] > 0):
                self.set_animation(0)   # left or up
            else:
                self.set_animation(1)   # right or down
# ------------------------------------------------------
    def check_collisions(self,vector,obstacles):
        newvector = vector
        c = self.collider    
        c.pos = self.pos
        collisions = []
        c.move(vector, speed=1)      #vector has already been adjusted for speed
        for item in obstacles:
            if c.collide_widget(item):
                collisions.append(item)
                Logger.debug('collided with {}'.format(item))
        futures = []
        c.pos = self.pos                   
        with cf.ThreadPoolExecutor() as executor:
            for item in collisions:
                futures.append(executor.submit(self.get_collision_vector, c, item, vector))
        vectors = []
        for future in cf.as_completed(futures):
            pv = future.result()
            vectors.append(pv)
            if pv == (0,0):
                newvector = pv
                break
        newx=vector[0]
        newy=vector[1]
        for v in vectors:
            Logger.debug('v={}'.format(v))
            if newx != 0 and abs(newx) > abs(v[0]):
                newx = v[0]
            if newy != 0 and abs(newy) > abs(v[1]):
                newy = v[1]
        newvector = (newx,newy)
        return newvector            
# ------------------------------------------------------ 
    def get_collision_vector(self, collider, widget, vector):
        c = collider
        oldpos = c.pos
        clear = False
        newvector = self.decrement_vector(vector)
        Logger.debug('decrementing to {}'.format(newvector))
        while newvector != (0,0) and not clear:
            c.moveTo(oldpos)
            c.move(vector=newvector,speed=1)           
            if (c.collide_widget(widget)):
                newvector = self.decrement_vector(vector)
                Logger.debug('decrementing to {}'.format(newvector))
            else:
                clear = True 
        c.moveTo(oldpos) 
        Logger.debug('return vector {}'.format(newvector)) 
        return newvector    
# ------------------------------------------------------ 
    def decrement_vector(self, vector):
        newx = vector[0]
        newy = vector[1]
        Logger.debug('before decrementing: newx={}  newy={}',format(newx,newy))
        if newx < 0:
            newx = newx + 1
        elif newx > 0:
            newx = newx - 1
        if newy < 0:
            newy = newy + 1
        elif newy > 0:
            newy = newy - 1 
        Logger.debug('after decrementing: newx={}  newy={}',format(newx,newy))            
        newvector = (newx,newy)
        return newvector
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
        self.anim_delay = .25     

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
        self.anim_delay = .25

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




          

