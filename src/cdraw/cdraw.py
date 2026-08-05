import curses
from.curses import CursesElement, CPanel
from.config import Config

class CDraw(CursesElement):
    def __init__(self, config=False):
        self.config=config if config else Config()
        self.log=self.config.log
        self.config.color = True
        self.title = "Curses Draw DevTool"
        self.y = 1
        self.x = 0
        self.artifacts = []
        self.show_coordinates = 0
        self.show_artifacts = 1
        self.show_artifact_info = False
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
            elif key in [ord('i'),ord('I')]:
                self.show_artifact_info = False\
                     if self.show_artifact_info else True
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
        self.draw_artifact_info()
        self.draw_help()
        self.stdscr.refresh()

    def draw_header(self):
        self.stdscr.hline(1,0,curses.ACS_HLINE,self.w)
        title_start = (self.w-len(self.title))//2
        self.addcolorstr(self.TITLE_COLOR,0,title_start,self.title)
        self.addcolorstr(self.dim_white,0,self.w-10,  f"Y,X:{self.y},{self.x}")
        self.addcolorstr(self.dim_white,0,0,f"H,W:{self.h},{self.w}")

    def draw_footer(self):
        self.stdscr.hline(self.h-2,0,curses.ACS_HLINE,self.w)

    def artifactyx(self,a):
        if not a: return False
        elif a['style'] == 'frame': return a['start']
        elif a['style'] == 'anchor': return (a['y'],a['x'])
        return False
    @property
    def yx(self):
        return (self.y,self.x)

    def artifacts_selected(self):
        selected = []
        for a in self.artifacts:
            if self.artifactyx(a) == self.yx: selected.append(a)
        return selected

    def draw_artifact_info(self):
        if not self.show_artifact_info:# or not self.artifact_selected::
            return
        artifacts = self.artifacts_selected()
        y,x = 10,30
        height = 8
        width = 33
        info_panel = CPanel(self.stdscr,y,x,height,width)
        for a in artifacts:
            info_panel.add_panel_line([
                         [self.dim_white,2,'Id:'],
                         [self.white,6,a['id']],
                        ])
            info_panel.add_panel_line([
                         [self.dim_white,2,'Style:'],
                         [self.white,8,a['style']],
                        ])
            coordinates =[
                          [self.dim_white,2,'Coordinates:'],
                          [self.white,15,self.artifactyx(a)],
                         ]
            if a['style'] == 'frame':
                coordinates.append([self.white,23,f"{a['end']}"])
            info_panel.add_panel_line(coordinates)
            info_panel.add_panel_line()
        info_panel.draw_panel()

    def draw_creating_frame(self):
        if not self.creating_frame:
            return
        f = self.creating_frame
        color=self.green|curses.A_BOLD
        if self.x > f['start'][1] and \
           self.y > f['start'][0]:
            self.draw_frame(f['start'][0],f['start'][1],
                         self.y,self.x,color=color)
        elif self.y == f['start'][0] and self.x > f['start'][1]:
             self.draw_line(f['start'][0],f['start'][1],
                               self.x-f['start'][1],color,'h')
        elif self.x == f['start'][1] and self.y > f['start'][0]:
             self.draw_line(f['start'][0],f['start'][1],
                            self.y-f['start'][0],color,'v')


    def display_artifacts(self):
        if not self.show_artifacts or not self.artifacts:
            return
        on_artifact_origin = False
        for a in self.artifacts:
            if a['style'] =='frame':
                color = self.green|self.DIM
                if (self.y,self.x) == a['start']:
                    color=self.yellow
                    on_artifact_origin = True
                #if ((self.x in [a['start'][1],a['end'][1]]) and\
                #    (self.y >= a['start'][0] and self.y <= a['end'][0]))\
                #   or\
                #   ((self.y in [a['start'][0],a['end'][0]]) and\
                #    (self.x >= a['start'][1] and self.x <= a['end'][1])):
                #    color=self.yellow
                if a['end'][1] > a['start'][1] and a['end'][0] > a['start'][0]:
                    self.draw_frame(a['start'][0],a['start'][1],
                                    a['end'][0],a['end'][1],
                                    color=color)
                elif a['end'][0]==a['start'][0] and a['end'][1] > a['start'][1]:
                    #self.stdscr.hline(a['start'][0],a['start'][1],
                    #            curses.ACS_HLINE,a['end'][1]-a['start'][1])
                    self.draw_line(a['start'][0],a['start'][1],
                                  a['end'][1]-a['start'][1],
                                  color, 'h')
                elif a['end'][1]==a['start'][1] and a['end'][0] > a['start'][0]:
                    #self.stdscr.vline(a['start'][0],a['start'][1],
                    #               curses.ACS_VLINE,a['end'][0]-a['start'][0])
                    self.draw_line(a['start'][0],a['start'][1],
                                   a['end'][0]-a['start'][0],
                                   color,'v')
            if a['style'] == 'anchor':
                color = self.magenta
                if self.artifacts and (self.y,self.x) == (a['y'],a['x']):
                    color = self.yellow
                    on_artifact_origin = True
                self.addcolorstr(color,a['y'],a['x'],a['ch'])
        if not on_artifact_origin:
            self.draw_center_crosshair()

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
            _x = 0
            #if self.creating_frame:
            #    self.addcolorstr(self.cyan,y+2,x,f"{self.creating_frame}")

            if self.artifacts:
                for a in self.artifacts:
                    if a['style'] == 'frame':
                        s_cstr = f"{a['start']}"
                        s_cstr_len = len(s_cstr)
                        e_cstr = f"{a['end']}"
                        e_cstr_len = len(e_cstr)
                        if a['start'][1]+s_cstr_len < self.w-2:
                            _x = a['start'][1]+1
                        else:
                            _x = a['start'][1]-s_cstr_len-1
                        self.addcolorstr(self.cyan,a['start'][0],_x,s_cstr)
                        if a['end'][1]+e_cstr_len < self.w-2:
                            _x = a['end'][1]+1
                        else:
                            _x = a['end'][1]-e_cstr_len
                        self.addcolorstr(self.cyan,a['end'][0],_x,e_cstr)
                    #    if (self.y,self.x) == a['start']:
                    #        self.addcolorstr(self.green,y+2+idx,x,
                    #                f"Frame:{a['start']},{a['end']}")
                    #        idx += 1
                    if a['style'] == 'anchor':
                        cstr = f"({a['y']},{a['x']})"
                        cstr_len = len(cstr)
                        if a['x']+cstr_len < self.w-2:
                            _x = a['x']+1
                        else:
                            _x = a['x']-cstr_len-1
                        self.addcolorstr(self.cyan,a['y'],_x,cstr)

    def draw_help(self):
        if not self.show_help:
            return
        y,x = 10,10
        width = 43
        height= 8
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
        self.addcolorstr(self.CONTROL_COLOR,y+5,x+2,"I")
        self.addcolorstr(self.white,y+5,x+4,
                              "Show/Hide Info for Selected Artifacts")
        self.addcolorstr(self.CONTROL_COLOR,y+6,x+2,"X")
        self.addcolorstr(self.white,y+6,x+4,
                              "Delete All Artifacts")
        self.addcolorstr(self.CONTROL_COLOR,y+7,x+2,"Q")
        self.addcolorstr(self.white,y+7,x+4,
                              "Quit")

    def draw_crosshairs(self):
        _y = 1
        _x = 0
        while _y < self.h-1:
            if _y != self.y:
                if (_y,self.x) != (self.h-1,self.w-1):
                    if _y not in [self.h-2,0,1]:
                        self.addcolorstr(self.dim_white,_y,self.x,self.v_line)
                    elif _y == 1:
                        self.addcolorstr(self.dim_white,_y,self.x,
                                         self.end_top_line)
                    elif _y == self.h-2:
                        self.addcolorstr(self.dim_white,_y,self.x,
                                         self.end_bottom_line)
            _y += 1
        while _x < self.w:
            if _x != self.x:
                if (self.y,_x) != (self.h-1,self.w-1):
                    self.addcolorstr(self.dim_white,self.y,_x,self.h_line)
            _x += 1
        self.draw_center_crosshair()

    def draw_center_crosshair(self):
        color = self.magenta|self.BOLD
        if self.y == 1:
            self.addcolorstr(color,self.y,self.x,self.end_top_line)
        elif self.y == self.h-2:
            self.addcolorstr(color,self.y,self.x,self.end_bottom_line)
        elif self.x == 0:
            self.addcolorstr(color,self.y,self.x,self.end_left_line)
        elif self.x == self.w-1:
            self.addcolorstr(color,self.y,self.x,self.end_right_line)
        else:
            self.addcolorstr(color,self.y,self.x,self.intersect_line)

