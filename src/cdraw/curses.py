import curses
from .config import Config
from .options import Options,Option
import os
import sys

class CursesElement():

    def __getattr__(self, name):
        if name in self.COLORS:
            return self.COLORS[name]
        raise AttributeError(
             f"'{type(self).__name__}' object has no attribute '{name}'")

    @property
    def COLORS(self):
        if '_COLORS' not in self.__dict__:
            self._COLORS = {
                'BLACK' : curses.COLOR_BLACK,
                'WHITE' : curses.COLOR_WHITE,
                'CYAN' : curses.COLOR_CYAN,
                'GREEN' : curses.COLOR_GREEN,
                'MAGENTA' : curses.COLOR_MAGENTA,
                'YELLOW' : curses.COLOR_YELLOW,
                'RED' : curses.COLOR_RED,
                'BLUE' : curses.COLOR_BLUE,
                'DIM' : curses.A_DIM,
                'REV' : curses.A_REVERSE,
            }
        return self._COLORS

    @property
    def config(self):
        if '_config' not in self.__dict__:
            self._config = Config()
        return self._config
    @config.setter
    def config(self, cfg):
        if not isinstance(cfg, Config):
            raise TypeError(
               f"'{type(self).__name__}.config' must be an instance of Config")
        self._config = cfg

    @property
    def colors(self):
        if '_colors' not in self.__dict__:
            self._colors={
                'cyan'      : self.color_pair(2, self.CYAN, self.BLACK),
                'green'     : self.color_pair(3, self.GREEN, self.BLACK),
                'magenta'   : self.color_pair(4, self.MAGENTA, self.BLACK),
                'yellow'    : self.color_pair(5, self.YELLOW, self.BLACK),
                'red'       : self.color_pair(6, self.RED, self.BLACK),
                'blue'      : self.color_pair(7, self.BLUE, self.BLACK),
                'white'     : self.color_pair(8, self.WHITE, self.BLACK),
               }
        return self._colors

    @property
    def cyan(self):
        return self.colors['cyan']

    @property
    def green(self):
        return self.colors['green']

    @property
    def magenta(self):
        return self.colors['magenta']

    @property
    def yellow(self):
        return self.colors['yellow']

    @property
    def red(self):
        return self.colors['red']

    @property
    def blue(self):
        return self.colors['blue']

    @property
    def white(self):
        return self.colors['white']

    @property
    def dim_white(self):
        return self.colors['white']|self.DIM

    def color_pair(self, index, foreground, background):
        curses.init_pair(index,foreground,background)
        return curses.color_pair(index)

    @property
    def MENU_COLOR(self):
        return self.colors[self.config.menu_color]

    @property
    def TITLE_COLOR(self):
        return self.colors[self.config.title_color]

    @property
    def CONTROL_COLOR(self):
        return self.colors[self.config.control_color]

    @property
    def r_arrow(self):
        return "➤"

    @property
    def d_scroll_arrow(self):
        return "▼"

    @property
    def u_scroll_arrow(self):
        return "▲"

    @property
    def h(self):
        if '_h' not in self.__dict__:
            self.set_geometry()
        return self._h
    @h.setter
    def h(self, i):
        if not isinstance(i, int):
            raise TypeError(f"'{type(self).__name__}.h' must be of type 'int'>")
        self._h = i

    @property
    def w(self):
        if '_w' not in self.__dict__:
            self.set_geometry()
        return self._w
    @w.setter
    def w(self, i):
        if not isinstance(i, int):
            raise TypeError(f"'{type(self).__name__}.w' must be of type 'int'>")
        self._w = i

    @property
    def stdscr(self):
        if '_stdstr' not in self.__dict__:
            self._stdstr = False
        return self._stdscr
    @stdscr.setter
    def stdscr(self, s):
        self._stdscr = s

    def set_geometry(self):
        self._h, self._w = self.stdscr.getmaxyx()
        if self._h < 24 or self._w < 80: # allow for a screen status bar
                                         # on a 25H std window
            self._exit_screen_bad_size()

    def _exit_screen_bad_size(self):
        self.exit_curses(terminate=False)
        self.log.error("Terminal too small for curses display. "+\
                       "Either use -t/--text for textmode or resize "+\
                       "terminal to at least 80(w)x25(h). "+\
                       f"Current Size: {self.w}(w)x"+\
                       f"{self.h}(h)")
        sys.exit(1)


    def addcolorstr(self, color, *args, **kwargs):
        args = (args[0],args[1]," ") if args[2] is None else args
        new_args = []
        for idx,itm in enumerate(args):
            if idx == 2:
                itm = str(itm)
            new_args.append(itm)
        args = tuple(new_args)
        if self.config.color:
            self.stdscr.attron(color)
        self.stdscr.addstr(*args, **kwargs)
        if self.config.color:
            self.stdscr.attroff(color)

    def addcolorstrs(self, color, strs=[]):
        if self.config.color:
            self.stdscr.attron(color)
        for s in strs:
            self.stdscr.addstr(s[0], s[1], s[2])
        if self.config.color:
            self.stdscr.attroff(color)

    def draw_frame(self, uly=None, ulx=None,
                         lry=None, lrx=None,
                         color=None, fill=False):
        color = color if color else self.DIM
        uly = uly if uly else 1
        ulx = ulx if ulx else 0
        lry = lry if lry else self.h-2
        lrx = lrx if lrx else self.w-1
        i = uly+1
        if fill:
            filler = " "*((lrx-ulx)-1)
        while i < lry:
            self.addcolorstrs(color,[ [i,ulx,"│"],[i,lrx,"│"] ])
            if fill:
                self.addcolorstr(color,i,ulx+1,filler)
            i=i+1
        frame_width = lrx - ulx + 1
        self.addcolorstrs(color,[
             [uly,ulx,"┌"], [uly,lrx,"┐"], [lry,ulx, "└"], [lry,lrx, "┘"],
             [uly,ulx+1,"─"*(frame_width-2)], [lry,ulx+1,"─"*(frame_width-2)] ])

    def _draw_ruler(self, y=False):
        """ dev utility for measuring screen positions """
        y = y if y else self.h-2 # put in place of footer divider if not y
        sect=     "0123456789"
        sect_tens="         1"
        ruler = f'{sect}'*9 # bigger than 80 which is what i design for
        ruler_tens = list(f'{sect_tens}'*9)
        x = 0
        self.stdscr.addstr(y, 0, ruler[:self.w])
        for i,c in enumerate(ruler_tens):
            if c.isdigit():
                 tens = str(int(c)+x)
                 x = x + 1
                 if i < self.w-1:
                     self.addcolorstr(self.CONTROL_COLOR,
                                       y, i+1, f"{tens}")

    def highlight_selection(self, y, x, text,
                            style=False, sel=False, color=False):
        ''' Leave 2 charracters to left of x for arrow'''
        arrow = False
        style = style if style else self.config.select
        select = self.config.select
        if sel and not self.config.color:
            style = 'arrow'

        icolor = color if color else self.CONTROL_COLOR

        if style == "arrow":
            selected = True if style == select else False
            color = icolor|curses.A_BOLD
            arrow = True
        elif style == "highlight":
            selected = True if style == select else False
            color = icolor|self.REV
        elif style == "both":
            selected = True if style == select else False
            color = icolor|self.REV
            arrow = True
        if arrow:
            self.addcolorstr(icolor|curses.A_BOLD,
                             y, x-2,self.r_arrow)
        self.addcolorstr(color, y, x, text)
        if selected and not sel:
            self.addcolorstr(curses.A_BOLD, y, x+len(text)+1 ,"←")
            self.addcolorstr(curses.A_DIM, y, x+len(text)+3 ,"Selected")

    def exit_curses(self, terminate=True):
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()
        if terminate:
            sys.exit()


