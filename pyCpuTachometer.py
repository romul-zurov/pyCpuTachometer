#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
TODO:
- paintEvent: delete link to .png files?
- thread?
- popUp menu!
- change size on double click - OK
'''


import sys, math
from PyQt4 import QtCore, QtGui
import psutil


INTERVAL = 100
MAX_ANGLE = 252.0
TACHO_BUF_SIZE = 30 * 100 / INTERVAL
GAZ_BUF_SIZE = 10


class Display(QtGui.QLabel):
    def __init__(self, parent = None):
        self.main_size = 192
        QtGui.QLabel.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | 
                            QtCore.Qt.WindowStaysOnTopHint)
        
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
#        self.painter = QtGui.QPainter(self)
    
    
    
    
    def set_path(self):
        self.tacho_path = 'tacho02.' + str(self.main_size) + '.png'
        self.arrow_path = 'arrow02.' + str(self.main_size) + '.png'
    
    def set_main_size(self):
        self.set_path()
        self.cx_tacho = self.main_size / 2
        self.cy_tacho = self.main_size / 2
        self.setFixedSize(self.main_size, self.main_size)
    
    def reset_main_size(self):
        self.main_size = (self.main_size - 64)
        if self.main_size < 64:
            self.main_size = 256
        self.set_main_size()
    
    def zabivka(self, size, val):
        ss = []
        for x in range(size):
            ss.append(val)
        return ss
    
    def draw_arrow(self, cx, cy, angle, sc, path):
        self.painter.translate(cx, cy)
        self.painter.rotate(angle)
        self.painter.scale(sc, sc)
        self.painter.translate(-cx, -cy)
        self.painter.drawPixmap(0, 0, QtGui.QPixmap(path))
    
    def old_draw_gaz(self, painter):
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setColor(QtGui.QColor.fromHsv(100 - self.gaz, 255, 255, 255))
        painter.setPen(pen)
        bru = QtGui.QBrush()
        bru.setStyle(QtCore.Qt.SolidPattern)
        bru.setColor(QtGui.QColor.fromHsv(100 - self.gaz, 255, 255, 255))
        painter.setBrush(bru)
        kr = 3
        gaz_rect = QtCore.QRect(self.main_size / 2 - (self.main_size / (kr * 2)),
                                self.main_size / 2 - (self.main_size / (kr * 2)),
                                self.main_size / kr , self.main_size / kr)
        gaz_start_angle = -16 * 90
        painter.drawPie(gaz_rect, gaz_start_angle, self.gaz_angle)
        pass
    
    def draw_tacho(self):
        self.draw_arrow(self.cx_tacho, self.cy_tacho, self.tacho_angle,
                        1.0, self.arrow_path)
    
    def draw_gaz(self):
        self.draw_arrow(self.cx_tacho, self.cy_tacho, self.gaz_angle,
                        0.64, self.arrow_path)
    
    def paintEvent(self, eve):
        self.painter = QtGui.QPainter(self)
#        painter = QtGui.QPainter(self)
        fon = QtGui.QPixmap(self.tacho_path)
        self.setMask(fon.mask())
        self.painter.drawPixmap(0, 0, QtGui.QPixmap(self.tacho_path))
        
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
        d = 4;    aa = int(round(self.gaz, 0)) / d;    aa *= d
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
    
    def mouseReleaseEvent(self, event):
        if (event.button() == QtCore.Qt.LeftButton):
            self.drag_flag = False
    
    def mouseDoubleClickEvent (self, event):
        if (event.button() == QtCore.Qt.LeftButton):
            self.reset_main_size()


if __name__ == '__main__':
    print "Hi!"
    
    app = QtGui.QApplication(sys.argv)
    win = Display()
    win.show()
    sys.exit(app.exec_())

