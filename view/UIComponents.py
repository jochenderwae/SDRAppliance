# FreqShow user interface classes.
# Author: Tony DiCola (tony@tonydicola.com)
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# Enhancements over the original freqshow by Dan Stixrud, WQ7T
import pygame
import time
import math
from view.Styling import style



# Alignment constants.
ALIGN_LEFT   = 0.0
ALIGN_TOP    = 0.0
ALIGN_CENTER = 0.5
ALIGN_RIGHT  = 1.0
ALIGN_BOTTOM = 1.0


def align(child, parent, horizontal=ALIGN_CENTER, vertical=ALIGN_CENTER,
	hpad=0, vpad=0):
	"""Return tuple of x, y coordinates to render the provided child rect
	aligned inside the parent rect using the provided horizontal and vertical
	alignment.  Each alignment value can be ALIGN_LEFT, ALIGNT_TOP, ALIGN_CENTER,
	ALIGN_RIGHT, or ALIGN_BOTTOM.  Can also specify optional horizontal padding
	(hpad) and vertical padding (vpad).
	"""
	cx, cy, cwidth, cheight = child
	px, py, pwidth, pheight = parent
	return (px+(horizontal*pwidth-horizontal*cwidth)+hpad,
			py+(vertical*pheight-vertical*cheight)+vpad)

def render_text(text, font=None, fg=( 255, 255, 255), bg=(19, 19, 30)):
	"""Render the provided text to a surface which is returned."""
	if bg is not None:
		# Optimized case when the background is known.
		return font.render(text, True, fg, bg)
	else:
		# Less optimized case with transparent background.
		return font.render(text, True, fg)

class UIComponent(object):
	idCounter = 0;

	def __init__(self, id=None) :
		self.dirty = True;
		self.rect = (0, 0, 0, 0);
		self.visible = True;
		self.preferredSize = (0, 0);
		if id :
			self.id = id;
		else :
			self.id = "UIComponent_{}".format(UIComponent.idCounter);
			UIComponent.idCounter += 1;
		self.foregroundColor = style.getStyle(self, "foreground.color");
		self.backgroundColor = style.getStyle(self, "background.color");
		self.hover = False;

	def getId(self) :
		return self.id;

	def setRect(self, rect) :
		if self.rect != rect:
			self.invalidate();
			self.rect = rect;

	def getRect(self) :
		return self.rect;

	def setVisible(self, visible) :
		self.visible = visible;

	def isVisible(self) :
		return self.visible;

	def invalidate(self) :
		self.dirty = True;

	def setPreferredSize(self, preferredSize) :
		self.preferredSize = preferredSize;

	def getPreferredSize(self) :
		return self.preferredSize;

	def render(self, screen) :
		if self.dirty and self.visible :
			self.doRender(screen);
			self.dirty = False;

	def doRender(self, screen) :
		screen.fill(self.backgroundColor, self.rect);

		borderColor = style.getStyle(self, "border.color");
		borderSize  = style.getStyle(self, "border.size");
		if borderColor and borderSize :
			pygame.draw.rect(screen, borderColor, self.rect, borderSize);

	def handleMouseEvent(self, event) :
		mouseX, mouseY = event.dict['pos'];
		x, y, w, h = self.getRect();
		if x <= mouseX < x + w and y <= mouseY <= y + h :
			self.doHandleMouseEvent(event);
			self.setHover(True);
		else :
			self.setHover(False);

	def setHover(self, hover) :
		if hover != self.hover :
			self.invalidate();
		self.hover = hover;

	def doHandleMouseEvent(self, event) :
		pass;

	def renderText(self, screen, text, pos=None, color=None, font=None):
		label = self.buildLabel(text, color, font);
		if pos :
			x, y = pos;
		else :
			x, y, w, h = self.getRect();
		screen.blit(label, (x, y));

	def buildLabel(self, text, color=None, font=None):
		if not font :
			font = style.getFont(self, "font");
		if not color :
			color = self.foregroundColor;
		if self.backgroundColor is not None:
			return font.render(text, True, color, self.backgroundColor);
		else:
			return font.render(text, True, color);

	def renderBorder(self, screen):
		pass;

class Button(UIComponent):
	CLICK_DEBOUNCE = 0.04

	def __init__(self, textOrIcon=None):
		super().__init__();
		self.label = None;
		self.text = None;
		self.icon = None;
		self.clickEvents = [];
		self.mouseDownTime = 0;

		if isinstance(textOrIcon, str) :
			self.text = textOrIcon;
			self.label = render_text(self.text, font=style.getFont(self, "font"), fg=style.getStyle(self, "foreground.color"), bg=style.getStyle(self, "background.color"));
		if isinstance(textOrIcon, pygame.Surface):
			self.icon = textOrIcon;

	def addClickEvent(self, event) :
		self.clickEvents.append(event);

	def doHandleMouseEvent(self, event) :
		if event.type == pygame.MOUSEBUTTONDOWN :
			if time.time() - self.mouseDownTime > Button.CLICK_DEBOUNCE :
				self.mouseDownTime = time.time();
				for handler in self.clickEvents :
					handler(self);

	def getPreferredSize(self) :
		w = h = 20;
		if self.label :
			x, y, w, h = self.label.get_rect();
		if self.icon :
			w, h = self.icon.get_size();
		size = max(w, h);
		return (size, size);

	def doRender(self, screen) :
		super().doRender(screen);
		if self.label:
			self.label_pos = align(self.label.get_rect(), self.rect)
			screen.blit(self.label, self.label_pos)
		if self.icon:
			pos = align(self.icon.get_rect(), self.rect)
			screen.blit(self.icon, pos)

