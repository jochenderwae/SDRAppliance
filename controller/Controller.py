
from controller.Radio import *;

class Controller:
    def __init__(self) :
        self.model = None;
        self.radio = Radio();

    def setModel(self, model) :
        self.model = model;

    def getModel(self) :
        return self.model;

    def start(self) :
        plugins = self.model.getPluginModel().getDemodPlugins();
        self.radio.setDemod(plugins["FMReceiver"].createInstance());
        #self.startRadio();

    def stop(self) :
        self.stopRadio();

    def startRadio(self) :
        self.radio.start();

    def stopRadio(self) :
        self.radio.stop();

    def getDemodulators(self) :
        demodulators = self.model.getPluginModel().getDemodPlugins();
        return demodulators.keys();

    def setDemodulator(self, key) :
        demodulators = self.model.getPluginModel().getDemodPlugins();
        demodulator = demodulators[key];
        self.radio.setDemod(demodulator.createInstance());
