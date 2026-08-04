from configparser import ConfigParser
import os
import json
import requests
from pathlib import Path
from .log import Log
import traceback

MOD='cdraw'
DEFAULT_COLOR=False
CONFIGFILE=os.path.expanduser(f"~/.{MOD}")
DEFAULT_CONFIG = {
                   # this is used as a common interface if
                   # the configfile is missing
                   MOD:{
                           'color': DEFAULT_COLOR,
                           'title_color': 'cyan',
                           'menu_color': 'green',
                           'control_color': 'magenta',
                           'select':'both',
                   }
                 }
AVAILABLE_COLORS = {'cyan'    :'[[C]]',
                    'green'   :'[[G]]',
                    'magenta' :'[[P]]',
                    'yellow'  :'[[Y]]',
                    'red'     :'[[R]]',
                    'blue'    :'[[B]]',
                    'white'   :'[[W]]',
                   }

class Config():
    def __init__(self, args=None):
        self._args = args
        # allow args from click/commandline to override config file
        if args:
            if args['color'] and args['nocolor']:
                print("ERROR: -c/--color and -n/--nocolor are mutually "+\
                      "exclusive options")
                exit(1)
            if args['color']: self.color = True
            if args['nocolor'] : self.color = False
        self._log = Log(color=self.color)


    @property
    def configfile(self):
        return CONFIGFILE


    @property
    def color(self):
        if '_color' not in self.__dict__:
            self._color = self.get_bool(MOD,'color',
                           default=DEFAULT_CONFIG[MOD]['color'])
        return self._color
    @color.setter
    def color(self,c):
        if not isinstance(c, bool):
            raise TypeError('Config.color must be set to a boolean.')
        self._color = True if c else False

    @property
    def title_color(self):
        if '_title_color' not in self.__dict__:
            self._title_color = self.get_item(MOD, 'title_color',
                           default=DEFAULT_CONFIG[MOD]['title_color'])
        return self._title_color

    @title_color.setter
    def title_color(self,c):
        if c.lower().strip() in AVAILABLE_COLORS:
            self._title_color = c.lower().strip()
            return
        raise Exception(f"'{c}' not in available colors: {AVAILABLE_COLORS}")

    @property
    def menu_color(self):
        if '_menu_color' not in self.__dict__:
            self._menu_color = self.get_item(MOD, 'menu_color',
                           default=DEFAULT_CONFIG[MOD]['menu_color'])
        return self._menu_color

    @menu_color.setter
    def menu_color(self,c):
        if c.lower().strip() in AVAILABLE_COLORS:
            self._menu_color = c.lower().strip()
            return
        raise Exception(f"'{c}' not in available colors: {AVAILABLE_COLORS}")

    @property
    def control_color(self):
        if '_control_color' not in self.__dict__:
            self._control_color = self.get_item(MOD, 'control_color',
                           default=DEFAULT_CONFIG[MOD]['control_color'])
        return self._control_color

    @control_color.setter
    def control_color(self,c):
        if c.lower().strip() in AVAILABLE_COLORS:
            self._control_color = c.lower().strip()
            return
        raise Exception(f"'{c}' not in available colors: {AVAILABLE_COLORS}")

    @property
    def select(self):
        if '_select' not in self.__dict__:
            self._select = self.get_item(MOD,'select',
                           default=DEFAULT_CONFIG[MOD]['select'])
        return self._select

    @select.setter
    def select(self, s):
        if s not in ['arrow','highlight','both']:
            raise ValueError("Config.select must be one of "+\
                             "['arrow','highlight','both']")
        self._select = s

    @property
    def cf(self):
        if '_cf' not in self.__dict__:
            self.cf = CONFIGFILE
        return self._cf

    @cf.setter
    def cf(self, f):
        cf = ConfigParser()
        if os.path.isfile(f):
            cf.read(f)
            self._cf = cf
            return
        else:
            cf.read_dict(DEFAULT_CONFIG)
            self._cf = cf
            self.save()

    @property
    def log(self):
        return self._log

    @property
    def args(self):
        return self._args

    def save(self):
        c = ConfigParser()
        c[MOD]={
           'color':self.color,
           'menu_color':self.menu_color,
           'title_color':self.title_color,
           'control_color':self.control_color,
           'select':self.select,
        }
        with open(CONFIGFILE, 'w', encoding='utf-8') as cf:
            c.write(cf)

    def get_item(self,section,item,default=None):
        """
          Retrieve a config value from the specified section,
          returning default if not found.
        """
        if self.cf.has_option(section, item):
            return self.cf[section][item]
        return default

    def get_bool(self,section,item,default=None):
        if self.cf.has_option(section,item):
            return self.cf.getboolean(section,item)
        return default

