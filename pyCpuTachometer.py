# -*- coding: utf-8 -*-

'''
TODO:
- привязку paintEvevn к файлам-картинкам убрать
- thread!
'''


import sys, math
from PyQt4 import QtCore, QtGui
import psutil


TACHO_PATH = 'tacho01.png'
ARROW_PATH = 'arrow01.png'
INTERVAL = 100
MAX_ANGLE = 252.0
TACHO_BUF_SIZE = 30 * 100 / INTERVAL
GAZ_BUF_SIZE = 10


class Display(QtGui.QLabel):
    def __init__(self, parent = None):
        self.k_naklona = 0.8
        self.k_scale = 1.0
        QtGui.QLabel.__init__(self, parent)
#        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | 
                            QtCore.Qt.WindowStaysOnTopHint)
        
        self.pixmap = QtGui.QPixmap(TACHO_PATH)
        self.setFixedSize(self.pixmap.width() * self.k_scale,
                          self.pixmap.height() * self.k_scale * self.k_naklona)
        self.timer = QtCore.QTimer(self)
        self.timer.start(INTERVAL)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.foo)
        self.tacho_angle = self.gaz_angle = 0.0
        self.tacho = self.gaz = 0.0
        self.tacho_arr = self.zabivka(TACHO_BUF_SIZE, 10.0)
        self.gaz_arr = self.zabivka(GAZ_BUF_SIZE, 0.0)
        self.cx_tacho = self.pixmap.width() / 2
        self.cy_tacho = self.pixmap.height() / 2
        self.drag_flag = False
        
        
    
    def zabivka(self, size, val):
        ss = []
        for x in range(size): 
            ss.append(val)
        return ss
    
    def draw_arrow(self, painter, cx, cy, angle, dx, dy, path):
        painter.translate(cx, cy)
        painter.rotate(angle)
        painter.translate(-cx, -cy)
        painter.drawPixmap(dx, dy, QtGui.QPixmap(path))
    
    def paintEvent(self, eve):
        painter = QtGui.QPainter(self)
        painter.scale(self.k_scale, self.k_scale * self.k_naklona)
        
#        painter.translate(self.cx_tacho, self.cy_tacho)
        painter.drawPixmap(0, 0, QtGui.QPixmap(TACHO_PATH))
        
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setCapStyle(0x20)
        pen.setColor(QtGui.QColor.fromHsv(100 - self.gaz, 255, 255, 255))
        painter.setPen(pen)
        gaz_rect = QtCore.QRect(45, 194 - (45 + 104), 104, 104)
        gaz_start_angle = -16 * 148
        painter.drawArc(gaz_rect, gaz_start_angle, self.gaz_angle)
        
        self.draw_arrow(painter, self.cx_tacho, self.cy_tacho, self.tacho_angle, 0, 0, ARROW_PATH)
        painter.resetTransform()
        painter.end()
    
    
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
        self.gaz_arr, self.gaz = self.usred(self.gaz_arr, perc)
        d = 4;    aa = int(round(self.gaz, 0)) / d;    aa *= d
        self.gaz = aa
        self.tacho_arr, self.tacho = self.usred(self.tacho_arr, self.gaz)
        
        self.tacho_angle = (MAX_ANGLE / 100.0) * self.tacho
        self.gaz_angle = -16 * (MAX_ANGLE / 100.0) * self.gaz
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



if __name__ == '__main__':
    print "Hi!"
    
    app = QtGui.QApplication(sys.argv)
    win = Display()
    win.show()
    sys.exit(app.exec_())
    