class Spinner(UIComponent):
	def __init__(self, value) :
		super().__init__();
		self.value = None;
		self.digits = 1;
		self.min = 0;
		self.max = 9;
		self.buttonEdge = 20;
		self.upIcon = style.getIcon(self, "icon.up");
		self.downIcon = style.getIcon(self, "icon.down");
		self.textColor = style.getStyle(self, "foreground.color");
		self.placeholderTextColor = style.getStyle(self, "placeholder.color");
		self.focus = False;
		self.mouseDownTime = 0;
		self.updateHandlers = [];

	def setValue(self, value) :
		if value != self.value :
			self.invalidate();
		self.value = value;

	def setRect(self, rect) :
		super().setRect(rect);
		x, y, w, h = rect;
		self.buttonEdge = int(y + h / 2);

	def getPreferredSize(self) :
		w = 20;
		h = 40;
		return (w, h);

	def addUpdateHandler(self, updateHandler) :
		self.updateHandlers.append(updateHandler);

	def doRender(self, screen) :
		super().doRender(screen);
		if self.value is not None :
			self.renderText(screen, "{:1d}".format(self.value%10));
		else :
			self.renderText(screen, "0", color=self.placeholderTextColor);
		if self.hover :
			x, y, w, h = self.getRect();

			ax, ay = align(self.upIcon.get_rect(), self.rect);
			ay = y;
			screen.blit(self.upIcon, (ax, ay));

			ix, iy, iw, ih = self.downIcon.get_rect();
			ax, ay = align(self.downIcon.get_rect(), self.rect);
			ay = y + h - ih;
			screen.blit(self.downIcon, (ax, ay));


	def doHandleMouseEvent(self, event) :
		mouseX, mouseY = event.dict['pos'];
		if event.type == pygame.MOUSEBUTTONDOWN :
			if time.time() - self.mouseDownTime > Button.CLICK_DEBOUNCE :
				self.mouseDownTime = time.time();
				if mouseY < self.buttonEdge :
					self.updateValue(True);
				else :
					self.updateValue(False);


	def updateValue(self, up) :
		oldValue = self.value;
		if up :
			if self.value :
				self.value = self.value + 1;
				self.triggerValueUpdated(oldValue);
				self.invalidate();
			else:
				self.value = 1;
				self.triggerValueUpdated(oldValue);
				self.invalidate();
		else :
			if self.value is not None :
				self.value = self.value - 1;
				self.triggerValueUpdated(oldValue);
				self.invalidate();

	def triggerValueUpdated(self, oldValue):
		for handler in self.updateHandlers :
			handler(self, oldValue, self.value);

class SpinnerGroup :
	def __init__(self) :
		self.spinners = [];
		self.value = 0;
		self.updateHandlers = [];

	def setValue(self, value) :
		self.value = value;
		index = len(self.spinners);
		leadingZeros = True;
		for spinner in self.spinners:
			index -= 1;
			digit = int(math.floor(self.value / (10 ** index))) % 10;
			if digit > 0 :
				leadingZeros = False;
			if leadingZeros :
				spinner.setValue(None);
			else :
				spinner.setValue(digit);

	def add(self, spinner) :
		self.spinners.append(spinner);
		spinner.addUpdateHandler(self.childUpdateHandler);

	def childUpdateHandler(self, spinner, oldValue, newValue) :
		if oldValue is None :
			oldValue = 0;
		if newValue is None :
			newValue = 0;
		index = self.spinners.index(spinner);
		difference = newValue - oldValue;
		index = len(self.spinners) - index - 1;
		scale = (10**index);
		increment = scale * difference;
		if self.value + increment < scale :
			increment = scale * difference / 10;
		self.setValue(self.value + increment);
		self.triggerValueUpdated();

	def addUpdateHandler(self, updateHandler) :
		self.updateHandlers.append(updateHandler);

	def triggerValueUpdated(self):
		for handler in self.updateHandlers :
			handler(self, self.value);



class Slider(UIComponent):
	def __init__(self, label, min=0, max=100) :
		super().__init__();
		self.label = label;
		self.min = min;
		self.max = max;

	def getPreferredSize(self) :
		w = 20;
		h = 100;
		return (w, h);

	def doRender(self, screen) :
		super().doRender(screen);

class Panel(UIComponent):
	def __init__(self, layoutManager = None) :
		super().__init__();
		self.children = {};
		self.layoutManager = layoutManager;
		self.layoutDirty = True;

	def add(self, uiElement, layoutArgument=None) :
		self.children[uiElement] = layoutArgument;
		self.layoutDirty = True;

	def getPreferredSize(self) :
		return self.layoutManager.getPreferredSize(self, self.children);

	def render(self, screen) :
		if self.layoutDirty :
			if self.layoutManager :
				self.layoutManager.apply(self, self.children);
			self.layoutDirty = False;
			self.invalidate();
		super().render(screen);
		for child in self.children.keys() :
			child.render(screen);

	def doHandleMouseEvent(self, event) :
		for child in self.children.keys() :
			child.handleMouseEvent(event);

	def invalidate(self) :
		super().invalidate();
		for child in self.children.keys() :
			child.invalidate();

	def setHover(self, hover) :
		super().setHover(hover);
		if not hover :
			for child in self.children.keys() :
				child.setHover(False);


class ButtonGrid(object):
	def __init__(self, width, height, cols, rows):
		pass;

	def click(self, location):
		"""Handle click events at the provided location tuple (x, y) for all the
		buttons.
		"""
		for button in self.buttons:
			button.click(location)
