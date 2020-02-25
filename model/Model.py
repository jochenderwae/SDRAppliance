
from model.PluginModel import *;


class Model :
    def __init__(self) :
        self.pluginModel = PluginModel();

    def start(self) :
        self.pluginModel.compilePlugins();
        self.pluginModel.loadPlugins();

    def stop(self) :
        pass;

    def getPluginModel(self) :
        return self.pluginModel;
