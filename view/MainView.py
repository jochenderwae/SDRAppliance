


import pygame
import os

from view.LayoutManagers import *
from view.UIComponents import *
from view.RadioComponents import *
from view.Styling import style

MAIN_BG        = (   5,  45,  45) # Dark Brown
DEBUG = True;


class MainView :
    def __init__(self) :
        self.controller = None;
        self.screenPanel = None;
        self.radioPlaying = False;
        self.frequencySpinnerGroup = None;

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


    def getId(self) :
        return "MainView";

    def getDrawState(self) :
        return "";

    def buildUI(self) :
        frequencyPanel = Panel(GridLayout(rows=1));
        digits = 10;
        self.frequencySpinnerGroup = SpinnerGroup();
        for digit in range(digits):
            power = digits - digit;
            button = Spinner(0);
            self.frequencySpinnerGroup.add(button);
            frequencyPanel.add(button);
            if (digits - digit - 1) % 3 == 0 and digit < digits - 1 :
                frequencyPanel.add(Label("."));
        frequencyPanel.add(Label("Hz"));
        self.frequencySpinnerGroup.setValue(self.controller.radio.getFrequency());
        self.frequencySpinnerGroup.addUpdateHandler(self.frequencyUpdateListener);

        frequencyCenterPanel = Panel(AlignLayout(AlignLayout.CENTER));
        frequencyCenterPanel.add(frequencyPanel);

        spectrumPanel = SpectrumPanel(self.controller);
        self.controller.addFFTDataListener(spectrumPanel.dataListener);
        bandPanel = BandPanel(self.controller);
        self.controller.addFFTDataListener(bandPanel.dataListener);
        waterfallPanel = WaterfallPanel(self.controller);
        self.controller.addFFTDataListener(waterfallPanel.dataListener);

        topLeftPanel = Panel(BorderLayout());
        topLeftPanel.add(frequencyCenterPanel, BorderLayout.TOP);
        topLeftPanel.add(spectrumPanel, BorderLayout.CENTER);
        topLeftPanel.add(bandPanel, BorderLayout.BOTTOM);

        leftPanel = Panel(BorderLayout());
        leftPanel.add(topLeftPanel, BorderLayout.CENTER);
        leftPanel.add(waterfallPanel, BorderLayout.BOTTOM);


        startButton = Button(style.getIcon(self, "icon.play"));
        startButton.addClickEvent(self.startPause);

        exitButton = Button(style.getIcon(self, "icon.close"));
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
        radioGroup = RadioGroup();
        for demodulator in demodulators :
            def buildOnClick(controller, demod) :
                def onClick(source) :
                    controller.setDemodulator(demod)
                return onClick

            demodulatorButton = RadioButton(radioGroup, demodulator);
            demodulatorButton.addClickEvent(buildOnClick(self.controller, demodulator));
            bottomButtonPanel.add(demodulatorButton);

        settingsButton = Button(style.getIcon(self, "icon.settings"));

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

    def setController(self, controller) :
        self.controller = controller;

    def getController(self) :
        return self.controller;

    def frequencyUpdateListener(self, spinnerGroup, value) :
        self.controller.radio.setFrequency(value);

    def quitApplication(self, source=None) :
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
