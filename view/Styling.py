
import os
import pygame
from svg import Parser, Rasterizer


class Styling :
    ICONS_PATH = ["icons"];

    def __init__(self, style) :
        self.style = style;
        self.fontCache = {};
        self.iconCache = {};

    def getStyle(self, component, key) :
        componentClass = type(component).__name__;
        componentId = component.getId();
        componentDrawState = component.getDrawState();
        keys = ["{}.{}.{}.{}".format(key, componentClass, componentId, componentDrawState),
            "{}.{}.{}".format(key, componentId, componentDrawState),
            "{}.{}.{}".format(key, componentClass, componentDrawState),
            "{}.{}".format(key, componentDrawState),
            "{}.{}.{}".format(key, componentClass, componentId),
            "{}.{}".format(key, componentId),
            "{}.{}".format(key, componentClass),
            key];

        for key in keys :
            try :
                value = self.style[key];
                return value;
            except KeyError:
                pass;
        return None;

    def getFont(self, component, key) :
        name = self.getStyle(component, "{}.{}".format(key, "name"));
        size = self.getStyle(component, "{}.{}".format(key, "size"));
        fontID = "{}_{}".format(name, size);
        if fontID not in self.fontCache:
            self.fontCache[fontID] = pygame.font.Font(name, int(size));
        return self.fontCache[fontID];

    def getIcon(self, component, key) :
        name = self.getStyle(component, "{}.{}".format(key, "name"));
        size = self.getStyle(component, "{}.{}".format(key, "size"));

        iconPath = os.path.join(*Styling.ICONS_PATH, name);
        iconID = "{}_{}".format(name, size);

        if type(size) is int:
            w = h = size;
        elif type(size) is tuple:
            w, h = size;
        else:
            w = h = 32;

        if iconID not in self.iconCache:
            svg = Parser.parse_file(iconPath);
            rast = Rasterizer();
            buff = rast.rasterize(svg, w, h);
            self.iconCache[iconID] = pygame.image.frombuffer(buff, (w, h), 'ARGB');
        return self.iconCache[iconID];

style = Styling({
    "background.color": (0, 0, 0), # black background
    "foreground.color": (255, 255, 255), # white text
    "placeholder.color": (64, 64, 64),
    "mask.color":       (0, 0, 0, 192),
    "border.color":     None,
    "border.size":      None,

    "font.size":        18,
    "font.size.BandPanel": 24,

    "font.size.Spinner": 50,

    "icon.settings.name": "settings.svg",
    "icon.settings.size": 24,
    "icon.close.name":    "x.svg",
    "icon.close.size":    24,
    "icon.play.name":     "play.svg",
    "icon.play.size":     24,
    "icon.up.name":       "arrow-up.svg",
    "icon.up.size":       24,
    "icon.down.name":     "arrow-down.svg",
    "icon.down.size":     24,

    "border.color.Button": (128, 128, 128),
    "border.size.Button":  1,
    "border.color.RadioButton": (128, 128, 128),
    "border.size.RadioButton":  1,
    "border.size.RadioButton.selected":3,

    "line.color.major":   (192, 192, 192),
    "line.color.minor":   (128, 128, 128),
    "line.color.center":  (255, 255, 255),
    "line.color.graph":   (150, 255, 255),

    "padding":          (5, 5, 5, 5),
});
