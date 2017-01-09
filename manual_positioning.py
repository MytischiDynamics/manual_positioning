from main_window import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFrame, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QDrag, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QDataStream, QIODevice, QPoint, QByteArray, QMimeData

class DragWidget(QFrame) :
    def __init__(self, parent = None) :
        super(DragWidget, self).__init__(parent)

        self.ControlPoints = []
        self.NumberOfControlPoints = 2

        self.setMinimumSize(600, 600)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.setAcceptDrops(True)

        self.BackgroundPic = QLabel(self)
        self.BackgroundPic.setPixmap(QPixmap('./BackDefault.png'))
        self.BackgroundPic.show()

        control_points_counter = 0
        while control_points_counter < 2 :
            self.ControlPoints.append(QLabel(self))
            self.ControlPoints[-1].setPixmap(QPixmap('./cross1.png'))
            self.ControlPoints[-1].move(10 + control_points_counter * 10, 10 + control_points_counter * 10)
            self.ControlPoints[-1].show()
            self.ControlPoints[-1].setAttribute(Qt.WA_DeleteOnClose)
            control_points_counter += 1

    def redrawGraph(self, event):
        pix = QPixmap("./BackDefault.png")
        qp = QPainter(pix)
        qp.begin(self)
        pen = QPen(Qt.black, 1, Qt.DashLine)
        qp.setPen(pen)
        if self.number_of_draggable == 1 :
            qp.drawLine(self.ControlPoints[0].pos(), event.pos())
        else :
            qp.drawLine(self.ControlPoints[1].pos(), event.pos())
        qp.end()
        self.BackgroundPic.setPixmap(pix)

    def SetBackground(self, filename) :
        self.BackgroundPic.setPixmap(QPixmap(filename))

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                self.redrawGraph(event)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if not child:
            return

        if child == self.BackgroundPic:
            return
        if child == self.ControlPoints[0]:
            self.number_of_draggable = 0
        else:
            self.number_of_draggable = 1
        child.move(event.pos())
        pixmap = QPixmap(child.pixmap())

        itemData = QByteArray()
        dataStream = QDataStream(itemData, QIODevice.WriteOnly)
        dataStream << pixmap << QPoint(event.pos() - child.pos())

        mimeData = QMimeData()
        mimeData.setData('application/x-dnditemdata', itemData)

        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - child.pos())

        tempPixmap = QPixmap(pixmap)
        painter = QPainter()
        painter.begin(tempPixmap)
        painter.fillRect(pixmap.rect(), QColor(127, 127, 127, 127))
        painter.end()

        child.setPixmap(tempPixmap)

        if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
            child.close()
        else:
            child.show()
            child.setPixmap(pixmap)

#    dragMoveEvent = dragEnterEvent

    def dropEvent(self, event):
        if event.mimeData().hasFormat('application/x-dnditemdata'):
            itemData = event.mimeData().data('application/x-dnditemdata')
            dataStream = QDataStream(itemData, QIODevice.ReadOnly)

            pixmap = QPixmap()
            offset = QPoint()
            dataStream >> pixmap >> offset

            newIcon = QLabel(self)
            newIcon.setPixmap(pixmap)
            newIcon.move(event.pos() - offset)
            newIcon.show()
            newIcon.setAttribute(Qt.WA_DeleteOnClose)
            self.ControlPoints[self.number_of_draggable] = newIcon

            if event.source() == self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    ui.actionSelect_Folder.triggered.connect(selectFolder)
    ui.VerticalLayout_Image.addWidget(DragWidget())

    window.show()

    sys.exit(app.exec_())