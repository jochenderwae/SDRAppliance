


import pygame
from svg import Parser, Rasterizer
import os

from view.LayoutManagers import *
from view.UIComponents import *
from view.RadioComponents import *

MAIN_BG        = (   5,  45,  45) # Dark Brown
DEBUG = True;


class MainView :
    def __init__(self) :
        self.controller = None;
        self.screenPanel = None;
        self.radioPlaying = False;

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


    def buildUI(self) :
        frequencyPanel = Panel(GridLayout(rows=1));
        digits = 10;
        for digit in range(digits):
            power = digits - digit;
            button = Spinner(0);
            frequencyPanel.add(button);

        frequencyCenterPanel = Panel(AlignLayout(AlignLayout.CENTER));
        frequencyCenterPanel.add(frequencyPanel);

        spectrumPanel = SpectrumPanel(self.controller);
        bandPanel = BandPanel(self.controller);
        waterfallPanel = WaterfallPanel(self.controller);

        topLeftPanel = Panel(BorderLayout());
        topLeftPanel.add(frequencyCenterPanel, BorderLayout.TOP);
        topLeftPanel.add(spectrumPanel, BorderLayout.CENTER);
        topLeftPanel.add(bandPanel, BorderLayout.BOTTOM);

        leftPanel = Panel(BorderLayout());
        leftPanel.add(topLeftPanel, BorderLayout.CENTER);
        leftPanel.add(waterfallPanel, BorderLayout.BOTTOM);


        playIcon = self.renderIcon('icons/play.svg');
        exitIcon = self.renderIcon('icons/x.svg');
        startButton = Button(playIcon);
        startButton.addClickEvent(self.startPause);

        exitButton = Button(exitIcon);
        exitButton.addClickEvent(self.quitApplication);

        topButtonPanel = Panel(GridLayout(cols=2));
        topButtonPanel.add(startButton);
        topButtonPanel.add(exitButton);


        volumeSlider = Slider("Volume", min=0, max=100);
        gainSlider = Slider("Gain", min=0, max=30);

        sliderPanel = Panel(GridLayout(cols=2));
        sliderPanel.add(volumeSlider);
        sliderPanel.add(gainSlider);


        bottomButtonPanel = Panel(GridLayout(cols=2));
        demodulators = self.controller.getDemodulators();
        for demodulator in demodulators :
            demodulatorButton = Button(demodulator);
            bottomButtonPanel.add(demodulatorButton);

        settingsIcon = self.renderIcon('icons/settings.svg');
        settingsButton = Button(settingsIcon);

        bottomButtonPanel.add(settingsButton);


        rightPanel = Panel(BorderLayout());
        rightPanel.add(topButtonPanel, BorderLayout.TOP);
        rightPanel.add(sliderPanel, BorderLayout.CENTER);
        rightPanel.add(bottomButtonPanel, BorderLayout.BOTTOM);

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

    def quitApplication(self, source) :
        self.keepRunning = False;

    def startPause(self, source) :
        if not self.radioPlaying :
            self.radioPlaying = True;
            self.controller.startRadio();
        else :
            self.radioPlaying = False;
            self.controller.stopRadio();

    def start(self) :
        self.buildUI();
        lastclick = 0;
        self.keepRunning = True;
        while self.keepRunning:
            # Process any events (only mouse events for now).
            for event in pygame.event.get():
                if event.type == pygame.QUIT :
                    self.quitApplication();
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION :
                    self.screenPanel.doHandleMouseEvent(event);
            self.screenPanel.render(self.screen);
            pygame.display.update();

    def stop(self) :
        pass;
