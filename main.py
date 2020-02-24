#!/bin/python3

from model.PluginModel import *;
from radio.Radio import *;

class Application:
    def __init__(self):
        self.pluginModel = PluginModel();

    def start(self):
        self.pluginModel.compilePlugins();
        self.pluginModel.loadPlugins();

        radio = Radio();
        radio.setDemod(self.pluginModel.getDemodPlugins()["FMRadio"]);
        radio.start();




def main():
    application = Application();
    application.start();


if __name__ == '__main__':
    main();
