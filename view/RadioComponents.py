import pygame
from view.UIComponents import UIComponent

class SpectrumPanel(UIComponent):
    def __init__(self, model) :
        super().__init__();
        self.model = model;

    def getPreferredSize(self) :
        return (300, 100);

    def doRender(self, screen) :
        super().doRender(screen);

class BandPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;

    def getPreferredSize(self) :
        return (300, 50);

    def doRender(self, screen) :
        super().doRender(screen);

class WaterfallPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;

    def getPreferredSize(self) :
        return (300, 200);

    def doRender(self, screen) :
        super().doRender(screen);
