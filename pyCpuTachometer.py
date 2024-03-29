#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
TODO:
- use svg instead png?
- thread?
- paintEvent: delete link to .png files? - OK
- popUp menu - OK
- change size on double click - OK
- not in a taskbar, in all desktops - OK
- hide to tray - OK
'''


import os, sys, math
from PyQt4 import QtCore, QtGui
import psutil


VERSION = "0.6.1"
INTERVAL = 100
MAX_ANGLE = 252.0
TACHO_BUF_SIZE = 30 * 100 / INTERVAL
GAZ_BUF_SIZE = 10


class Display(QtGui.QLabel):
	def __init__(self, parent = None):
		self.main_size = 128
		QtGui.QLabel.__init__(self, parent)
		
		self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | 
							QtCore.Qt.WindowStaysOnTopHint | 
							QtCore.Qt.X11BypassWindowManagerHint)   
		
		self.maska_flag = False
		self.set_path()
		self.pixmap = QtGui.QPixmap(self.tacho_path)
		self.set_main_size()
		self.timer = QtCore.QTimer(self)
		self.timer.start(INTERVAL)
		self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.foo)
		self.tacho_angle = self.gaz_angle = self.mem_angle = 0.0
		self.tacho = self.gaz = 0.0
		self.tacho_arr = self.zabivka(TACHO_BUF_SIZE, 10.0)
		self.gaz_arr = self.zabivka(GAZ_BUF_SIZE, 0.0)
		self.drag_flag = False
		self.MEM = psutil.TOTAL_PHYMEM
		self.set_menu()
	
	
	def set_menu(self):
		self.pop_menu = QtGui.QMenu(self)
		self.hide_action = self.pop_menu.addAction("Hide/Show")
		self.connect(self.hide_action, QtCore.SIGNAL("triggered()"), self.hide_or_show)
		self.quit_action = self.pop_menu.addAction("Quit")
		self.connect(self.quit_action, QtCore.SIGNAL("triggered()"), self.close)
		self.about_action = self.pop_menu.addAction("About..")
		self.connect(self.about_action, QtCore.SIGNAL("triggered()"), self.about)
		self.tray_icon = QtGui.QSystemTrayIcon(QtGui.QIcon(self.tacho_path), self)
		self.tray_icon.show()
		self.tray_icon.setContextMenu(self.pop_menu)
		
		self.tray_icon.activated.connect(self.hide_on_left_click)
	
	def hide_or_show(self):
		if self.isHidden():
			self.show()
		else:
			self.hide()
	
	def hide_on_left_click(self, value):
		if (value == QtGui.QSystemTrayIcon.Trigger):
			self.hide_or_show()
		pass
	
	def set_path(self):
		self.tacho_path = 'tacho02.' + str(self.main_size) + '.png'
		self.arrow_path = 'arrow02.' + str(self.main_size) + '.png'
		if self.maska_flag:
			self.maska_path = 'maska.' + str(self.main_size) + '.png'
		else:
			self.maska_path = self.tacho_path
		
		self.tacho_pixmap = QtGui.QPixmap(self.tacho_path)
		self.arrow_pixmap = QtGui.QPixmap(self.arrow_path)
		self.maska_pixmap = QtGui.QPixmap(self.maska_path)
		pass
	
	
	def set_main_size(self):
		self.set_path()
		self.cx_tacho = self.main_size / 2
		self.cy_tacho = self.main_size / 2
		self.setFixedSize(self.main_size, self.main_size)
	
	def about(self):
		msg_box = QtGui.QMessageBox()
		msg_box.setText("pyCpuTachometer v. " + VERSION)
		msg_box.exec_()
		pass
	
	def reset_main_size(self):
		if self.main_size <= 32 : self.main_size = 256
		elif self.main_size > 128 : self.main_size -= 64
		else: self.main_size -= 32
		self.set_main_size()
	
	def zabivka(self, size, val):
		ss = []
		for x in range(size):
			ss.append(val)
		return ss
	
	def draw_arrow(self, cx, cy, angle, sc, pixmap):
		self.painter.translate(cx, cy)
		self.painter.rotate(angle)
		self.painter.scale(sc, sc)
		self.painter.translate(-cx, -cy)
		self.painter.drawPixmap(0, 0, pixmap)
	
	def draw_tacho(self):
		self.draw_arrow(self.cx_tacho, self.cy_tacho, self.tacho_angle,
						1.0, self.arrow_pixmap)
	
	def draw_gaz(self):
		self.draw_arrow(self.cx_tacho, self.cy_tacho, self.gaz_angle,
						0.64, self.arrow_pixmap)
	
	def paintEvent(self, eve):
		self.painter = QtGui.QPainter(self)
		self.setMask(self.maska_pixmap.mask())
		self.painter.drawPixmap(0, 0, self.tacho_pixmap)
		
		self.draw_tacho()
		self.painter.resetTransform()
		self.draw_gaz()
		
		self.painter.resetTransform()
		self.painter.end()
	
	
	def usred(self, ss, v):
		del ss[0]
		ss.append(v)
		a = 0.0
		for x in ss:
			a += x
		res = a / len(ss)
		return ss, res
	
	def foo(self):
		perc = psutil.cpu_percent(interval = None, percpu = False)
		mem = psutil.avail_phymem()
		self.gaz_arr, self.gaz = self.usred(self.gaz_arr, perc)
		d = 4;	aa = int(round(self.gaz, 0)) / d;	aa *= d
		self.gaz = aa
		self.tacho_arr, self.tacho = self.usred(self.tacho_arr, self.gaz)
		
		self.tacho_angle = (MAX_ANGLE / 100.0) * self.tacho
		self.gaz_angle = (MAX_ANGLE / 100.0) * self.gaz
		self.mem_angle = MAX_ANGLE * (1.0 * mem / self.MEM)
		self.update()
		pass
	
	def move_tacho(self, eve):
		self.move(eve.globalX() - self.point.x(), eve.globalY() - self.point.y())
		pass
	
	def mouseMoveEvent(self, event):
		if self.drag_flag:
			self.move_tacho(event)
	
	def mousePressEvent(self, event):
		if (event.button() == QtCore.Qt.LeftButton):
			self.drag_flag = True
			self.point = event.pos()
		elif (event.button() == QtCore.Qt.MiddleButton):
			self.maska_flag = not self.maska_flag
			self.set_path()
#			res = os.popen('top -n 1 -b')
#			for x in res.readlines():
#				print x
		elif (event.button() == QtCore.Qt.RightButton):
			self.pop_menu.popup(QtGui.QCursor.pos(), self.quit_action)
	
	def mouseReleaseEvent(self, event):
		if (event.button() == QtCore.Qt.LeftButton):
			self.drag_flag = False
	
	def mouseDoubleClickEvent (self, event):
		if (event.button() == QtCore.Qt.LeftButton):
			self.reset_main_size()
	


if __name__ == '__main__':
#if True:
	print VERSION
	app = QtGui.QApplication(sys.argv)
	win = Display()
	win.show()
	sys.exit(app.exec_())
