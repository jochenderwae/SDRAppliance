#!/bin/python3

from model.PluginModel import *;

class Application:
    def __init__(self):
        self.pluginModel = PluginModel();

    def start(self):
        self.pluginModel.compilePlugins();
        self.pluginModel.loadPlugins();


def main():
    application = Application();
    application.start();


if __name__ == '__main__':
    main();