class Menu(CursesElement):
    def __init__(self, stdscr=None, config=None, select=False,
                 start_y=None, start_x=None, width=None, height=None,
                 scrollbar=True, scrollarrows=True):
        self.config = config if config else Config()
        self.log = self.config.log
        self._stdscr = stdscr
        self._current_row = 0
        self._start_row = 0
        self._selected_item = None
        self._menu_max_w = None
        self._menu_len = False
        self.active=True
        self._start_y = start_y
        self._start_x = start_x
        self._width = width
        self._height = height
        self._item_bold = False
        self._scrollbar = scrollbar
        self._scrollarrows = scrollarrows
        if select:
             self.select = select
        self._menu = {
                       'title':None,
                       'options':Options(),
                     }

    @property
    def stdscr(self):
        return self._stdscr
    @stdscr.setter
    def stdscr(self, s):
        self._stdscr = s

    @property
    def title(self):
        return self._menu['title']
    @title.setter
    def title(self,t):
        if isinstance(t, str):
            self._menu['title'] = t
            return
        raise TypeError("CursesDisplay title must be of type 'str'")

    @property
    def options(self):
        return self._menu['options']
    @options.setter
    def options(self,opts):
        self._menu['options']=Options(opts)

    @property
    def menu_max_w(self):
        if not self._menu_max_w or not self.menu_len:
            self._menu_max_w = max([len(i.text) for i in self.options])

        return min(self._menu_max_w, self.w-10)

    @property
    def menu_len(self):
        if not self._menu_len:
            self._menu_len = self.options.length
        return int(self._menu_len)

    @property
    def option(self):
        return Option

    @property
    def select(self):
        return self.config.select
    @select.setter
    def select(self, s):
        self.config.select = s

    def menu_input(self, key=None):
        #if not key:
        #    key = self.stdscr.getch()
        if key == ord('\n'):  # Enter key
            #self.stdscr.clear()
            return self.selected_item
        elif key == curses.KEY_UP and self.current_row > 0:
            self.current_row -= 1
        elif key == curses.KEY_DOWN and self.current_row < self.menu_len:
            self.current_row += 1
        elif key in [27,ord('q'),ord('Q'),ord('e'),ord('E')]:
            self.exit_curses()
        return key

    @property
    def item_bold(self):
        if not self._item_bold:
            def nobold(v,color):
                return color
            return nobold
        else:
            return self._item_bold
    @item_bold.setter
    def item_bold(self, f):
        self._item_bold = f

    @property
    def start_row(self):
        return self._start_row
    @start_row.setter
    def start_row(self,i):
        self._start_row = i
    @property
    def current_row(self):
        return self._current_row
    @current_row.setter
    def current_row(self, i):
        if i < 0:
            self._current_row = 0
        if i >= self.menu_len:
            self._current_row = self.menu_len-1
        else:
            self._current_row = i
        if self._current_row < self.start_row:
            self.start_row = self._current_row
        elif self._current_row >= self.start_row + self.height:
            self.start_row = self.current_row  - self.height + 1

    @property
    def height(self):
        if not self._height:
            return False
        return self._height
    @height.setter
    def height(self, h):
        if isinstance(h, int) and h >= 0:
            self._height = h
        else:
            raise TypeError("Height must be of type 'int'")

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, h):
        if isinstance(h, int) and h >= 0:
            self._width = h
        else:
            raise TypeError("Width must be of type 'int'")

    @property
    def start_y(self):
        return self._start_y
    @start_y.setter
    def start_y(self, i):
        if isinstance(i, int) and i >= 0:
            self._start_y = i
        else:
            raise TypeError("Start_y must be of type 'int'")

    @property
    def start_x(self):
        return self._start_x
    @start_x.setter
    def start_x(self, i):
        if isinstance(i, int) and i >= 0:
            self._start_x = i
        else:
            raise TypeError("Start_x must be of type 'int'")

    @property
    def scrollbar(self) -> bool:
        return self._scrollbar
    @scrollbar.setter
    def scrollbar(self, b: bool):
        if not isinstance(b, bool):
            raise TypeError(f"scrollbar must be boolean not {type(b).__name__}")
        self._scrollbar = b

    @property
    def scrollarrows(self) -> bool:
        return self._scrollarrows
    @scrollarrows.setter
    def scrollarrows(self, b: bool):
        if not isinstance(b, bool):
            raise TypeError(
                     f"scrollarrows must be boolean not {type(b).__name__}")
        self._scrollarrows = b

    @property
    def selected_item(self):
        return self._selected_item
    @selected_item.setter
    def selected_item(self, i):
        self._selected_item = i

    @property
    def s_item(self):
        return list(self.options)[self.current_row]

    def set_current_row(self,text):
        for idx, item in enumerate(self.options):
            if text == item.text:
                self.start_row = 0 # forces a recalc correctly in setter
                self.current_row = idx
                self.selected_item = item
                return

    def draw_menu(self):
        """
          Draw the menu with the current selection highlighted
        """

        if not self.height:
            self.height = min([self.h-7,self.menu_len])
        if not self.width:
            self.width = min([self.menu_max_w,self.w-6])
        if not self.start_y:
            self.start_y = (self.h - self.height)//2
        if not self.start_x:
            self.start_x = (self.w - self.menu_max_w)//2 - 3

        y, x  = self.start_y, self.start_x+3
        if self.title:
            self.addcolorstr(self.TITLE_COLOR,y-1,x-3,self.title)
        opts = [i for i in self.options]
        selected_item=None
        for i in range(self.height):
            idx = self.start_row + i
            if idx >= self.menu_len:
                break
            _y = y + i
            item = opts[idx]
            item_text = f"{item.text: <{self.width}}"
            item_text = item_text[:self.width]
            if not self.config.color:
                select = 'arrow'
            else:
                select = self.select
            if idx == self.current_row and self.active:
                self.selected_item = item
                # Highlight selected item
                if select == "arrow":
                    color = self.CONTROL_COLOR|curses.A_BOLD
                    arrow = f"{self.r_arrow}"
                    text = f"{item_text}"
                    _x = x-2
                elif select == "highlight":
                    color = self.CONTROL_COLOR|self.REV
                    arrow = ""
                    text = f"{item_text}"
                    _x = x
                else:
                    color = self.CONTROL_COLOR|self.REV
                    arrow = f"{self.r_arrow}"
                    text = f"{item_text}"
                    _x = x-2
                self.addcolorstr(self.CONTROL_COLOR|curses.A_BOLD,
                                 _y, _x, arrow)
                self.addcolorstr(color, _y, x,text)
                if self.scrollbar:
                    if self.start_row > 0 or (self.start_row+self.height)\
                                         < self.menu_len:
                        self.addcolorstr(self.CONTROL_COLOR, _y, x-3, "│")
                        if _y - self.start_y == 0:
                            self.addcolorstr(self.CONTROL_COLOR, _y, x-3, "┯")
                        elif _y - self.start_y == self.height-1:
                            self.addcolorstr(self.CONTROL_COLOR, _y, x-3, "┷")
                        else:
                            self.addcolorstr(self.CONTROL_COLOR, _y, x-3, "│")

            else:
                color = self.colors[item.color]\
                          if item.color else self.MENU_COLOR
                color = self.item_bold(item, color)
                self.addcolorstr(color, _y, x, item_text)
                if self.scrollbar:
                    if self.start_row > 0 or (self.start_row+self.height)\
                                         < self.menu_len:
                        if _y - self.start_y == 0:
                            self.addcolorstr(self.DIM, _y, x-3, "┯")
                        elif _y - self.start_y == self.height-1:
                            self.addcolorstr(self.DIM, _y, x-3, "┷")
                        else:
                            self.addcolorstr(self.DIM, _y, x-3, "│")

        if self.scrollarrows:
            if self.start_row > 0:
                self.addcolorstr(self.DIM, y, x-3, self.u_scroll_arrow)
            if self.start_row+self.height < self.menu_len:
                self.addcolorstr(self.DIM,
                                 y+(self.height-1),x-3,self.d_scroll_arrow)


