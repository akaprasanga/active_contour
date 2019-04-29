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
    active_thread_signal = pyqtSignal(list)

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
        self.another_process = ActiveThread()
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
        self.list_of_points = []
        self.color = (0,255,0)

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def connect_signals(self):
        self.openfile_dialog_btn.clicked.connect(self.openfile_dialog)
        self.another_process.active_thread_signal.connect(self.active_thread_complete)
        self.process_image_btn.clicked.connect(self.draw_outline)

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
        max_px_move_label = QLabel('Maximum pixel distance to move per iteration')
        convergence_label = QLabel('Convergence criteria.')
        max_iteration_label = QLabel('Maximum iterations to optimize snake shape.')
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
        self.max_px_move_textbox.setText('1.0')
        self.boundary_option = QComboBox()
        self.convergence_textbox = QLineEdit()
        self.convergence_textbox.setText('0.1')
        self.max_iteration_spinbox = QSpinBox()
        self.max_iteration_spinbox.setSingleStep(500)
        self.max_iteration_spinbox.setMaximum(2500)
        self.max_iteration_spinbox.setMinimum(500)
        self.max_iteration_spinbox.setValue(500)
        self.time_label = QLabel()

        options_list = ['fixed', 'free', 'periodic', 'free-fixed',
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
        layout.addWidget(max_iteration_label, 9, 0)
        layout.addWidget(self.max_iteration_spinbox, 9, 1)

        layout.addWidget(self.process_image_btn, 10, 0, 2, 0)
        layout.addWidget(self.time_label, 11,0,2,0)

        self.parameterGroupBox.setLayout(layout)

    def create_input_image_groupbox(self):
        input_image_groupbox = QGroupBox('Input Image')
        layout = QVBoxLayout()
        self.input_scene = QGraphicsScene()
        self.input_view = QGraphicsView(self.input_scene)


        # self.scene = QGraphicsScene()
        # self.view = QGraphicsView(self.scene)
        # self.view.mousePressEvent = self.get_position
        # self.input_img_label.setAlignment(Qt.AlignTop)
        # self.input_img_label.setAlignment(Qt.AlignLeft)
        self.input_view.mousePressEvent = self.get_coordinate


        layout.addWidget(self.input_view)
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
        if filename[0] != '':
            print(filename)
            self.current_img_path = filename[0]
            self.current_img = np.asarray(Image.open(self.current_img_path).convert('RGB'))
            # self.current_img = QImage(filename[0])
            self.render_image(self.current_img, self.input_scene)
            self.list_of_points = []

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
        if self.current_img_path == None:
            print('No image')
        else:
            self.draw_rectangle()

    def draw_rectangle(self):
        self.current_img = cv2.line(self.current_img, (self.start_x, self.start_y), (self.end_x, self.end_y),(255,0,0), 2)
        self.render_image(self.current_img, self.input_img_label)
        self.call_worker_thread()

    def get_status(self):

        # def active_contour(image, snake, alpha=0.01, beta=0.1,
        #                    w_line=0, w_edge=1, gamma=0.01,
        #                    bc='periodic', max_px_move=1.0,
        #                    max_iterations=2500, convergence=0.1):

        parameter_list = []
        parameter_list.append(self.alpha_spinbox.value())
        parameter_list.append(self.beta_spinbox.value())
        parameter_list.append(int(self.w_line_textbox.text()))
        parameter_list.append(int(self.w_edge_textbox.text()))
        parameter_list.append(float(self.gamma_textbox.text()))
        parameter_list.append(str(self.boundary_option.currentText()))
        parameter_list.append(float(self.max_px_move_textbox.text()))
        parameter_list.append(int(self.max_iteration_spinbox.value()))
        parameter_list.append(float(self.convergence_textbox.text()))

        return parameter_list

    def call_worker_thread(self, guided_line):
        img_to_process = np.asarray(Image.open(self.current_img_path).convert('L'))
        self.another_process.image_to_process = img_to_process
        self.another_process.image_path = self.current_img_path
        self.another_process.parameter_list = self.get_status()
        self.another_process.guided_line = guided_line
        self.another_process.start()

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
        place_holder.clear()
        place_holder.addPixmap(pixmap)

    def render_image_resized(self, img, place_holder):
        pixmap = QPixmap(self.numpy_to_pixmap(img))
        h = self.input_img_groupbox.height()
        w = self.input_img_groupbox.width()
        # print('scaled to =', h)
        # mainsmaller_pixmap = pixmap.scaled(400, 400,Qt.KeepAspectRatio, Qt.FastTransformation)
        place_holder.addPixmap(pixmap)

    def plot_graph(self, snake, init, img):
        ax = self.figure.add_subplot(111)
        ax.clear()
        import matplotlib.pyplot as plt
        ax.imshow(img, cmap=plt.cm.gray)
        # ax.plot(init[:, 0], init[:, 1], '--', lw=1)
        ax.plot(snake[:, 0], snake[:, 1], '-g', lw=2)
        ax.set_xticks([]), ax.set_yticks([])
        ax.axis([0, img.shape[1], img.shape[0], 0])
        self.render_image_resized(self.current_img, self.input_scene)

        self.canvas.draw()
        # plt.savefig('test.png', bbox_inches="tight")

    def get_coordinate(self, event):
        pos = self.input_view.mapToScene(event.pos())
        x = int(pos.x())
        y = int(pos.y())
        print(x, y)
        self.draw_points(x,y)

    def draw_points(self, x, y):
        self.list_of_points.append(tuple((x,y)))
        self.current_img = cv2.circle(self.current_img, (x, y), 5, self.color, -1)
        self.render_image(self.current_img, self.input_scene)

    def draw_outline(self):
        activeContour = ActiveContour()
        final_init = activeContour.create_outline_for_extraction(self.list_of_points)
        for i, each in enumerate(self.list_of_points):
            if i < len(self.list_of_points)-1:
                self.current_img = cv2.line(self.current_img, self.list_of_points[i], self.list_of_points[i+1], (255, 0, 0), thickness=2)
        self.render_image(self.current_img, self.input_scene)
        self.call_worker_thread(final_init)

    @QtCore.pyqtSlot(list)
    def active_thread_complete(self, returned_list):
        print('returned')
        self.plot_graph(returned_list[0], returned_list[1], returned_list[2])
        self.time_label.setText('Time taken = '+ str(returned_list[3]))


class ActiveThread(QThread):
    active_thread_signal = pyqtSignal(list)
    def __init__(self, parent=None):
        super(ActiveThread, self).__init__(parent)
        self.image_to_process = None
        self.image_path = ''
        self.parameter_list = None
        self.guided_line = None

    @QtCore.pyqtSlot()
    def run(self):
        activeContour = ActiveContour()
        # filename, img, start_x, end_x, start_y, end_y
        return_list = []
        snake, rect, img, time = activeContour.ative_algorithm(self.image_path, self.image_to_process, self.guided_line, self.parameter_list)
        return_list.append(snake)
        return_list.append(rect)
        return_list.append(img)
        return_list.append(time)
        print('still in thread')
        self.active_thread_signal.emit(return_list)


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

