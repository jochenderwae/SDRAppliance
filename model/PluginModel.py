import os
import sys
import importlib.util
import subprocess
import yaml
#try:
#    from yaml import CLoader as Loader
#except ImportError:
#    from yaml import Loader

GRC_COMPILER = "grcc";
WHEREIS_COMMAND = "whereis -b grcc";
GRC_COMPILER_PATH = "/usr/bin/grcc";
GRC_PYTHON_PATH = "~/.grc_gnuradio";
GRC_PLUGIN_PATH = ["plugins", "demod"];

class DemodPlugin:
    def __init__(self, pythonFile):
        self.pythonFile = pythonFile;
        self.ymlFile = pythonFile + ".block.yml";
        self.path = GRC_PYTHON_PATH;
        self.spec = None;
        self.module = None;
        self.pluginClass = None;
        self.parameters = {};
        self.id = None;

    def load(self):
        self.ymlFile = os.path.expanduser(self.path + "/" + self.ymlFile);
        self.pythonFile = os.path.expanduser(self.path + "/" + self.pythonFile);
        stream = open(self.ymlFile);
        data = yaml.load(stream, Loader=yaml.FullLoader);

        self.id = data["id"];
        if data["category"] != "SDRA DEMOD plugin":
            raise ImportError("Expected category to be 'SDRA DEMOD plugin', got {} instead".format(data["category"]));

        self.loadParameters(data["parameters"]);
        self.loadInputs(data["inputs"]);
        self.loadOutputs(data["outputs"]);
        self.loadModule();



    def loadParameters(self, parameters):
        for parameter in parameters:
            name = parameter["id"];
            value = parameter["default"];
            type = parameter["dtype"];
            if type == "real" :
                value = float(value);
            self.parameters[name] = value;



    def loadInputs(self, inputs):
        if len(inputs) != 1 :
            raise ImportError("There should be exactly one Sink");

        input = inputs[0];
        name = input["label"];
        type = input["dtype"];
        vlen = input["vlen"];

        if name != "rfIn" :
            raise ImportError("Expected input name to be 'rfIn', instead found {0}".format(name));

        if type != "complex" :
            raise ImportError("Expected input type to be 'complex', instead found {0}".format(type));

        if vlen != 1 :
            raise ImportError("Expected input vlen to be '1', instead found {0}".format(vlen));



    def loadOutputs(self, outputs):
        audioLeftFound = False;
        audioRightFound = False;
        outputNames = [];

        if len(outputs) < 2 :
            raise ImportError("There should be at least two sources");

        for output in outputs:
            name = output["label"];
            type = output["dtype"];
            vlen = output["vlen"];

            outputNames.append(name);

            if name == "audioLeft":
                audioLeftFound = True;
            elif name == "audioRight":
                audioRightFound = True;
            else:
                continue;

            if type != "float" :
                raise ImportError("Expected output type of {0} to be 'float', instead found {1}".format(name, type));

            if vlen != 1 :
                raise ImportError("Expected output vlen of {0} to be '1', instead found {1}".format(name, vlen));

        if not audioLeftFound or not audioRightFound :
            raise ImportError("Expected at least outputs named 'audioLeft' and 'audioRight', instead found {0}".format(", ".join(outputNames)));




    def loadModule(self):
        self.spec = importlib.util.spec_from_file_location("grModule." + self.id, self.pythonFile);
        self.module = importlib.util.module_from_spec(self.spec);
        self.spec.loader.exec_module(self.module);
        self.pluginClass = getattr(self.module, self.id);


    def createInstance(self): #optionally overwrite default parameters?
        return self.pluginClass(**self.parameters);

class PluginModel:
    def __init__(self):
        self.demodPluginList = {};

    def compilePlugins(self) :
        pluginPath = os.path.join(*GRC_PLUGIN_PATH);
        pluginFiles = filter(lambda x: x.endswith('.grc'), os.listdir(pluginPath));
        for file in pluginFiles:
            path = os.path.join(pluginPath, file);
            #os.path.getmtime(path);
            subprocess.call([GRC_COMPILER, path]);

    def loadPlugins(self) :
        pluginPath = os.path.expanduser(GRC_PYTHON_PATH);
        pluginFiles = filter(lambda x: x.endswith('.py'), os.listdir(pluginPath));
        for file in pluginFiles:
            plugin = DemodPlugin(file);
            try:
                plugin.load();
                self.demodPluginList[plugin.id] = plugin;
                print("loaded module {0}".format(plugin.id))
            except IOError as err:
                print("Failed to load file {0} as a demod module: {1}".format(file, err.strerror));

    def getDemodPlugins(self) :
        return self.demodPluginList;
