import pygame
from view.UIComponents import UIComponent

class SpectrumPanel(UIComponent):
    def __init__(self, model) :
        super().__init__();
        self.model = model;
        self.bg_color     = (0, 0, 0)

    def getPreferredSize(self) :
        return (400, 100);

    def doRender(self, screen) :
        screen.fill(self.bg_color, self.rect)
        pygame.draw.rect(screen, (128, 0, 0), self.rect, 1)

class BandPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;
        self.bg_color     = (0, 0, 0)

    def getPreferredSize(self) :
        return (400, 50);

    def doRender(self, screen) :
        screen.fill(self.bg_color, self.rect)
        pygame.draw.rect(screen, (128, 0, 0), self.rect, 1)

class WaterfallPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;
        self.bg_color     = (0, 0, 0)

    def getPreferredSize(self) :
        return (400, 200);

    def doRender(self, screen) :
        screen.fill(self.bg_color, self.rect)
        pygame.draw.rect(screen, (128, 0, 0), self.rect, 1)
