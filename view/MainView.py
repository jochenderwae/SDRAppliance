


import pygame
from svg import Parser, Rasterizer
import os
import time

from view.LayoutManagers import *
from view.UIComponents import *
from view.RadioComponents import *

MAIN_BG        = (   5,  45,  45) # Dark Brown
CLICK_DEBOUNCE  = 0.04
DEBUG = True;


class MainView :
    def __init__(self) :
        self.controller = None;
        self.screenPanel = None;

        # set parameters if these devices are available
        if os.path.isfile("/dev/fb1") :
        	os.putenv('SDL_VIDEODRIVER', 'fbcon');
        	os.putenv('SDL_FBDEV'      , '/dev/fb1');

        if os.path.isfile("/dev/input/touchscreen") :
        	os.putenv('SDL_MOUSEDRV'   , 'TSLIB');
        	os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen');

        pygame.display.init();
        pygame.font.init();
        pygame.mouse.set_visible(True);
        # Get size of screen and create main rendering surface.
        if DEBUG:
            self.size = (int(pygame.display.Info().current_w / 2), int(pygame.display.Info().current_h / 2));
            self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE);
        else :
            self.size = (int(pygame.display.Info().current_w), int(pygame.display.Info().current_h));
            self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE);
        self.screen.fill(MAIN_BG);
        pygame.display.update();
        # Create model and controller.
        #fsmodel = model.FreqShowModel(size[0], size[1]);
        #fscontroller = controller.FreqShowController(fsmodel);
        #time.sleep(2.0)
        # Main loop to process events and render current view.
        #self.buildUI();

    def buildUI(self) :
        frequencyPanel = Panel(GridLayout(rows=1));
        digits = 10;
        for digit in range(digits):
            power = digits - digit;
            button = Spinner(0);
            frequencyPanel.add(button);

        spectrumPanel = SpectrumPanel(self.controller);
        bandPanel = BandPanel(self.controller);
        waterfallPanel = WaterfallPanel(self.controller);

        topLeftPanel = Panel(BorderLayout());
        topLeftPanel.add(frequencyPanel, BorderLayout.TOP);
        topLeftPanel.add(spectrumPanel, BorderLayout.CENTER);
        topLeftPanel.add(bandPanel, BorderLayout.BOTTOM);

        leftPanel = Panel(BorderLayout());
        leftPanel.add(topLeftPanel, BorderLayout.CENTER);
        leftPanel.add(waterfallPanel, BorderLayout.BOTTOM);


        playIcon = self.renderIcon('icons/play.svg');
        exitIcon = self.renderIcon('icons/x.svg');
        startButton = Button(playIcon);
        exitButton = Button(exitIcon);

        topButtonPanel = Panel(GridLayout(cols=2));
        topButtonPanel.add(startButton);
        topButtonPanel.add(exitButton);


        volumeSlider = Slider("Volume", min=0, max=100);
        gainSlider = Slider("Gain", min=0, max=30);

        sliderPanel = Panel(GridLayout(cols=2));
        sliderPanel.add(volumeSlider);
        sliderPanel.add(gainSlider);


        demodulatorPanel = Panel(GridLayout(cols=2));
        demodulators = self.controller.getDemodulators();
        for demodulator in demodulators :
            demodulatorButton = Button(demodulator);
            demodulatorPanel.add(demodulatorButton);

        rightMiddlePanel = Panel(BorderLayout());
        rightMiddlePanel.add(sliderPanel, BorderLayout.CENTER);
        rightMiddlePanel.add(demodulatorPanel, BorderLayout.BOTTOM);


        settingsIcon = self.renderIcon('icons/settings.svg');
        settingsButton = Button(settingsIcon);

        bottomPanel = Panel(GridLayout(cols=2));
        bottomPanel.add(settingsButton);

        rightPanel = Panel(BorderLayout());
        rightPanel.add(topButtonPanel, BorderLayout.TOP);
        rightPanel.add(rightMiddlePanel, BorderLayout.CENTER);
        rightPanel.add(bottomPanel, BorderLayout.BOTTOM);

        self.screenPanel = Panel(BorderLayout());
        width, height = self.size;
        self.screenPanel.setRect((0, 0, width, height));
        self.screenPanel.add(leftPanel, BorderLayout.CENTER);
        self.screenPanel.add(rightPanel, BorderLayout.RIGHT);


    def renderIcon(self, path, size=None) :
        if size is None:
            w = h = 32;
        else:
            w, h = size;
        svg = Parser.parse_file(path);
        rast = Rasterizer();
        buff = rast.rasterize(svg, w, h);
        return pygame.image.frombuffer(buff, (w, h), 'ARGB');


    def setController(self, controller) :
        self.controller = controller;

    def getController(self) :
        return self.controller;

    def start(self) :
        self.buildUI();
        lastclick = 0;
        keepRunning = True;
        while keepRunning:
            # Process any events (only mouse events for now).
            for event in pygame.event.get():
                if event.type is pygame.MOUSEBUTTONDOWN \
                and (time.time() - lastclick) >= CLICK_DEBOUNCE:
                    lastclick = time.time();
                    keepRunning = False;
            #fscontroller.current().click(pygame.mouse.get_pos());
            # Update and render the current view.
            #fscontroller.current().render(screen);
            self.screenPanel.render(self.screen);
            pygame.display.update();
        print("end loop");

    def stop(self) :
        pass;
