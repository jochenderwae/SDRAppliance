

import math
from view.UIComponents import UIComponent


class LayoutManager :
    def apply(self, container, children) :
        pass;

class BorderLayout(LayoutManager) :
    TOP = "BorderLayout_TOP";
    BOTTOM = "BorderLayout_BOTTOM";
    LEFT = "BorderLayout_LEFT";
    RIGHT = "BorderLayout_RIGHT";
    CENTER = "BorderLayout_CENTER";

    def __init__(self) :
        pass;

    def apply(self, container, children) :
        ctrx, ctry, ctrw, ctrh = container.getRect();
        top = ctry;
        bottom = ctry + ctrh;
        left = ctrx;
        right = ctrx + ctrw;

        for component, param in children.items() :
            width, height = component.getPreferredSize();
            if param == BorderLayout.LEFT :
                left = ctrx + width;
            if param == BorderLayout.RIGHT :
                right = ctrx + ctrw - width;
            if param == BorderLayout.TOP :
                top = ctry + height;
            if param == BorderLayout.BOTTOM :
                bottom = ctry + ctrh - height;

        for component, param in children.items() :
            if param == None or param == BorderLayout.CENTER :
                component.setRect((left, top, right - left, bottom - top));
            if param == BorderLayout.LEFT :
                component.setRect((ctrx, top, left - ctrx, bottom - top));
            if param == BorderLayout.RIGHT :
                component.setRect((right, top, ctrx + ctrw - right, bottom - top));
            if param == BorderLayout.TOP :
                component.setRect((ctrx, ctry, ctrw, top - ctry));
            if param == BorderLayout.BOTTOM :
                component.setRect((ctrx, bottom, ctrw, ctry + ctrh - bottom));
            print(param, container.getRect(), component.getRect());

    def getPreferredSize(self, container, children) :
        leftWidth = 0;
        centerWidth = 0;
        rightWidth = 0;
        topHeight = 0;
        centerHeight = 0;
        bottomHeight = 0;

        for component, param in children.items() :
            width, height = component.getPreferredSize();
            if param == None or param == BorderLayout.CENTER :
                centerWidth = width;
                centerHeight = height;
            if param == BorderLayout.LEFT :
                leftWidth = width;
            if param == BorderLayout.RIGHT :
                rightWidth = width;
            if param == BorderLayout.TOP :
                topHeight = height;
            if param == BorderLayout.BOTTOM :
                bottomHeight = height;
        return (leftWidth + centerWidth + rightWidth, topHeight + centerHeight + bottomHeight);


class GridLayout(LayoutManager) :
    def __init__(self, cols=None, rows=None) :
        self.cols = cols;
        self.rows = rows;

        if not self.cols and not self.rows :
            self.cols = 2;

    def apply(self, container, children) :
        children = list(children.keys());
        itemCount = len(children);
        cols = self.cols;
        rows = self.rows;

        if cols :
            if rows :
                if itemCount > cols * rows :
                    itemCount = cols * rows;
            else :
                rows = math.ceil(itemCount / cols);
        else :
            cols = math.ceil(itemCount / rows);

        ctrx, ctry, ctrw, ctrh = container.getRect();

        componentWith = math.floor(ctrw / cols);
        componentHeight = math.floor(ctrh / rows);

        i = 0;
        componentX = 0;
        componentY = 0;

        print(rows, componentWith, cols, componentHeight, ctrw, ctrh);
        for row in range(rows) :
            for col in range(cols) :
                if i >= itemCount :
                    break;
                component = children[i];
                if col == cols - 1 :
                    width = ctrw - componentWith * col;
                else :
                    width = componentWith;
                if row == rows - 1 :
                    height = ctrh - componentHeight * row;
                else :
                    height = componentHeight;
                component.setRect((ctrx + col * componentWith, ctry + row * componentHeight, width, height));
                print((col * componentWith, row * componentHeight, width, height));
                i += 1;

    def getPreferredSize(self, container, children) :
        maxWidth = 0;
        maxHeight = 0;
        children = list(children.keys());
        for component in children :
            width, height = component.getPreferredSize();
            maxWidth = max(maxWidth, width);
            maxHeight = max(maxHeight, height);

        itemCount = len(children);
        cols = self.cols;
        rows = self.rows;

        if cols :
            if rows :
                if itemCount > cols * rows :
                    itemCount = cols * rows;
            else :
                rows = math.ceil(itemCount / cols);
        else :
            cols = math.ceil(itemCount / rows);

        print("preferred", maxWidth, cols, maxHeight, rows, itemCount);
        return (maxWidth * cols, maxHeight * rows);
