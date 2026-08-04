import curses
from.curses import CursesElement
from.config import Config

class CDraw(CursesElement):
    def __init__(self, config=False):
        self.config=config if config else Config()
        self.log=self.config.log
        self.config.color = True
        self.y = 1
        self.x = 0
        self.artifacts = []
        self.show_coordinates = 0
        self.show_artifacts = 1
        self.show_help = 0
        self.art_id = 0
        self.creating_frame = None


    @property
    def empty_frame(self):
        return {
                'id':None,
                'style':'frame',
                'start':None,
                'end':None,
               }

    @property
    def new_id(self):
        i = self.art_id
        self.art_id += 1
        return i

    def __call__(self):
        self.start_curses()

    def start_curses(self):
        curses.wrapper(self.__run)

    def __run(self,stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        if not curses.has_colors():
            self.config.color=False
        self.stdscr.clear()
        self.draw_screen()
        self.get_input()

    def get_input(self):
        while True:
            key = self.stdscr.getch()
            if key in [ord('q'),ord('Q')]:
                self.exit_curses()
            elif key in [ord('f'),ord('F')]:
                self.frame()
            elif key == curses.KEY_DOWN:
                self.y = self.y+1 if self.y < self.h-2 else self.y
            elif key == curses.KEY_UP:
                if self.creating_frame and\
                      self.y == self.creating_frame['start'][0]:
                    pass
                else:
                    self.y = self.y-1 if self.y > 1 else self.y
            elif key == curses.KEY_RIGHT:
                self.x = self.x+1 if self.x < self.w-1 else self.x
            elif key == curses.KEY_LEFT:
                if self.creating_frame and\
                      self.x == self.creating_frame['start'][1]:
                    pass
                else:
                    self.x = self.x-1 if self.x > 0 else self.x
            elif key in [ord('c'),ord('C')]:
                self.show_coordinates = False\
                     if self.show_coordinates else True
            elif key in [ord('d'),ord('D')]:
                self.show_artifacts = False\
                     if self.show_artifacts else True
            elif key in [ord('h'),ord('H')]:
                self.show_help = False\
                     if self.show_help else True
            elif key in [ord('a'),ord('A')]:
                self.add_anchor()
            elif key in [ord('x'),ord('X')]:
                self.artifacts = []
            self.draw_screen()

    def frame(self):
        if not self.creating_frame:
            for a in self.artifacts:
                if a['style'] == 'frame' and (self.y,self.x) == a['start']:
                    self.remove_artifact(a['id'])
                    return
            nf = self.empty_frame.copy()
            nf['id'] = self.new_id
            nf['start'] = (self.y,self.x)
            self.creating_frame = nf.copy()
            return
        elif self.creating_frame:
            if (self.y,self.x) != self.creating_frame['start']:
                self.creating_frame['end'] = (self.y,self.x)
                self.artifacts.append(self.creating_frame.copy())
            self.creating_frame = None
            return

    def draw_screen(self):
        self.set_geometry()
        self.stdscr.clear()
        self.draw_header()
        self.draw_footer()
        self.draw_crosshairs()
        self.display_artifacts()
        self.display_coordinates()
        self.draw_creating_frame()
        self.draw_help()
        self.stdscr.refresh()

    def draw_header(self):
        self.stdscr.hline(1,0,curses.ACS_HLINE,self.w)

    def draw_footer(self):
        self.stdscr.hline(self.h-2,0,curses.ACS_HLINE,self.w)

    def draw_creating_frame(self):
        if not self.creating_frame:
            return
        f = self.creating_frame
        if self.x > f['start'][1] and \
           self.y > f['start'][0]:
            self.draw_frame(f['start'][0],f['start'][1],
                         self.y,self.x,color=self.yellow)
        elif self.y == f['start'][0] and self.x > f['start'][1]:
             self.stdscr.hline(f['start'][0],f['start'][1],
                               curses.ACS_HLINE,self.x-f['start'][1])
        elif self.x == f['start'][1] and self.y > f['start'][0]:
             self.stdscr.vline(f['start'][0],f['start'][1],
                               curses.ACS_VLINE,self.y-f['start'][0])


    def display_artifacts(self):
        if not self.show_artifacts:
            return
        for a in self.artifacts:
            if a['style'] =='frame':
                color = self.green|self.DIM
                if self.artifacts and (self.y,self.x) == a['start']:
                    color=self.yellow
                self.draw_frame(a['start'][0],a['start'][1],
                                a['end'][0],a['end'][1],
                                color=color)
            if a['style'] == 'anchor':
                color = self.magenta    
                if self.artifacts and (self.y,self.x) == (a['y'],a['x']):
                    color = self.yellow
                self.addcolorstr(color,a['y'],a['x'],a['ch'])

    def add_anchor(self):
        if (self.y,self.x) == (self.h-1,self.w-1):
            return
        for a in self.artifacts:
            if a['style'] == 'anchor' and (self.y,self.x) == (a['y'],a['x']):
                self.remove_artifact(a['id'])
                return
        self.artifacts.append({
                 'id':self.new_id,
                 'style':'anchor',
                 'y':self.y,
                 'x':self.x,
                 'ch':'A',
                  })

    def remove_artifact(self, aid):
        for idx,a in enumerate(self.artifacts):
            if a['id'] == aid: del self.artifacts[idx] 

    def display_coordinates(self):
        if self.show_coordinates:
            y,x = 5,5
            self.addcolorstr(self.cyan,y,x,  f"Y,X:{self.y},{self.x}")
            self.addcolorstr(self.cyan,y+1,x,f"H,W:{self.h},{self.w}")
            if self.creating_frame:
                self.addcolorstr(self.cyan,y+2,x,f"{self.creating_frame}")
            idx = 1
            if self.artifacts:
                for a in self.artifacts:
                    if a['style'] == 'frame':
                        if (self.y,self.x) == a['start']:
                            self.addcolorstr(self.green,y+2+idx,x,
                                    f"Frame:{a['start']},{a['end']}")
                            idx += 1
                    if a['style'] == 'anchor':
                        if (self.y,self.x) == (a['y'],a['x']):
                            self.addcolorstr(self.green,y+2+idx,x,
                                    f"Anchor:({a['y']},{a['x']})")
                            idx += 1

    def draw_help(self):
        if not self.show_help:
            return
        y,x = 10,10
        width = 33
        height= 7
        self.draw_frame(y,x,y+height,x+width,fill=True)
        self.addcolorstr(self.white,y,x+5,"Help")
        self.addcolorstr(self.CONTROL_COLOR,y,x+5,"H")
        self.addcolorstr(self.CONTROL_COLOR,y+1,x+2,"A")
        self.addcolorstr(self.white,y+1,x+4,
                              "Add or Remove an Anchor")
        self.addcolorstr(self.CONTROL_COLOR,y+2,x+2,"F")
        self.addcolorstr(self.white,y+2,x+4,
                              "Start, End or Remove a Frame")
        self.addcolorstr(self.CONTROL_COLOR,y+3,x+2,"D")
        self.addcolorstr(self.white,y+3,x+4,
                              "Display Artifacts Toggle")
        self.addcolorstr(self.CONTROL_COLOR,y+4,x+2,"C")
        self.addcolorstr(self.white,y+4,x+4,
                              "Show/Hide Coordinate Data")
        self.addcolorstr(self.CONTROL_COLOR,y+5,x+2,"X")
        self.addcolorstr(self.white,y+5,x+4,
                              "Delete All Artifacts")
        self.addcolorstr(self.CONTROL_COLOR,y+6,x+2,"Q")
        self.addcolorstr(self.white,y+6,x+4,
                              "Quit")

    def draw_crosshairs(self):
        _y = 1
        _x = 0
        while _y < self.h-1:
            if _y != self.y:
                if (_y,self.x) != (self.h-1,self.w-1)\
                   and _y not in [self.h-2,0,1]:
                    self.addcolorstr(self.dim_white,_y,self.x,"│")
            _y += 1
        while _x < self.w:
            if _x != self.x:
                if (self.y,_x) != (self.h-1,self.w-1):
                    self.addcolorstr(self.dim_white,self.y,_x,"─")
            _x += 1
        self.addcolorstr(self.white,self.y,self.x,"+")




        