class SettingsDisplay(CursesElement):
    def __init__(self, config=None, stdscr=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self.stdscr = stdscr
        self.current_row = 1
        self.settings_color = False
        self.settings_show_picker = False
        self.disp_saved = False
        self._color_menu = False
        self.config_colors = {
                               'title_color': self.config.title_color,
                               'menu_color': self.config.menu_color,
                               'control_color': self.config.control_color,
                             }
    @property
    def color_menu(self):
        if not self._color_menu:
            colors = self.colors
            self._color_menu = Menu(config=self.config, stdscr=self.stdscr,
                                    width=15, height=5)
            self._color_menu.options = [Option(c,c,color=c) for c in colors]
        return self._color_menu

    def draw_settings_footer(self):
        if not self.settings_color:
            self.addcolorstrs(self.DIM,[
                    [self.h-1,14,'BACK:'],
                    [self.h-1,36,'SAVE:'],
                    [self.h-1,55,'QUIT:'],
                    [self.h-1,61,'|']])

            self.addcolorstrs(self.CONTROL_COLOR,[
                    [self.h-1, 19, "<ESC>"],
                    [self.h-1, 41, "S"],
                    [self.h-1, 60, "Q"],
                    [self.h-1, 62, "E"]])
        else:
            self.addcolorstrs(self.DIM,[
                    [self.h-1,4,'BACK:'],
                    [self.h-1,16,'NAVIGATE COLOR:'],
                    [self.h-1,36,'SELECT COLOR:'],
                    [self.h-1,58,'SAVE:'],
                    [self.h-1,66,'QUIT:'],
                    [self.h-1,72,'|']])

            self.addcolorstrs(self.CONTROL_COLOR,[
                    [self.h-1, 9, "<ESC>"],
                    [self.h-1, 31, "↑/↓"],
                    [self.h-1, 49, "<ENTER>"],
                    [self.h-1, 63, "S"],
                    [self.h-1, 71, "Q"],
                    [self.h-1, 73, "E"]])


    def draw_settings(self):
        uly, ulx = 5, 15
        self.draw_frame(uly,ulx,uly+15,ulx+50,self.DIM, fill=True)

        # title
        y, x = uly, ulx+22
        title="Settings"
        self.addcolorstr(self.TITLE_COLOR, y, x, title)
        cf = f"CfgFile: {self.config.configfile}"
        self.addcolorstr(self.dim_white, y+1, ulx+(25)-(len(cf)//2), cf)

        # Color on/off
        y, x = uly+2, ulx+2
        c = "On" if self.config.color else "Off"
        self.draw_control(y,x,'O'," ", color=self.config.control_color)
        self.addcolorstr(self.colors['white'], y, x+2, "Color")
        self.addcolorstr(curses.A_BOLD, y, x+12, c)

        # Color selections
        y,x = uly+4, ulx+2
        self.draw_color_setting(y, x, 'T', 'title', 'Title',
                                self.TITLE_COLOR, self.config.title_color)
        self.draw_color_setting(y+1, x, 'M', 'menu', 'Menu',
                                self.MENU_COLOR, self.config.menu_color)
        self.draw_color_setting(y+2, x, 'C', 'control', 'Control',
                                self.CONTROL_COLOR, self.config.control_color)

        # toggle select indicator
        y, x = uly+8, ulx+2
        self.draw_control(y,x,'Z'," ",color=self.config.control_color)
        self.addcolorstr(self.colors['white'],y,x+2,'Select Style')
        self.highlight_selection(y,x+18,"Arrow and Reverse", 'both')
        self.highlight_selection(y+1,x+18,"Arrow", 'arrow')
        self.highlight_selection(y+2,x+18,"Reverse", 'highlight')

        # save confirmed message
        y, x = uly+15, ulx+18
        if self.disp_saved:
            self.addcolorstr(self.DIM, y, x, "< Config Saved >")
            self.disp_saved = False

        # color options display
        y, x = uly+2, ulx+24
        if self.settings_color:
            self.addcolorstr(self.colors['white'],y,x-1,"Select Color")
            self.color_menu.start_y = y+1
            self.color_menu.start_x = x
            self.color_menu.width = 15
            self.color_menu.height = 5
            self.color_menu.draw_menu()

    def draw_color_setting(self, y, x, key, setting, label, color, cname):
        if self.settings_color == setting:
            self.highlight_selection(y,x+2,label,sel=True)
        else:
            self.addcolorstr(self.colors['white'],y,x+2,label)
            self.draw_control(y,x,key, color=self.config.control_color)
            self.addcolorstr(self.DIM, y, x+1,":")
        self.addcolorstr(color, y, x+12, cname)



    def draw_control(self, y, x, control, label=False, color=False,
                                sep=':', rev=False):
            col = self.colors[color] if color else self.DIM
            if rev:
                if label:
                    self.addcolorstr(self.DIM, y, x, f"{label}{sep}")
                    self.addcolorstr(col,y,x,label)
                    self.addcolorstr(self.CONTROL_COLOR,
                                     y, (x+len(label)+len(sep)), control)
                else:
                    self.addcolorstr(col,y,x,control)

            else:
                if label:
                    self.addcolorstr(self.DIM, y, x, f"{control}{sep}")
                    self.addcolorstr(self.CONTROL_COLOR, y, x, control)
                    self.addcolorstr(col,
                                     y, (x+len(control)+len(sep)), label)
                else:
                    self.addcolorstr(col,y,x,control)


    def set_setting_color(self, setting, color, soft=False):
        if setting == 'title':
            if color == "RESET":
                self.config.title_color = self.config_colors['title_color']
                return
            if not soft:
                self.config_colors['title_color'] = color
            else:
                self.config.title_color = color
        if setting == 'menu':
            if color == "RESET":
                self.config.menu_color = self.config_colors['menu_color']
                return
            if not soft:
                self.config_colors['menu_color'] = color
            else:
                self.config.menu_color = color
        if setting == 'control':
            if color == "RESET":
                self.config.control_color = self.config_colors['control_color']
                return
            if not soft:
                self.config_colors['control_color'] = color
            else:
                self.config.control_color = color

    def settings_input(self, key):
        if self.settings_color:
            if key == 27: # escape
                self.set_setting_color(
                       self.settings_color,
                       "RESET")
                self.color_menu.current_row = 0
                self.settings_color = False
                return
            elif key == ord('\n'):  # Enter key
                self.set_setting_color(
                       self.settings_color,
                       self.color_menu.s_item.color)
                self.color_menu.current_row = 0
                self.settings_color = False
                return
            elif key == curses.KEY_UP and self.color_menu.current_row > 0:
                self.color_menu.current_row -= 1
                self.set_setting_color(
                       self.settings_color,
                       self.color_menu.s_item.color, soft=True)
            elif key == curses.KEY_DOWN and\
                 self.color_menu.current_row < self.color_menu.menu_len-1:
                self.color_menu.current_row += 1
                self.set_setting_color(
                       self.settings_color,
                       self.color_menu.s_item.color, soft=True)

        if key in [ord('q'),ord('Q'),ord('e'),ord('E')]:
            self.exit_curses()
        elif key in [ord('o'), ord('O')]:
            if self.config.color:
                self.config.color=False
            else:
                self.config.color=True
        elif key in [ord('t'), ord('T')]:
            self.settings_color = 'title'
            self.color_menu.set_current_row(self.config.title_color)
        elif key in [ord('m'), ord('M')]:
            self.settings_color = 'menu'
            self.color_menu.set_current_row(self.config.menu_color)
        elif key in [ord('c'), ord('C')]:
            self.settings_color = 'control'
            self.color_menu.set_current_row(self.config.control_color)
        elif key in [ord('z'), ord('Z')]:
            self.settings_toggle_select()
        elif key in [ord('s'), ord('S')]:
            self.config.save()
            self.disp_saved = True
        elif key == 27: # escape==27
            return 'main_menu'

    def settings_toggle_select(self):
        if self.config.select == 'both':
            self.config.select = 'arrow'
        elif self.config.select == 'highlight':
            self.config.select = 'both'
        elif self.config.select == 'arrow':
            self.config.select = 'highlight'
        return

class CPanel(CursesElement):
    def __init__(self, stdscr, y, x, height, width,
                       config=False, frame=True,
                       Title=False):
        self.config = config if config else Config()
        self.stdscr = stdscr
        self.frame = frame
        self._y = y
        self._x = x
        self._width = width
        self._height = height
        self.frame = frame
        self.title = False
        self.start = 0
        self._lines = []
        self.controls = []


    @property
    def lines(self):
        return self._lines
    @lines.setter
    def lines(self,l):
        self._lines = l

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, x):
        if isinstance(x,int) and x < self.w-1:
            self._x = x
        else:
            raise ValueError(
                   f"'x' must be of type 'int' and < screen width -1")

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,y):
        if isinstance(y,int) and y < self.h-1:
            self._y = y
        else:
            raise ValueError(
                   f"'y' must be of type 'int' and < screen height -1")

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, i):
        if isinstance(i,int) and i < self.w-1-self.x:
            self._width = i
        else:
            raise ValueError(
                   f"'width' must be of type 'int' and "+\
                   f"< screen {self.w-1-self.x}")

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, i):
        if isinstance(i,int) and i < self.h-1-self.y:
            self._height = i
        else:
            raise ValueError(
                   f"'height' must be of type 'int' and "+\
                   f"< screen {self.h-2-self.x}")


    def handle_panel_input(self, key):
        for i in self.controls:
            if key in i['controls']:
                kwargs = i['kwargs']
                if kwargs:
                    i['action'](**kwargs)
                else:
                    i['action']
                return key
        return key

    def add_control_key(self, keys, action, kwargs=None):
        if not isinstance(keys,list)\
           or not all(type(item) is int for item in keys):
            raise ValueError("'keys' must be a list of integers.")
        if kwargs and not isinstance(kwargs, dict):
            raise ValueError("'kwargs' must be wither None or `dict`")
        self.controls.append({'controls':keys,
                              'action':action,
                              'kwargs':kwargs,
                             })

    def add_panel_line(self, line=None):
        if line == None:
            self._lines.append(line)
            return
        elif isinstance(line, list):
            self._lines.append(line)
            return
        raise ValueError("'line' must be a 'list' of 'list's or None.")

    def draw_panel(self):
        if self.frame:
            self.draw_frame(self.y,self.x,
                            self.y+self.height,
                            self.x+self.width)
        i = 1
        for idx,line in enumerate(self.lines):
            if idx < self.start:
                next
            if line != None:
                for item in line:
                    self.addcolorstr(item[0],self.y+i,self.x+item[1],
                                     item[2])
            i += 1

