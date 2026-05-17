from dataclasses import dataclass

@dataclass
class Palette:
    def to_list(self) -> list:
        return list(self.__dict__.values())

@dataclass
class ANSI_Palette(Palette):
    black: str
    red: str
    green: str
    yellow: str
    blue: str
    magenta: str
    cyan: str
    white: str
    bright_black: str
    bright_red: str
    bright_green: str
    bright_yellow: str
    bright_blue: str
    bright_magenta: str
    bright_cyan: str
    bright_white: str

@dataclass
class Git_Palette(Palette):
    added: str
    modified: str
    deleted: str
    ignored: str
    untracked: str
    conflicting: str

@dataclass
class UI_Palette(Palette):
    background: str
    borders: str
    normal_text: str
    light_text: str

