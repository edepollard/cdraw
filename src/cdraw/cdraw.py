import curses
from.curses import CursesElement, CPanel
from.config import Config

class HotKeys:
    def __init__(self):
        self.hot_key_map = {}

    def key_func(self, key):
        if self.has_key(key):
           return self.hot_key_map[key]

    def has_key(self, key):
        return True if key in self.hot_key_map else False

    def add_keys_list(self, key_list):
        for keys in key_list:
            self.add_keys(keys[0],keys[1])

    def add_keys(self,keys,func):
        self.keys = keys
        self.func = func
        if not isinstance(keys, list): self.bad_keys()
        if not callable(func): self.bad_func()
        for key in keys:
            self.add(key, func)

    def add(self,key,func):
            if isinstance(key,int):
                self.hot_key_map[key] = func
            elif isinstance(key, str) and len(key) == 1:
                self.hot_key_map[ord(key)] = func
            elif isinstance(key, str) and len(key) > 1:
                if key == 'up': 
                    self.hot_key_map[curses.KEY_UP] = func
                elif key == 'down': 
                    self.hot_key_map[curses.KEY_DOWN] = func
                elif key == 'left': 
                    self.hot_key_map[curses.KEY_LEFT] = func
                elif key == 'right': 
                    self.hot_key_map[curses.KEY_RIGHT] = func
                elif key == 'del': 
                    self.hot_key_map[127] = func
                    self.hot_key_map[curses.KEY_BACKSPACE] = func
                    self.hot_key_map[curses.KEY_DC] = func
            else:
                raise Exception(f"Unrecognized key or alias: {k}")
        

    def bad_keys(self):
        raise TypeError("HotKey.keys must be of type 'list'")
        exit(1)

    def bad_func(self):
        raise TypeError("HotKey.func must be callable")


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
        self.action_map = {}
        self._hot_keys = HotKeys() 
        self.hot_keys.add_keys_list([
              [['a', 'A'], self.add_anchor],
              [['c', 'C'], self.toggle_show_coordinates],
              [['d', 'D'], self.toggle_show_artifacts],
              [['f', 'F'], self.frame],
              [['h', 'H'], self.toggle_show_help],
              [['i', 'I'], self.toggle_show_artifact_info],
              [['n', 'N'], self.info_panel_scroll_down],
              [['p', 'P'], self.info_panel_scroll_up],
              [['x', 'X'], self.clear_artifacts],
              [['q', 'Q'], self.exit_curses],
              [['del'],    self.remove_selected],
              [['up'],     self.key_up],
              [['down'],   self.key_down],
              [['left'],   self.key_left],
              [['right'],  self.key_right],
             ])


    @property
    def hot_keys(self):
        return self._hot_keys

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
        stdscr.keypad(True)
        curses.curs_set(0)
        if not curses.has_colors():
            self.config.color=False
        self.stdscr.clear()
        self.draw_screen()
        self.get_input()

    def get_input(self):
        while True:
            key = self.stdscr.getch()
            if self.hot_keys.has_key(key):
                self.hot_keys.key_func(key)()
            self.draw_screen()

    # Input Functions
    def clear_artifacts(self):
        self.artifacts = []
    def key_up(self):
        self.y = self.y-1 if self.y > 1 else self.y
    def key_down(self):
        self.y = self.y+1 if self.y < self.h-2 else self.y
    def key_left(self):
        self.x = self.x-1 if self.x > 0 else self.x
    def key_right(self):
        self.x = self.x+1 if self.x < self.w-1 else self.x
    def toggle_show_coordinates(self):
        self.show_coordinates = self.toggle(self.show_coordinates)
    def toggle_show_artifacts(self):
        self.show_artifacts = self.toggle(self.show_artifacts)
    def toggle_show_help(self):
        self.show_help = self.toggle(self.show_help)
    def toggle_show_artifact_info(self):
        self.show_artifact_info = self.toggle(self.show_artifact_info)
        self.info_panel_start = 0
    def info_panel_scroll_down(self):
        self.info_panel.scroll_down()
        self.info_panel_start = self.info_panel.start
    def info_panel_scroll_up(self):
        self.info_panel.scroll_up()
        self.info_panel_start = self.info_panel.start
    def toggle(self, item):
        return True if not item else False


    def frame(self):
        if not self.creating_frame:
            nf = self.empty_frame.copy()
            nf['id'] = self.new_id
            nf['start'] = (self.y,self.x)
            self.creating_frame = nf.copy()
            return
        elif self.creating_frame:
            sy = self.creating_frame['start'][0]
            sx = self.creating_frame['start'][1]
            if self.y > sy and self.x > sx:
                sy = sy
                sx = sx
                ey = self.y 
                ex = self.x
            elif self.y > sy and self.x == sx:
                sy = sy 
                sx = sx
                ey = self.y
                ex = self.x
            if self.y == sy and self.x > sx:
                sy = sy
                sx = sx
                ey = self.y 
                ex = self.x
            elif self.y < sy and self.x < sx:
                ey = sy
                ex = sx
                sy = self.y 
                sx = self.x
            elif self.y > sy and self.x < sx:
                sy = sy
                ey = self.y 
                ex = sx
                sx = self.x
            elif self.y < sy and self.x > sx:
                sx = sx
                ey = sy
                ex = self.x
                sy = self.y
            elif self.y == sy and self.x < sx:
                sy = sy
                ex = sx
                sx = self.x
                ey = sy
            elif self.y < sy and self.x == sx:
                ey = sy
                ex = sx
                sy = self.y
                sx = self.x
            elif (self.y,self.x) == (sy,sx):
                self.creating_frame = None
                return
            self.creating_frame['start']=(sy,sx)
            self.creating_frame['end']=(ey,ex)
            self.artifacts.append(self.creating_frame.copy())
            self.creating_frame = None
            return

    def draw_screen(self):
        self.set_geometry()
        self.stdscr.clear()
        self.build_info_panel()
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
        self.draw_line(1,0,self.w,self.dim_white,'h')
        title_start = (self.w-len(self.title))//2
        self.addcolorstr(self.TITLE_COLOR,0,title_start,self.title)
        self.addcolorstr(self.dim_white,0,self.w-10,  f"Y,X:{self.y},{self.x}")
        self.addcolorstr(self.dim_white,0,0,f"H,W:{self.h},{self.w}")

    def draw_footer(self):
        self.draw_line(self.h-2,0,self.w,self.dim_white,'h')
        self.addcolorstr(self.white,self.h-1,5,"Help")
        self.addcolorstr(self.CONTROL_COLOR,self.h-1,5,"H")

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
        self.info_panel.draw_panel(color=self.dim_white)

    def build_info_panel(self):
        artifacts = self.artifacts_selected()
        if len(artifacts) == 0:
            self.show_artifact_info = 0
            self.info_panel_start = 0
            return
        y,x = 10,30
        height = min([10, len(artifacts)+1])
        width = 28
        self.info_panel = CPanel(self.stdscr,y,x,height,width,
                                 config=self.config)
        self.info_panel.start = self.info_panel_start
        for a in artifacts:
            end = "" if a['style'] != 'frame' else f" {a['end']}"
            coordinates = f"{self.artifactyx(a)} {end}"
            self.info_panel.add_panel_line([
               [self.white,3,f"{a['id']}:{a['style']}:{coordinates}"]])

    def draw_creating_frame(self):
        if not self.creating_frame:
            return
        f = self.creating_frame
        sy = f['start'][0]
        sx = f['start'][1]
        color=self.green|curses.A_BOLD
        if self.y > sy and self.x > sx:
            self.draw_frame(sy,sx,self.y,self.x,color=color)
        elif self.y < sy and self.x < sx:
            self.draw_frame(self.y,self.x,sy,sx,color=color)
        elif self.y < sy and self.x > sx:
            self.draw_frame(self.y,sx,sy,self.x,color=color)
        elif self.y > sy and self.x < sx:
            self.draw_frame(sy,self.x,self.y,sx,color=color)
        elif self.y == sy and self.x < sx:
            self.draw_line(self.y,self.x,sx-self.x,color,'h')
        elif self.y < sy and self.x == sx:
            self.draw_line(self.y,self.x,sy-self.y,color,'v')
        elif self.y == sy and self.x > sx:
            self.draw_line(sy,sx,self.x-sx,color,'h')
        elif self.y > sy and self.x == sx:
            self.draw_line(sy,sx,self.y-sy,color,'v')
        self.draw_center_crosshair()


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
                if a['end'][1] > a['start'][1] and a['end'][0] > a['start'][0]:
                    self.draw_frame(a['start'][0],a['start'][1],
                                    a['end'][0],a['end'][1],
                                    color=color)
                elif a['end'][0]==a['start'][0] and a['end'][1] > a['start'][1]:
                    self.draw_line(a['start'][0],a['start'][1],
                                  a['end'][1]-a['start'][1],
                                  color, 'h')
                elif a['end'][1]==a['start'][1] and a['end'][0] > a['start'][0]:
                    self.draw_line(a['start'][0],a['start'][1],
                                   a['end'][0]-a['start'][0],
                                   color,'v')
                if color == self.green|self.DIM:
                    color = self.green
                    hchar = self.ul_corner
                    if a['start'][0] == a['end'][0]:
                        hchar = self.h_line
                    elif a['start'][1] == a['end'][1]:
                        hchar = self.v_line
                    self.addcolorstr(color,
                                     a['start'][0],a['start'][1],hchar)
                   
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
        self.artifacts.append({
                 'id':self.new_id,
                 'style':'anchor',
                 'y':self.y,
                 'x':self.x,
                 'ch':'A',
                  })

    def remove_selected(self):
        for a in self.artifacts:
            if a['style'] == 'anchor': y,x = a['y'],a['x']
            if a['style'] == 'frame': y,x = a['start']
            if (self.y,self.x) == (y,x):
                self.remove_artifact(a['id'])
                return

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
        width = 43
        height= 9
        y,x = (self.h-2)-height,2
        self.draw_frame(y,x,y+height,x+width,fill=True)
        self.addcolorstr(self.CONTROL_COLOR,y+1,x+2,"A")
        self.addcolorstr(self.white,y+1,x+4,
                              "Add an Anchor")
        self.addcolorstr(self.CONTROL_COLOR,y+2,x+2,"F")
        self.addcolorstr(self.white,y+2,x+4,
                              "Start or End a Frame")
        self.addcolorstr(self.CONTROL_COLOR,y+3,x+2,"D")
        self.addcolorstr(self.white,y+3,x+4,
                              "Display Artifacts Toggle")
        self.addcolorstr(self.CONTROL_COLOR,y+4,x+2,"C")
        self.addcolorstr(self.white,y+4,x+4,
                              "Show/Hide Coordinate Data")
        self.addcolorstr(self.CONTROL_COLOR,y+5,x+2,"I")
        self.addcolorstr(self.white,y+5,x+4,
                              "Show/Hide Info for Selected Artifacts")
        self.addcolorstr(self.CONTROL_COLOR,y+6,x+2,"<DEL>")
        self.addcolorstr(self.white,y+6,x+8,
                              "Delete a Selected Artifact")
        self.addcolorstr(self.CONTROL_COLOR,y+7,x+2,"X")
        self.addcolorstr(self.white,y+7,x+4,
                              "Delete All Artifacts")
        self.addcolorstr(self.CONTROL_COLOR,y+8,x+2,"Q")
        self.addcolorstr(self.white,y+8,x+4, "Quit")
        # help 
        self.addcolorstr(self.white,self.h-1,5,"Help")
        self.addcolorstr(self.CONTROL_COLOR,self.h-1,5,"H")

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

