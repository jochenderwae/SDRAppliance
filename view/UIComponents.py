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

font_cache = {}
def get_font(size):
	"""Get font of the specified size.  Will cache fonts internally for faster
	repeated access to them.
	"""
	if size not in font_cache:
		font_cache[size] = pygame.font.Font(None, size)
	return font_cache[size]

def render_text(text, size=18, fg=( 255, 255, 255), bg=(19, 19, 30)):
	"""Render the provided text to a surface which is returned."""
	if bg is not None:
		# Optimized case when the background is known.
		return get_font(size).render(text, True, fg, bg)
	else:
		# Less optimized case with transparent background.
		return get_font(size).render(text, True, fg)

class UIComponent(object):
	def __init__(self) :
		self.dirty = True;
		self.rect = (0, 0, 0, 0);
		self.visible = True;
		self.preferredSize = (0, 0);

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
		pass;

class Button(UIComponent):
	# Default color and other button configuration.  Can override these values
	# to change all buttons.
	fg_color     = (255, 255, 255)
	#fg_color     = ( 60, 255, 255)
	bg_color     = (60, 60, 60)
	#bg_color     = ( 19,  19,  30)
	border_color = (200, 200, 200)
	#border_color = ( 19,  19,  30)
	padding_px   = 2
	border_px    = 2
	font_size    = 18

	def __init__(self, textOrIcon=None, click=None, font_size=None, bg_color=None):
		super().__init__();
		self.label = None;
		self.text = None;
		self.icon = None;

		if isinstance(textOrIcon, str) :
			self.text = textOrIcon;
			self.label = render_text(self.text, size=self.font_size, fg=self.fg_color, bg=self.bg_color)
		if isinstance(textOrIcon, pygame.Surface):
			self.icon = textOrIcon;
		#self.bg_color = bg_color if bg_color is not None else self.bg_color
		#self.font_size = font_size if font_size is not None else self.font_size
		#self.click_func = click
		# Determine rendered dimensions based on padding.
		#x, y, width, height = rect
		#x += self.padding_px
		#y += self.padding_px
		#width -= 2*self.padding_px
		#height -= 2*self.padding_px
		#self.rect = (x, y, width, height)
		# Draw label centered in the button for quick rendering later.

	def getPreferredSize(self) :
		w = h = 20;
		if self.label :
			x, y, w, h = self.label.get_rect();
		if self.icon :
			w, h = self.icon.get_size();
		return (w, h);

	def doRender(self, screen) :
		screen.fill(self.bg_color, self.rect)
		pygame.draw.rect(screen, self.border_color, self.rect, self.border_px)
		if self.label:
			self.label_pos = align(self.label.get_rect(), self.rect)
			screen.blit(self.label, self.label_pos)
		if self.icon:
			pos = align(self.icon.get_rect(), self.rect)
			screen.blit(self.icon, pos)

	def click(self, location):
		x, y, width, height = self.rect
		mx, my = location
		if mx >= x and mx <= (x + width) and my >= y and my <= (y + height) \
			and self.click_func is not None:
			self.click_func(self)

class Spinner(UIComponent):
	def __init__(self, value) :
		super().__init__();
		self.bg_color     = (0, 0, 0)

	def getPreferredSize(self) :
		w = 20;
		h = 40;
		return (w, h);

	def doRender(self, screen) :
		screen.fill(self.bg_color, self.rect)
		pygame.draw.rect(screen, (0, 128, 0), self.rect, 1)

class Slider(UIComponent):
	def __init__(self, label, min=0, max=100) :
		super().__init__();
		self.label = label;
		self.min = min;
		self.max = max;
		self.bg_color     = (0, 0, 0)

	def getPreferredSize(self) :
		w = 20;
		h = 100;
		return (w, h);

	def doRender(self, screen) :
		screen.fill(self.bg_color, self.rect)
		pygame.draw.rect(screen, (0, 0, 128), self.rect, 1)

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

class ButtonGrid(object):
	def __init__(self, width, height, cols, rows):
		self.col_size = width / cols
		self.row_size = height / rows
		self.buttons = []

	def add(self, col, row, text, rowspan=1, colspan=1, **kwargs):
		x = col*self.col_size
		y = row*self.row_size
		width = colspan*self.col_size
		height = rowspan*self.row_size
		self.buttons.append(Button((x,y,width,height), text, **kwargs))

	def render(self, screen):
		"""Render buttons on the provided surface."""
		# Render buttons.
		for button in self.buttons:
			button.render(screen)

	def click(self, location):
		"""Handle click events at the provided location tuple (x, y) for all the
		buttons.
		"""
		for button in self.buttons:
			button.click(location)
