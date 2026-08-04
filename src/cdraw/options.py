
class OptionIterator:
    def __init__(self, options):
        self.options = options
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.options):
            raise StopIteration
        option = self.options[self.index]
        self.index += 1
        return option

class Option:
    def __init__(self, text, action, menu_char=0, color=False):
        self._text = None
        self._menu_char = menu_char
        self._action = action
        self._color = color
        self.text = text


    def __str__(self):
        return self.text
    def __repr__(self):
        return f"<Option text:'{self.text}' "+\
               f"action:{self.action} "+\
               f"menu_char:{self.menu_char}>"

    @property
    def menu_char(self):
        return self._menu_char
    @menu_char.setter
    def menu_char(self, c):
        if not c or (len(c) == 1  and c.isalpha()):
            self._menu_char = False
            return
        raise TypeError("<Option>.menu_char must be a letter or False ")

    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, item):
        if not isinstance(item,str):
            raise TypeError(
                 "<Option>.text must be of type 'str' not '{type(item)}'.")
        self._text = item

    @property
    def action(self):
        return self._action
    @action.setter
    def action(self, i):
        self._action = i

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self, c):
        self._color = c

    def run(self, terminate=True):
        if self.action:
            self.action.run(terminate=terminate)
        else:
            raise Exception(f"{repr(self)} has no action.")

    @classmethod
    def control(cls, text, action, menu_char):
        return cls(text, action, menu_char=menu_char)


class Options:
    def __init__(self, items=[], allow_duplicates=True):
        self._items = items
        self.allow_duplicates = allow_duplicates
        self.items = self._items

    @property
    def items(self):
        return self._items
    @items.setter
    def items(self, itms):
        if isinstance(itms, Option):
           self.add(itms)
           return
        if isinstance(itms, list) or\
           isinstance(itms, tuple):
           self._items = []
           [self.add(i) for i in itms]
           return
        raise TypeError(
           f"<Options> items be <Option> or list/tuple of <Option>")

    def add(self, i):
        if isinstance(i, Option):
           if i.text in [n.text for n in self.items] and\
              not self.allow_duplicates:
               raise ValueError(
                     f"Duplicate option found: '{i.text}' exists")
           if i.menu_char in [c.menu_char for c in self.items] and\
              not self.allow_duplicates:
               raise ValueError(
                     f"Duplicate option found: '{i.menu_char}' exists")
           self._items.append(i)
        else:
           raise TypeError(f"Items must be of type <Option>.")
    def append(self, i):
        self.add.append(i)
    def extend(self, i):
        if isinstance(i, Option):
           self.add(i)
           return
        if isinstance(i, list) or\
           isinstance(i, tuple):
           [self.add(m) for m in i]
           return
        raise TypeError(
           f"<Options> items must <Option> or tuple/list of <Options>")

    @property
    def length(self):
        return len(self.items)

    def __iter__(self):
        return OptionIterator(self.items)
    def __str__(self):
        return f"{[str(i) for i in self]}"
    def __repr__(self):
        return f"<Options {[str(i) for i in self]}>"
    def __call__(self):
       return self.items




