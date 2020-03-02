


class Styling :
    def __init__(self, style) :
        self.style = style;

    def getStyle(self, component, key) :
        componentClass = type(component).__name__;
        componentId = component.getId();
        keys = ["{}.{}.{}".format(key, componentClass, componentId),
            "{}.{}".format(key, componentId),
            "{}.{}".format(key, componentClass),
            key];

        for key in keys :
            try :
                value = self.style[key];
                return value;
            except KeyError:
                pass;
        return None;


style = Styling({
	"background.color": (0, 0, 0), # black background
	"foreground.color": (255, 255, 255), # white text
	"border.color":     None,
	"border.size":      None,

	"border.color.Button": (128, 128, 128),
	"border.size.Button":  1,

    "line.color.SpectrumPanel":   (150, 255, 255),
	"border.color.SpectrumPanel": (128, 128, 128),
	"border.size.SpectrumPanel":  1,

	"padding":          (5, 5, 5, 5),
});
