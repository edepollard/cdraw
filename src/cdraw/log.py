
COLOR_CODES = [
      {"color":"red","string":"[[R]]","bash":"\x01\033[31m\x02"},
      {"color":"green","string":"[[G]]","bash":"\x01\033[32m\x02"},
      {"color":"yellow","string":"[[Y]]","bash":"\x01\033[33m\x02"},
      {"color":"blue","string":"[[B]]","bash":"\x01\033[34m\x02"},
      {"color":"purple","string":"[[P]]","bash":"\x01\033[35m\x02"},
      {"color":"cyan","string":"[[C]]","bash":"\x01\033[36m\x02"},
      {"color":"white","string":"[[W]]","bash":"\x01\033[37m\x02"},
      {"color":"end","string":"[[E]]","bash":"\x01\033[0m\x02"}
]

class Log:
    def __init__(self, color=False):
        self._color = color

    def __call__(self, msg):
        """Allow Log instance to be called directly as a function to print messages."""
        self.stdout(msg)

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, bool_setting):
        if isinstance(bool_setting, bool):
            self._color = bool_setting
        else:
            e = f"bool_setting needs to be a boolean not {type(bool_setting)}"
            raise TypeError(e)

    def stdout(self, msg):
        """Print message to stdout with color encoding applied."""
        print(self.encodeColor(msg), flush=True)

    def error(self, msg, fatal=False, error_code=1):
        """Print error message, optionally exiting the program if fatal."""
        prefix = "Fatal Error:" if fatal else "Error:"
        self.stdout(f"{prefix} {msg}")
        if fatal: exit(error_code)

    def fatal(self, msg, error_code=1):
        """Print fatal error message and exit the program."""
        self.error(msg,fatal=True, error_code=1)

    def stripColor(self, textin):
        """Remove all color markup tokens from text, returning plain string."""
        for color in COLOR_CODES:
            textin = textin.replace(color['string'],"")
        return textin

    def enableColor(self):
        """Enable color output for all subsequent messages."""
        self.color = True

    def disableColor(self):
        """Disable color output for all subsequent messages."""
        self.color = False

    def encodeColor(self,textin):
        """Convert custom color tokens ([[R]], [[G]], etc.) to ANSI codes or strip them if color disabled."""
        if self.color:
            for color in COLOR_CODES:
                textin = str(textin)
                textin = textin.replace(color['string'],color['bash'])
        else:
            textin = self.stripColor(textin)
        return textin



