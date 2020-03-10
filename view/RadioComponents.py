import pygame
import numpy
import math
from view.UIComponents import UIComponent
from view.Styling import style
from quantiphy import Quantity

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
        self.minPower = 30;
        self.range = 60;

    def getPreferredSize(self) :
        return (300, 100);

    def setRect(self, rect) :
        if not rect == self.rect :
            x, y, w, h = rect;
            self.graph = pygame.Surface((w, h));
        super().setRect(rect);

    def doRender(self, screen) :
        super().doRender(screen);
        x, y, w, h = self.getRect();

        if self.data is not None :
            dataLength = len(self.data);

            # Scale the FFT values to the range 0 to 1.
            self.data = - (numpy.array(self.data, dtype=float) + self.minPower) / self.range;
            self.data = numpy.pad(self.data, int((w - (dataLength%w)) / 2), mode='edge');
            self.data = numpy.reshape(self.data, (w, int(len(self.data)/w)));
            self.data = numpy.mean(self.data, axis=1);

            backgroundColor = style.getStyle(self, "background.color");
            lineColor = style.getStyle(self, "line.color.graph");
            self.graph.lock();
            self.graph.fill(backgroundColor, (0, 0, w, h));
            lasty = self.data[0];
            for gx in range(1, w):
                gy=self.data[gx-1];
                pygame.draw.line(self.graph, lineColor, (gx-1, lasty*h), (gx, gy*h));
                #pygame.draw.line(screen, freqshow.GRID_LINE, (i, y), (i, height))
                lasty = gy;
            self.graph.unlock();

        screen.blit(self.graph, (x, y), area=(0, 0, w, h))
        self.data = None;

    def dataListener(self, radio, data) :
        self.data = data;
        self.invalidate();

class BandPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;
        self.data = None;
        self.labels = {};
        self.tickLines = [];
        self.midLabel = None;
        self.minorLineColor = style.getStyle(self, "line.color.minor");
        self.majorLineColor = style.getStyle(self, "line.color.major");
        self.centerLineColor = style.getStyle(self, "line.color.center");
        self.font = style.getFont(self, "font");
        self.foreground = style.getStyle(self, "foreground.color");
        self.background = style.getStyle(self, "background.color");

    def getPreferredSize(self) :
        return (300, 50);

    def doRender(self, screen) :
        super().doRender(screen);
        if self.data is None :
            return;

        dataLength = len(self.data);
        x, y, w, h = self.getRect();

        midX = dataLength / 2;
        offset = w - (dataLength%w);
        dataLength = dataLength + offset;

        for tickX in self.tickLines :
            tickX = tickX + offset / 2;
            tickX = int(tickX * w / dataLength);
            pygame.draw.line(screen, self.minorLineColor, (x + tickX, y), (x + tickX, y + 10));

        for gx in self.labels:
            label = self.labels[gx];
            labelX,labelY,labelWidth,labelHeight = label.get_rect();
            gx = gx + offset / 2;
            gx = int(gx * w / dataLength);
            pygame.draw.line(screen, self.majorLineColor, (x + gx, y), (x + gx, y + h));
            screen.blit(label,(x + gx - labelWidth / 2, y + h - labelHeight));

        labelX,labelY,labelWidth,labelHeight = self.midLabel.get_rect();
        midX = midX + offset / 2;
        midX = int(midX * w / dataLength);
        pygame.draw.line(screen, self.centerLineColor, (x + midX, y), (x + midX, y + h));
        screen.blit(self.midLabel,(x + midX - labelWidth / 2, y + labelHeight));

    def dataListener(self, radio, data) :
        self.data = data;

        mid = len(data)/2;

        digits = math.ceil(math.log10(radio.frequency));
        majorDivisor = math.pow(10, digits - 3);
        nearestFrequency = math.floor(radio.frequency / majorDivisor) * majorDivisor;

        binFrequency = radio.getBinFrequency();

        self.midLabel = self.font.render("{:9s}".format(Quantity(radio.frequency, "Hz")), True, self.foreground, self.background);

        self.tickLines = [];
        for i in range(19) :
            if i == 10 :
                continue;
            pos = 1e5 * i;
            if mid + (nearestFrequency + pos - radio.frequency) / binFrequency < radio.fftBinSize :
                self.tickLines.append(mid + (nearestFrequency + pos - radio.frequency) / binFrequency);
            if mid + (nearestFrequency - pos - radio.frequency) / binFrequency > 0 :
                self.tickLines.append(mid + (nearestFrequency - pos - radio.frequency) / binFrequency);

        self.labels = {};
        for step in [-1e6, 0, 1e6]:
            if not nearestFrequency + step == radio.frequency:
                binsOffset = (nearestFrequency - radio.frequency + step) / binFrequency;
                self.labels[mid + binsOffset] = self.font.render("{:9s}".format(Quantity(nearestFrequency + step, "Hz")), True, self.foreground, self.background);

        self.invalidate();

class WaterfallPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;
        self.data = None;
        w, h = self.getPreferredSize();
        self.waterfall = pygame.Surface((w, h));
        self.color_func = gradient_func(WATERFALL_GRAD);
        self.minPower = 30;
        self.range = 60;

    def getPreferredSize(self) :
        return (300, 400);

    def setRect(self, rect) :
        if not rect == self.rect :
            x, y, w, h = rect;
            self.waterfall = pygame.Surface((w, h));
        super().setRect(rect);

    def doRender(self, screen) :
        super().doRender(screen);
        x, y, w, h = self.getRect();

        if self.data is not None :
            dataLength = len(self.data);

            # Scroll up the waterfall display.
            self.waterfall.scroll(0, 1);

            # Scale the FFT values to the range 0 to 1.
            self.data = - (numpy.array(self.data, dtype=float) + self.minPower) / self.range;
            self.data = numpy.pad(self.data, int((w - (dataLength%w)) / 2), mode='edge');
            self.data = numpy.reshape(self.data, (w, int(len(self.data)/w)));
            self.data = numpy.mean(self.data, axis=1);

            # Draw FFT values mapped through the gradient function to a color.
            self.waterfall.lock();

            for gx in range(w) :
                power = max(min(1 - self.data[gx], 1.0), 0.0);
                self.waterfall.set_at((gx, 0), self.color_func(power))
            self.waterfall.unlock();
        screen.blit(self.waterfall, (x, y), area=(0, 0, w, h))
        self.data = None;

    def dataListener(self, radio, data) :
        self.data = data;
        self.invalidate();
