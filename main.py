#!/bin/python3

from model.Model import *;
from controller.Controller import *;
from view.MainView import *;

class Application:
    def __init__(self):
        self.model = Model();
        self.controller = Controller();
        self.mainView = MainView();

    def start(self):
        self.controller.setModel(self.model);
        self.mainView.setController(self.controller);

        self.model.start();
        self.controller.start();
        self.mainView.start();

        # mainView.start() is blocking. When it ends, the application can stop

        self.mainView.stop();
        self.controller.stop();
        self.model.stop();


def main():
    application = Application();
    application.start();


if __name__ == '__main__':
    main();
