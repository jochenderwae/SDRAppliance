
from view.UIComponents import UIComponent

class SpectrumPanel(UIComponent):
    def __init__(self, model) :
        super().__init__();
        self.model = model;

    def getPreferredSize(self) :
        return (400, 100);

class BandPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;

    def getPreferredSize(self) :
        return (400, 50);

class WaterfallPanel(UIComponent) :
    def __init__(self, model) :
        super().__init__();
        self.model = model;

    def getPreferredSize(self) :
        return (400, 200);
