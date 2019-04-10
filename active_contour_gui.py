from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
import cv2
from PIL import Image
import numpy as np
from PIL import ImageQt
from algorithm_active_contur import ActiveContour
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        # self.setMouseTracking(True)

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        self.createParameterGroupBox()
        # self.createCanvasBox_2()

        topLayout = QHBoxLayout()
        self.input_img_groupbox = self.create_input_image_groupbox()
        self.output_img_groupbox = self.create_ouput_image_groupbox()
        self.parameterGroupBox.setFixedWidth(400)
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.parameterGroupBox, 0, 0)
        mainLayout.addWidget(self.input_img_groupbox, 0, 1)
        mainLayout.addWidget(self.output_img_groupbox, 0, 2)

        # mainLayout.addWidget(self.canvasGroupBox_2, 1, 2)

        self.setLayout(mainLayout)

        self.setWindowTitle("Active Contour")
        self.changeStyle('Fusion')
        self.connect_signals()
        self.init_variables()

    def init_variables(self):
        self.current_img = None
        self.current_img_path = None
        self.start_x = 0
        self.end_x = 0
        self.start_y = 0
        self.end_y = 0

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def connect_signals(self):
        self.openfile_dialog_btn.clicked.connect(self.openfile_dialog)

    def createParameterGroupBox(self):

        self.process_image_btn = QPushButton("Process Image")

        self.parameterGroupBox = QGroupBox("Parameters")

        self.openfile_dialog_btn = QPushButton('Open Image')


        alpha_spinbox_label = QLabel('Higher value, snake contract faster')
        beta_spinbox_label = QLabel('Higher values makes snake smoother')
        w_line_spinbox_label = QLabel('Negative values to attract to dark regions.')
        w_edge_spinbox_label = QLabel('Use negative values to repel snake from edges.')
        gamma_label = QLabel('Explicit time stepping parameter')
        boundary_label = QLabel('Boundary conditions for worm')
        max_px_move_label = QLabel('Maximum iterations to optimize snake shape')
        convergence_label = QLabel('Convergence criteria.')
        self.alpha_spinbox = QDoubleSpinBox()
        self.alpha_spinbox.setValue(0.01)
        self.beta_spinbox = QDoubleSpinBox()
        self.beta_spinbox.setValue(0.1)
        self.w_line_textbox = QLineEdit()
        self.w_line_textbox.setText('0')
        self.w_edge_textbox = QLineEdit()
        self.w_edge_textbox.setText('10')
        self.gamma_textbox = QLineEdit()
        self.gamma_textbox.setText('0.01')
        self.max_px_move_textbox = QLineEdit()
        self.boundary_option = QComboBox()
        self.convergence_textbox = QLineEdit()

        options_list = ['periodic', 'free', 'fixed', 'free-fixed',
                 'fixed-free', 'fixed-fixed', 'free-free']
        for each in options_list:
            self.boundary_option.addItem(each)

        layout = QGridLayout()
        layout.addWidget(self.openfile_dialog_btn, 0 , 0, 2, 0)
        layout.addWidget(alpha_spinbox_label, 1, 0)
        layout.addWidget(self.alpha_spinbox, 1, 1)
        layout.addWidget(beta_spinbox_label, 2, 0)
        layout.addWidget(self.beta_spinbox, 2, 1)
        layout.addWidget(w_line_spinbox_label, 3, 0)
        layout.addWidget(self.w_line_textbox, 3, 1)
        layout.addWidget(w_edge_spinbox_label, 4, 0)
        layout.addWidget(self.w_edge_textbox, 4, 1)
        layout.addWidget(gamma_label, 5, 0)
        layout.addWidget(self.gamma_textbox, 5, 1)
        layout.addWidget(boundary_label, 6, 0)
        layout.addWidget(self.boundary_option, 6, 1)
        layout.addWidget(max_px_move_label, 7, 0)
        layout.addWidget(self.max_px_move_textbox, 7, 1)
        layout.addWidget(convergence_label, 8, 0)
        layout.addWidget(self.convergence_textbox, 8, 1)

        layout.addWidget(self.process_image_btn, 9, 0, 2, 0)

        self.parameterGroupBox.setLayout(layout)

    def create_input_image_groupbox(self):
        input_image_groupbox = QGroupBox('Input Image')
        layout = QVBoxLayout()
        self.input_img_label = QLabel()

        # self.scene = QGraphicsScene()
        # self.view = QGraphicsView(self.scene)
        # self.view.mousePressEvent = self.get_position
        self.input_img_label.setAlignment(Qt.AlignTop)
        self.input_img_label.setAlignment(Qt.AlignLeft)
        self.input_img_label.mousePressEvent = self.get_start_position
        self.input_img_label.mouseReleaseEvent = self.get_end_position

        layout.addWidget(self.input_img_label)
        input_image_groupbox.setLayout(layout)
        return input_image_groupbox

    def create_ouput_image_groupbox(self):
        output_image_groupbox = QGroupBox('Output Image')
        layout = QVBoxLayout()
        # self.output_img_label = QLabel()

        self.figure = Figure()

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        # self.button = QPushButton('Plot')
        # self.button.clicked.connect(self.plot)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        output_image_groupbox.setLayout(layout)
        return output_image_groupbox

    def openfile_dialog(self):
        filename = QFileDialog.getOpenFileName(self, "Select Image")
        if filename:
            print(filename)
            self.current_img_path = filename[0]
            self.current_img = np.asarray(Image.open(self.current_img_path).convert('RGB'))
            # self.current_img = QImage(filename[0])
            self.render_image(self.current_img, self.input_img_label)

    def get_start_position(self, event):
        p = self.input_img_label.mapFrom(self.input_img_groupbox, event.pos())
        geometry = self.input_img_label.frameGeometry()
        self.start_x = p.x()+geometry.x()
        self.start_y = p.y()+geometry.y()

    def get_end_position(self, event):
        p = self.input_img_label.mapFrom(self.input_img_groupbox, event.pos())
        geometry = self.input_img_label.frameGeometry()
        self.end_x = p.x()+geometry.x()
        self.end_y = p.y()+geometry.y()

        print('sx = ', self.start_x, 'sy=',self.start_y, 'ex=',self.end_x, 'ey=',self.end_y)
        self.draw_rectangle()

    def draw_rectangle(self):
        self.current_img = cv2.rectangle(self.current_img, (self.start_x, self.start_y), (self.end_x, self.end_y),(255,0,0), 2)
        self.render_image(self.current_img, self.input_img_label)

        activeContour = ActiveContour()
        img_to_process = np.asarray(Image.open(self.current_img_path).convert('L'))
        # tolerence = 30
        # img_to_process = img_to_process[self.start_y-tolerence:self.end_y+tolerence, self.start_x-tolerence:self.end_x+tolerence]
        snake, init, img = activeContour.ative_algorithm(self.current_img_path, img_to_process, self.start_x, self.end_x, self.start_y, self.end_y)
        self.plot_graph(snake, init, img)

    def numpy_to_pixmap(self, img):
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return qImg

    def render_image(self, img, place_holder):
        pixmap = QPixmap(self.numpy_to_pixmap(img))
        h = self.input_img_groupbox.height()
        w = self.input_img_groupbox.width()
        # print('scaled to =', h)
        # mainsmaller_pixmap = pixmap.scaled(w, h,Qt.KeepAspectRatio, Qt.FastTransformation)
        place_holder.setPixmap(pixmap)
        print(place_holder.frameGeometry())

    def render_image_resized(self, img, place_holder):
        pixmap = QPixmap(self.numpy_to_pixmap(img))
        h = self.input_img_groupbox.height()
        w = self.input_img_groupbox.width()
        # print('scaled to =', h)
        mainsmaller_pixmap = pixmap.scaled(400, 400,Qt.KeepAspectRatio, Qt.FastTransformation)
        place_holder.setPixmap(mainsmaller_pixmap)
        print(place_holder.frameGeometry())

    def plot_graph(self, snake, init, img):
        ax = self.figure.add_subplot(111)
        ax.clear()
        import matplotlib.pyplot as plt
        ax.imshow(img, cmap=plt.cm.gray)
        ax.plot(init[:, 0], init[:, 1], '--r', lw=1)
        ax.plot(snake[:, 0], snake[:, 1], '-b', lw=1)
        ax.set_xticks([]), ax.set_yticks([])
        ax.axis([0, img.shape[1], img.shape[0], 0])
        self.render_image_resized(self.current_img, self.input_img_label)

        self.canvas.draw()
        # plt.savefig('test.png', bbox_inches="tight")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    screen = app.primaryScreen()
    h = screen.size().height()
    w = screen.size().width()
    gallery = WidgetGallery()
    gallery.setFixedSize(screen.size().width()-50, screen.size().height()-100)
    gallery.show()
    sys.exit(app.exec_())

