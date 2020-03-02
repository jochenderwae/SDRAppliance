import pygame
import numpy
import math
from view.UIComponents import UIComponent
from view.Styling import style

WATERFALL_GRAD = [(0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 0)]

# Color and gradient interpolation functions used by waterfall spectrogram.
def lerp(x, x0, x1, y0, y1):
    """Linear interpolation of value y given min and max y values (y0 and y1),
    min and max x values (x0 and x1), and x value.
    """
    return y0 + (y1 - y0)*((x - x0)/(x1 - x0))

def rgb_lerp(x, x0, x1, c0, c1):
    """Linear interpolation of RGB color tuple c0 and c1."""
    return (math.floor(lerp(x, x0, x1, float(c0[0]), float(c1[0]))),
            math.floor(lerp(x, x0, x1, float(c0[1]), float(c1[1]))),
            math.floor(lerp(x, x0, x1, float(c0[2]), float(c1[2]))))

def gradient_func(colors):
    """Build a waterfall color function from a list of RGB color tuples.  The
    returned function will take a numeric value from 0 to 1 and return a color
    interpolated across the gradient of provided RGB colors.
    """
    grad_width = 1.0 / (len(colors)-1.0)
    def _fun(value):
        if value <= 0.0:
            return colors[0]
        elif value >= 1.0:
            return colors[-1]
        else:
            pos = int(value / grad_width)
            c0 = colors[pos]
            c1 = colors[pos+1]
            x = (value % grad_width)/grad_width
            return rgb_lerp(x, 0.0, 1.0, c0, c1)
    return _fun


class SpectrumPanel(UIComponent):
    def __init__(self, model) :
        super().__init__();
        self.model = model;
        self.data = None;
        w, h = self.getPreferredSize();
        self.graph = pygame.Surface((w, h));
        self.min_intensity = -70;
        self.range = 70;

    def getPreferredSize(self) :
        return (300, 100);

    def setRect(self, rect) :
        if not rect == self.rect :
            x, y, w, h = rect;
            self.graph = pygame.Surface((w, h));
        super().setRect(rect);

    def doRender(self, screen) :
        super().doRender(screen);
        if not self.data :
            return;

        # Convert scaled values to pixels drawn at the bottom of the display.
        x, y, w, h = self.getRect();
        dataLength = len(self.data);

        # Scale the FFT values to the range 0 to 1.
        self.data = 1 - (numpy.array(self.data, dtype=float) - self.min_intensity) / self.range;
        self.data = numpy.pad(self.data, int((w - (dataLength%w)) / 2), mode='edge');
        self.data = numpy.reshape(self.data, (w, int(len(self.data)/w)));
        self.data = numpy.mean(self.data, axis=1);

        backgroundColor = style.getStyle(self, "background.color");
        lineColor = style.getStyle(self, "line.color");
        self.graph.lock();
        self.graph.fill(backgroundColor, (0, 0, w, h));
        lasty = self.data[0];
        for gx in range(1, w):
            gy=self.data[gx-1];
            pygame.draw.line(self.graph, lineColor, (gx-1, lasty*h), (gx, gy*h));
            #pygame.draw.line(screen, freqshow.GRID_LINE, (i, y), (i, height))
            lasty = gy;
        self.graph.unlock()
        screen.blit(self.graph, (x, y), area=(0, 0, w, h))

    def dataListener(self, data) :
        self.data = data;
        self.invalidate();

class BandPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;
        self.data = None;

    def getPreferredSize(self) :
        return (300, 50);

    def doRender(self, screen) :
        super().doRender(screen);

    def dataListener(self, data) :
        self.data = data;
        self.invalidate();

class WaterfallPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;
        self.data = None;
        w, h = self.getPreferredSize();
        self.waterfall = pygame.Surface((w, h));
        self.color_func = gradient_func(WATERFALL_GRAD);
        self.min_intensity = -70;
        self.range = 70;

    def getPreferredSize(self) :
        return (300, 400);

    def setRect(self, rect) :
        if not rect == self.rect :
            x, y, w, h = rect;
            self.waterfall = pygame.Surface((w, h));
        super().setRect(rect);

    def doRender(self, screen) :
        super().doRender(screen);
        if not self.data :
            return;

        # Convert scaled values to pixels drawn at the bottom of the display.
        x, y, w, h = self.getRect();
        dataLength = len(self.data);

        # Scroll up the waterfall display.
        self.waterfall.scroll(0, -1);

        # Scale the FFT values to the range 0 to 1.
        self.data = (numpy.array(self.data, dtype=float) - self.min_intensity) / self.range;
        self.data = numpy.pad(self.data, int((w - (dataLength%w)) / 2), mode='edge');
        self.data = numpy.reshape(self.data, (w, int(len(self.data)/w)));
        self.data = numpy.mean(self.data, axis=1);

        # Draw FFT values mapped through the gradient function to a color.
        self.waterfall.lock();

        for gx in range(w) :
            power = max(min(self.data[gx], 1.0), 0.0);
            self.waterfall.set_at((gx, h-1), self.color_func(power))
        self.waterfall.unlock()
        screen.blit(self.waterfall, (x, y), area=(0, 0, w, h))

    def dataListener(self, data) :
        self.data = data;
        self.invalidate();
