import datetime

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

colors = {
    "[黒]": "\033[30m",
    "[赤]": "\033[31m",
    "[緑]": "\033[32m",
    "[黃]": "\033[33m",
    "[黄色]": "\033[33m",
    "[青]": "\033[34m",
    "[マゼンタ]": "\033[35m",
    "[シアン]": "\033[36m",
    "[白]": "\033[37m",
    "[反転]": "\033[7m",
    "[太字]": "\033[1m",
    "[アンダーライン]": "\033[4m",
    "[/]": "\033[0m",
}
theme = {
    "D": "\033[34m",
    "I": "\033[32m",
    "W": "\033[33m",
    "E": "\033[31m",
    "C": "\033[31;1;7m",
}

CRITICAL = 4
ERROR = 3
WARNING = 2
INFO = 1
DEBUG = 0


class logger:
    CRITICAL = 4
    ERROR = 3
    WARNING = 2
    INFO = 1
    DEBUG = 0

    def __init__(self, **kwargs):
        self.format = kwargs.get(
            "format", "[time] [theme_color]| [level] |[theme_end] [message]"
        )
        self.level = kwargs.get("level", self.DEBUG)
        self.time_format = kwargs.get("time_format", "%H:%M:%S")
        self.last_printed_time = ""

    def set_level(self, level):
        self.level = level

    def get_time(self):
        now = datetime.datetime.now()
        time_formated = now.strftime(self.time_format)

        if self.last_printed_time == time_formated:
            time_formated = " " * len(time_formated)
        else:
            self.last_printed_time = time_formated

        return time_formated

    def colorize(self, input_text):
        colorized_text = input_text

        for k, v in colors.items():
            colorized_text = colorized_text.replace(k, v)
        return colorized_text

    def main_str(self, level, message):
        message = self.colorize(message)
        message_elements = {
            "[time]": self.get_time(),
            "[theme_color]": theme.get(level),
            "[theme_end]": colors["[/]"],
            "[message]": message,
            "[level]": level,
        }

        print_message = self.colorize(self.format)

        for k, v in message_elements.items():
            print_message = print_message.replace(k, v)

        print_message = self.colorize(print_message)
        print(print_message)

    def main_dict(self, level, message):
        highlighted = highlight(str(message), PythonLexer(), TerminalFormatter())
        highlighted = self.colorize(highlighted)
        highlighted = highlighted.replace("\n", "")
        message_elements = {
            "[time]": self.get_time(),
            "[theme_color]": theme.get(level),
            "[theme_end]": colors["[/]"],
            "[message]": highlighted,
            "[level]": level,
        }

        print_message = self.colorize(self.format)

        for k, v in message_elements.items():
            print_message = print_message.replace(k, v)

        print_message = self.colorize(print_message)
        print(print_message)

    def main(self, level, message):
        if type(message) == str:
            self.main_str(level, message)
        elif type(message) == int:
            self.main_str(level, f"{message}")
        elif type(message) == list:
            self.main_dict(level, message)
        elif type(message) == dict:
            self.main_dict(level, message)
        else:
            self.main_str(level, str(message))

    def D(self, *messages):
        if self.level > self.DEBUG:
            return

        for message in messages:
            self.main("D", message)

    def I(self, *messages):
        if self.level > self.INFO:
            return

        for message in messages:
            self.main("I", message)

    def W(self, *messages):
        if self.level > self.WARNING:
            return

        for message in messages:
            self.main("W", message)

    def E(self, *messages):
        if self.level > self.ERROR:
            return

        for message in messages:
            self.main("E", message)

    def C(self, *messages):
        if self.level > self.CRITICAL:
            return

        for message in messages:
            self.main("C", message)

    def debug(self, *messages):
        if self.level > self.DEBUG:
            return

        for message in messages:
            self.main("D", message)

    def info(self, *messages):
        if self.level > self.INFO:
            return

        for message in messages:
            self.main("I", message)

    def warning(self, *messages):
        if self.level > self.WARNING:
            return

        for message in messages:
            self.main("W", message)

    def error(self, *messages):
        if self.level > self.ERROR:
            return

        for message in messages:
            self.main("E", message)

    def critilal(self, *messages):
        if self.level > self.CRITICAL:
            return

        for message in messages:
            self.main("C", message)
