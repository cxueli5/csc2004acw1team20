# import libraries
from contextlib import redirect_stderr
import sys
import os
# import qypy libraries
from qtpy import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtCore import *
# from qtpy.QtCore import Qt, QFileSystemWatcher, QSettings, Signal
# import Endcode.py and Decode.py to use
import Encode
import Decode
from playsound import playsound
from threading import Thread


# drag and drop image into boxes (before clicking on encode and decode buttons)
class DragDropWidget(QLabel):
    # init constructor
    def __init__(self):
        super().__init__()

        # align images/docs/audio/video files in center when dragged and dropped into boxes
        self.setAlignment(Qt.AlignCenter)
        # styling of boxes
        self.setStyleSheet('''
            QLabel{
                background-color: rgb(229, 184, 206);                
                border: 4px dashed;
                border-color: rgb(15, 2, 130)
            }
        ''')
        # check if setAcceptDrops method returns true/false
        # if method returns true
        self.setAcceptDrops(True)
        # initialisation to get file path
        self.file_path = ""
        # get input from QLabel() object - used to display non-editable text/image
        self.label = QLabel()
   
    # method to set image file formats which program accepts (to encode and decode)
    def set_image(self, file_path):
        if(
            # program accepts image file formats: .jpg, .png, .tiff, .bmp
            # gets image file format
            os.path.splitext(self.file_path)[1] == ".jpg"
            or os.path.splitext(self.file_path)[1] == ".png"
            or os.path.splitext(self.file_path)[1] == ".tiff"
            or os.path.splitext(self.file_path)[1] == ".bmp"
        ):
            # reads image file and adjust size accordingly before displaying on screen
            # if image file is bigger than box, scale image to adjust size
            if(QPixmap(file_path).width() > self.width()):
                self.setPixmap(QPixmap(file_path).scaled(self.width(),
              
                                                       self.height(), Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self.setPixmap(QPixmap(file_path))
        # scale image file to fit nicely in box(es)
        else:
            self.setPixmap(QPixmap(file_path).scaled(100,
                                                     100, Qt.AspectRatioMode.KeepAspectRatio))

    # display text in text placeholder(s)
    def setPlaceholderText(self, text):
        self.setText('\n\n {} \n\n'.format(text))

    # method to handle drag event (what happens after drag input)
    def dragEnterEvent(self, event):
        # accept url drags
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()
    
    # method to handle move event
    def dragMoveEvent(self, event):
        # accept url drags
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    # method to handle drop event (what happens after drop)
    def dropEvent(self, event):
        # accpet url drops
        if event.mimeData().hasUrls:
            # set drop action to be the proposed action
            event.setDropAction(Qt.CopyAction)
            # sets file path of input from local file
            self.file_path = event.mimeData().urls()[0].toLocalFile()

            # retrieves file format
            file_type = os.path.splitext(self.file_path)[1]
            # if input detected is a .docx file, show word doc png
            # this is to give visual feedback to the users that a word doc file has been inputed
            if file_type == ".docx":
                self.set_image("icon/Word.png")
            # if input detected is a .txt file, show txt doc png
            # this is to give a visual feedback to the users that a text file has been inputed
            elif file_type == ".txt":
                self.set_image("icon/TXT.png")
            # if input detected is a .pptx file, show pptx png
            # this is to give a visual feedback to the users that a powerpoint file has been inputed
            elif file_type == ".pptx":
                self.set_image("icon/Powerpoint.png")
            # if input detected is a .xlsx file, show excel png
            # this is to give a visual feedback to the users that an excel file has been inputed
            elif file_type == ".xlsx":
                self.set_image("icon/Excel.png")
            # if input detected is a .pdf file, show pdf png
            # this is to give a visual feedback to the users that a pdf file has been inputed
            elif file_type == ".pdf":
                self.set_image("icon/pdf.png")
            # if input detected is a .mp3 file, show mp3 png
            # this is to give a visual feedback to the users that an excel file has been inputed
            elif file_type == ".mp3":
                self.set_image("icon/mp3.png")
            # if input detected is a .mp3 file, show mp3 png
            # this is to give a visual feedback to the users that a mp3 file has been inputed
            elif file_type == ".mp4":
                self.set_image("icon/mp4.png")
            # if input detected is a .wav file, show wav png
            # this is to give a visual feedback to the users that an wav audio file has been inputed
            elif file_type == ".wav":
                self.set_image("icon/WAV.png")
            # if input detected is a .mov file, show mov png
            # this is to give a visual feedback to the users that a mov video file has been inputed
            elif file_type == ".mov":
                self.set_image("icon/MOV.png")
            # if input detected is a .avi file, show avi png
            # this is to give a visual feedback to the users that an avi video file has been inputed
            elif file_type == ".avi":
                self.set_image("icon/AVI.png")
            # if image file formats are detected
            elif file_type == ".jpg":
                self.set_image("icon/jpg.png")
            elif (
                file_type == ".png"
                #or file_type == ".jpg"
                or file_type == ".tiff"
                or file_type == ".bmp"
            ):
            # go to set_image method and adjust size accordingly
                self.set_image(self.file_path)
            # if input does not meet the required file formats above
            else:
                # sends pop up and display error texts
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("File not supported.")
                errorMsg.setText(
                    "The following file types are supported: \nImage File Types: .jpg, .bmp, .png, .tiff\nDocument File Types: .docx, .txt, .xls, .pdf, .pptx\nAudio-Visual File Types: .mp3, .mp4, .wav, .mov, .avi")
                errorMsg.exec_()

            event.accept()

        else:
            event.ignore()

# method to select LSBs (from bits 0 to 7)
class LSBPosition(QWidget):
    # init constructor
    def __init__(self):
        super().__init__()
        # empty array to store bit list
        self.selectedBitList = []
        # dropdown to select number of bits
        self.bitsAmnt = QComboBox()
        self.bitsAmnt.setFont(QFont('Georgia',12))
        # list up to 7 bits
        for i in range(7):
            self.bitsAmnt.addItem("{}".format(i+1))
        self.bitsAmnt.currentIndexChanged.connect(self.selectionchange)

        # checkboxes to allow user to select the number of bits in LSB position
        self.checkBox0 = QCheckBox("Bit 0", self)
        self.checkBox1 = QCheckBox("Bit 1", self)
        self.checkBox2 = QCheckBox("Bit 2", self)
        self.checkBox3 = QCheckBox("Bit 3", self)
        self.checkBox4 = QCheckBox("Bit 4", self)
        self.checkBox5 = QCheckBox("Bit 5", self)
        self.checkBox6 = QCheckBox("Bit 6", self)

        self.checkBox0.stateChanged.connect(self.uncheck)
        self.checkBox1.stateChanged.connect(self.uncheck)
        self.checkBox2.stateChanged.connect(self.uncheck)
        self.checkBox3.stateChanged.connect(self.uncheck)
        self.checkBox4.stateChanged.connect(self.uncheck)
        self.checkBox5.stateChanged.connect(self.uncheck)
        self.checkBox6.stateChanged.connect(self.uncheck)

        # styling of choosing bits layout
        #self.layout = QHBoxLayout()
        self.layout = QGridLayout()
        #self.layout.addWidget(QLabel("Choose No. of Bits to replace (1-7):"))
        # self.layout.addWidget(QLabel("Choose No. of"),0,0,Qt.AlignRight)
        # self.layout.addWidget(QLabel("LSB to"),0,1,Qt.AlignLeft)
        # self.layout.addWidget(QLabel("replace:"),0,2,Qt.AlignLeft)
        # self.layout.addWidget(QLabel("(1-7):"),0,3,Qt.AlignLeft)
        bitsLabel = QLabel('Choose No. of LSB to replace:')
        bitsLabel.setFont(QFont('Georgia',12))
        self.layout.addWidget(bitsLabel)

        # self.layout.addWidget(QLine)
        # checkbox
        #self.layout.addWidget(QLabel("LSB Position:"),1,0,Qt.AlignLeft)
        self.layout.addWidget(self.bitsAmnt,0,4,Qt.AlignLeft)
        #@@@@@
        self.layout.addWidget(self.checkBox6,3,0,Qt.AlignRight)
        self.layout.addWidget(self.checkBox5,3,1)
        self.layout.addWidget(self.checkBox4,3,2)
        self.layout.addWidget(self.checkBox3,3,3)
        self.layout.addWidget(self.checkBox2,3,4)
        self.layout.addWidget(self.checkBox1,3,5)
        self.layout.addWidget(self.checkBox0,3,6)
        
        
        self.setLayout(self.layout)


        # default checkbox (for LSB position), bit 0 checked and displayed by default
        self.checkBox0.setChecked(True)
        self.checkBox0.setHidden(True)
        self.checkBox1.setHidden(True)
        self.checkBox2.setHidden(True)
        self.checkBox3.setHidden(True)
        self.checkBox4.setHidden(True)
        self.checkBox5.setHidden(True)
        self.checkBox6.setHidden(True)        

    # method to uncheck checkboxes (LSB position)
    def uncheck(self, state):
        # check if box is checked
        if state == Qt.Checked:
            if self.sender() == self.checkBox0:
                self.selectedBitList.append(0)
            elif self.sender() == self.checkBox1:
                self.selectedBitList.append(1)
            elif self.sender() == self.checkBox2:
                self.selectedBitList.append(2)
            elif self.sender() == self.checkBox3:
                self.selectedBitList.append(3)
            elif self.sender() == self.checkBox4:
                self.selectedBitList.append(4)
            elif self.sender() == self.checkBox5:
                self.selectedBitList.append(5)
            elif self.sender() == self.checkBox6:
                self.selectedBitList.append(6)
        # check if box is unchecked
        elif state == Qt.Unchecked:
            if self.sender() == self.checkBox0:
                self.selectedBitList.remove(0)
            elif self.sender() == self.checkBox1:
                self.selectedBitList.remove(1)
            elif self.sender() == self.checkBox2:
                self.selectedBitList.remove(2)
            elif self.sender() == self.checkBox3:
                self.selectedBitList.remove(3)
            elif self.sender() == self.checkBox4:
                self.selectedBitList.remove(4)
            elif self.sender() == self.checkBox5:
                self.selectedBitList.remove(5)
            elif self.sender() == self.checkBox6:
                self.selectedBitList.remove(6)                
        # print(self.selectedBitList)

    # method to change checkbox selection
    def selectionchange(self, i):
        # for j in range(i+1):
        #     if (getattr(self, "checkBox{}".format(j)).isHidden()):
        #         getattr(self, "checkBox{}".format(j)).setHidden(True)
        # for k in range(6, i, -1):
        #     if (getattr(self, "checkBox{}".format(k)).isHidden() == False):
        #         getattr(self, "checkBox{}".format(k)).setHidden(True)
        #         getattr(self, "checkBox{}".format(k)).setChecked(False)
        for j in range(i+1):            
            getattr(self, "checkBox{}".format(j)).setChecked(True)
        for k in range(6, i, -1):
            getattr(self, "checkBox{}".format(k)).setChecked(False)

# class for processing long-running tasks for threading purposes
class Worker(QObject):
    finished = Signal()
    progress = Signal(str)
    error = Signal(str)

    # init constructor
    def __init__(self, coverObject='', payload='', BitPosition='', stegaObject=''):
        super().__init__()
        # get value(s) of input by users
        self.coverObject = coverObject
        self.payload = payload
        self.BitPosition = BitPosition
        self.stegaObject = stegaObject

    # method to run after user clicks 'Encode' button
    def runEncode(self):
        """Long-running task."""
        # Encode.py, encode cover object, payload and bit position (when checked)
        Encode.encode(self.coverObject, self.payload, self.BitPosition)
        # if("Error"):
        #     self.error.emit("[ERROR] Insufficient Bit")
        # else:
        self.progress.emit("Status:  Encode Done")
        self.finished.emit()

    # method to run after user clicks 'Decode' button
    def runDecode(self):
        """Long-running task."""
        # Decode.py, decode cover object, payload and bit position (when checked)
        Decode.decode(self.stegaObject, self.BitPosition)
        self.progress.emit("Status:  Decode Done")
        self.finished.emit()


# styles of buttons for 'Encode' and 'Decode'
class ButtonWidgetforEnDecoding(QWidget):
    # init constructor
    def __init__(self):
        super().__init__()
        # encode button
        self.btnEncode = QPushButton("Encode")
        self.btnEncode.setFont(QFont('Georgia', 10))
        self.btnEncode.setStyleSheet('''
                QPushButton {
                    border: 1px solid #8f8f91;
                    border-radius: 6px;
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #e5b8ce, stop: 1 #dadbde);
                    min-width: 80px;
                    min-height: 40px;
                }

                QPushButton:pressed {
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                    stop: 0 #645f9d, stop: 1 #e5b8ce);
                }

                QPushButton:flat {
                    border: none; /* no border for a flat push button */
                }

                QPushButton:default {
                    border-color: navy; /* make the default button prominent */
                }

                /*background-color : #E4F4FA;*/
                /*border: none;*/
            
            '''
                                         )
        # decode button
        self.btnDecode = QPushButton("Decode")
        self.btnDecode.setFont(QFont('Georgia', 10))
        self.btnDecode.setStyleSheet('''
                QPushButton {
                    border: 1px solid #8f8f91;
                    border-radius: 6px;
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #e5b8ce, stop: 1 #dadbde);
                    min-width: 80px;
                    min-height: 40px;
                }

                QPushButton:pressed {
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                    stop: 0 #645f9d, stop: 1 #e5b8ce);
                }

                QPushButton:flat {
                    background-color: red;
                    border: none; /* no border for a flat push button */

                }

                QPushButton:default {
                    border-color: navy; /* make the default button prominent */
                }

                /*background-color : #E4F4FA;*/
                /*border: none;*/
            
            '''
                                     )

        # clear Bits button
        self.btnClear = QPushButton("Clear Bits")
        self.btnClear.setFont(QFont('Georgia', 10))
        self.btnClear.setStyleSheet('''
                QPushButton {
                    border: 1px solid #8f8f91;
                    border-radius: 6px;
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #e5b8ce, stop: 1 #dadbde);
                    min-width: 80px;
                    min-height: 40px;
                }

                QPushButton:pressed {
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                    stop: 0 #645f9d, stop: 1 #e5b8ce);
                }

                QPushButton:flat {
                    background-color: red;
                    border: none; /* no border for a flat push button */

                }

                QPushButton:default {
                    border-color: navy; /* make the default button prominent */
                }

                /*background-color : #E4F4FA;*/
                /*border: none;*/
            
            '''
                                     )

        # Clear files button
        self.btnClearFiles = QPushButton("Clear Files")
        self.btnClearFiles.setFont(QFont('Georgia', 10))
        self.btnClearFiles.setStyleSheet('''
                QPushButton {
                    border: 1px solid #8f8f91;
                    border-radius: 6px;
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #e5b8ce, stop: 1 #dadbde);
                    min-width: 80px;
                    min-height: 40px;
                }

                QPushButton:pressed {
                    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                    stop: 0 #645f9d, stop: 1 #e5b8ce);
                }

                QPushButton:flat {
                    background-color: red;
                    border: none; /* no border for a flat push button */

                }

                QPushButton:default {
                    border-color: navy; /* make the default button prominent */
                }

                /*background-color : #E4F4FA;*/
                /*border: none;*/
            
            '''
                                     )

        self.filePath_displayResult = ''
        # when encoding / decoding, display doraemon finding gif
        self.resultLabel = QLabel('Doraemon Steganography Time!')
        self.resultLabel.setFont(QFont('Georgia',18))
        self.Image_label = QLabel()
        self.extaLineLabel = QLabel("")
        self.movie = QMovie("gif/Doraemon Finding.gif")

    # error message output if encounter insufficient bits in file(s)
    def set_error(self):        
        self.resultLabel.setText("Insufficient bits, need bigger cover object or smaller payload!")
        self.Image_label.setPixmap(QPixmap("icon/Doraemon Error.png"))

    # after successful encode / decode
    def set_img(self):
        self.resultLabel.setText("Completed!")
        self.Image_label.setPixmap(QPixmap("icon/Doraemon.png"))

    # when encode / decode
    def set_gif(self):
        self.resultLabel.setText("Doraemon is working on it...")
        self.Image_label.setMovie(self.movie)
        self.movie.start()

    # method for encoding stegnography (with error message popup functionalities)
    def encodeStegaWithPopUpError(self, payload, coverObject, BitPosition):

        # get file format(s) of payload and cover object
        payloadFileType = os.path.splitext(payload)[1]
        coverObjectFileType = os.path.splitext(coverObject)[1]

        # if detect no input, display error message
        if(payload == '' and coverObject == ''):
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("Error!")
            errorMsg.setText(
                "Please drop a cover object file and a payload file to encode.")
            errorMsg.exec_()
        # if correct file format(s) are input into program
        elif (
            (
                payloadFileType == '.docx'
                or payloadFileType == '.txt'
                or payloadFileType == '.pptx'
                or payloadFileType == '.xlsx'
                or payloadFileType == '.mp3'
                or payloadFileType == '.mp4'
                or payloadFileType == '.png'
                or payloadFileType == '.pdf'
                or payloadFileType == '.tiff'
                or payloadFileType == '.jpg'
                or payloadFileType == '.bmp'
                or payloadFileType == '.wav'
                or payloadFileType == '.mov'
                or payloadFileType == '.avi'
            )
            and
            (
                # coverObjectFileType == '.docx'
                # or coverObjectFileType == '.txt'
                # or coverObjectFileType == '.pptx'
                # or coverObjectFileType == '.xlsx'
                coverObjectFileType == '.mp3'
                or coverObjectFileType == '.mp4'
                or coverObjectFileType == '.png'
                # or coverObjectFileType == '.pdf'
                or coverObjectFileType == '.tiff'
                or coverObjectFileType == '.jpg'
                or coverObjectFileType == '.bmp'
                or coverObjectFileType == '.mov'
                or coverObjectFileType == '.avi'
                or coverObjectFileType == '.wav'
            )

        ):
            # display error message if no input detected
            if(payload == '' or coverObject == ''):
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("Error!")
                errorMsg.setText(
                    "Please drop a cover object file and a payload file to encode.")
                errorMsg.exec_()

            # check if payload is too large to encode
            elif(os.path.getsize(payload) >= os.path.getsize(coverObject)):
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("Error!")
                errorMsg.setText(
                    "Payload cannot be larger than Cover Object.")
                errorMsg.exec_()

            # input meets all conditions, proceed to encode
            else:
                print("Status:  Encoding")
                # display Doraemon working gif
                self.set_gif()

                # create QThread object
                self.thread = QThread()
                # create worker object
                self.worker = Worker(
                    coverObject=coverObject,
                    payload=payload,
                    BitPosition=BitPosition
                )
                # move worker to the thread
                self.worker.moveToThread(self.thread)
                # connect signals and slots
                self.thread.started.connect(self.worker.runEncode)
                self.worker.finished.connect(self.thread.quit)
                self.worker.finished.connect(self.worker.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                self.worker.progress.connect(self.set_img)
                self.worker.error.connect(self.set_error)
                # start the thread
                self.thread.start()

                # resets
                self.btnEncode.setEnabled(False)
                self.btnDecode.setEnabled(False)
                self.btnClear.setEnabled(False)
                self.btnClearFiles.setEnabled(False)
                self.thread.finished.connect(
                    lambda: self.btnEncode.setEnabled(True)
                )
                self.thread.finished.connect(
                    lambda: self.btnDecode.setEnabled(True)
                )
                self.thread.finished.connect(
                    lambda: self.btnClear.setEnabled(True)
                )
                self.thread.finished.connect(
                    lambda: self.btnClearFiles.setEnabled(True)
                )
        # detects unsupported file formats in the program, display error message
        else:
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle(
                "Some file currently not supported for encoding.")
            errorMsg.setText(
                "Please try another file. \n\nSupported Cover file formats: .bmp, .png, .tiff, .mp3, .mp4, .wav, .mov, .avi\n\nSupported Payload file formats: .jpg, .bmp, .png, .tiff, .docx, .txt, xlsx, .pdf, .pptx, .mp3, .mp4, .wav, .mov, .avi")
            errorMsg.exec_()

     # method for decoding stegnography (with error message popup functionalities)
    def decodeStegaWithPopUpError(self, stegaObject, BitPosition):
        # get file format
        stegaObjectFileType = os.path.splitext(stegaObject)[1]
        if (
            # stegaObjectFileType == '.docx'
            # or stegaObjectFileType == '.txt'
            # or stegaObjectFileType == '.pptx'
            # or stegaObjectFileType == '.xlsx'
            stegaObjectFileType == '.mp3'
            or stegaObjectFileType == '.mp4'
            # or stegaObjectFileType == '.pdf'
            or stegaObjectFileType == '.png'
            or stegaObjectFileType == '.tiff'
            or stegaObjectFileType == '.jpg'
            or stegaObjectFileType == '.bmp'
            or stegaObjectFileType == '.mov'
            or stegaObjectFileType == '.avi'
            or stegaObjectFileType == '.wav'
        ):

            print("Status:  Decoding")
            self.set_gif()

            # create QThread object
            self.thread = QThread()
            # create worker object
            self.worker = Worker(stegaObject=stegaObject,
                                 BitPosition=BitPosition)
            # move worker to the thread
            self.worker.moveToThread(self.thread)
            # connect signals and slots
            
            self.thread.started.connect(self.worker.runDecode)
            self.worker.finished.connect(self.thread.quit)            
            self.worker.finished.connect(self.worker.deleteLater)            
            self.thread.finished.connect(self.thread.deleteLater)            
            self.worker.progress.connect(self.set_img)        
            self.worker.error.connect(self.set_error)
            
            self.thread.start()
            # resets
            self.btnEncode.setEnabled(False)
            self.btnDecode.setEnabled(False)
            self.btnClear.setEnabled(False)
            self.btnClearFiles.setEnabled(False)
        
            self.thread.finished.connect(
                lambda: self.btnEncode.setEnabled(True)
            )
            self.thread.finished.connect(
                lambda: self.btnDecode.setEnabled(True)
            )
            self.thread.finished.connect(
                lambda: self.btnClear.setEnabled(True)
            )
            self.thread.finished.connect(
                lambda: self.btnClearFiles.setEnabled(True)
            )
        # detects unsupported file formats in the program, display error message
        else:
            if(stegaObject != ''):
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("Error!")
                errorMsg.setText(
                    "Unsupported File Type.")
                errorMsg.exec_()
            else:
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("Error!")
                errorMsg.setText("No steganography object detected.")
                errorMsg.exec_()
        
# virtual window display after running program
class Window(QWidget):
    # init constructor
    def __init__(self):
        super().__init__()
        # window title
        self.setWindowTitle("Team 20 Steganography Tool")
        # self.setStyleSheet("background-color:#6e6e6e")

        # window background colour
        p = QPalette()
        gradient = QLinearGradient(0, 0, 800, 800)
        gradient.setColorAt(0.0, QColor(174, 127, 156))
        gradient.setColorAt(1.0, QColor(117, 108, 143))
        p.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(p)

        # window resize
        self.resize(1600, 800)
        # self.resize(1200, 800)

        # encode, decode button class
        buttonEncodeDecode = ButtonWidgetforEnDecoding()

        # dropdown layout
        layoutForDropDown = QHBoxLayout()
        # checkbox for LSB bit position (returns list)
        bitPosition = LSBPosition()
        layoutForDropDown.addWidget(bitPosition)
        layoutForDropDown.setAlignment(Qt.AlignCenter)
        # end dropdown layout

        # encoding (for first layout)
        firstLayout = QVBoxLayout()

        # drag and drop cover object
        drag_drop_cover_object = DragDropWidget()
        drag_drop_cover_object.setPlaceholderText("Drag Cover Object Here")
        drag_drop_cover_object.setFixedSize(400, 350)
        drag_drop_cover_object.setFont(QFont('Georgia',18))

        # drag and drop payload
        drag_drop_payload = DragDropWidget()
        drag_drop_payload.setPlaceholderText("Drag Payload Here")
        drag_drop_payload.setFixedSize(400, 350)
        drag_drop_payload.setFont(QFont('Georgia',18))

        firstLayout.addWidget(drag_drop_cover_object)
        # label for drag and drop cover object
        laebl = drag_drop_cover_object.label
        laebl.setFixedWidth(400)
        firstLayout.addWidget(laebl)

        firstLayout.addWidget(drag_drop_payload)
        # label for drag and drop payload
        laebl2 = drag_drop_payload.label
        laebl2.setFixedWidth(400)
        firstLayout.addWidget(laebl2)
        
        # encode, decode button, show popup error message if conditions not met
        buttonEncodeDecode.btnEncode.clicked.connect(lambda: buttonEncodeDecode.encodeStegaWithPopUpError(
            drag_drop_payload.file_path, drag_drop_cover_object.file_path, bitPosition.selectedBitList))

        # add buttons to layout
        firstLayout.addWidget(buttonEncodeDecode.btnEncode)
        # align buttons to center
        firstLayout.setAlignment(Qt.AlignCenter)
        # end of firstLayout

        # decoding (second layout)
        secondLayout = QVBoxLayout()

        # drag and drop output of encoded file into box (for decode)
        drag_drop_stega_object = DragDropWidget()
        drag_drop_stega_object.setPlaceholderText("Drag Encoded File Here")
        drag_drop_stega_object.setFixedSize(400, 350)
        drag_drop_stega_object.setFont(QFont('Georgia',18))


        # encode, decode button, show popup error message if conditions not met
        buttonEncodeDecode.btnDecode.clicked.connect(lambda: buttonEncodeDecode.decodeStegaWithPopUpError(
            drag_drop_stega_object.file_path, bitPosition.selectedBitList))

        buttonEncodeDecode.btnClear.clicked.connect(lambda:     
        (bitPosition.checkBox0.setChecked(False), 
        bitPosition.checkBox1.setChecked(False),
        bitPosition.checkBox2.setChecked(False),
        bitPosition.checkBox3.setChecked(False),
        bitPosition.checkBox4.setChecked(False),
        bitPosition.checkBox5.setChecked(False),
        bitPosition.checkBox6.setChecked(False))
        )

        buttonEncodeDecode.btnClearFiles.clicked.connect(lambda:     
        (drag_drop_payload.setPlaceholderText("Drag Payload Here"),
        drag_drop_cover_object.setPlaceholderText("Drag Cover Object Here"),
        drag_drop_stega_object.setPlaceholderText("Drag Encoded File Here"))
        )

        secondLayout.addWidget(drag_drop_stega_object)
        # label for drag and drop object (file input into decode box)
        laebl3 = drag_drop_stega_object.label
        laebl3.setFixedWidth(400)
        secondLayout.addWidget(laebl3)

        # add buttons to layout
        secondLayout.addWidget(buttonEncodeDecode.btnDecode)
        # align buttons to center
        secondLayout.setAlignment(Qt.AlignCenter)
        # end of secondLayout

        # thirdLayout for Doraemon image when program starts
        loading = buttonEncodeDecode.Image_label
        loading.setPixmap(QPixmap("icon/Doraemon.png"))
        loading.setAlignment(Qt.AlignCenter)

        # 'Doraemon Steganography Time!' label style (upon program startup)
        labelResult = buttonEncodeDecode.resultLabel
        labelResult.setFont(QFont('Georgia',14))
        labelResult.setStyleSheet('''
            QLabel{
                color: Navy;
                font: bold;
            }
        ''')
        
        
        labelResult.setAlignment(Qt.AlignCenter)

        thirdLayout = QVBoxLayout()
        #thirdLayout = QGridLayout()

        thirdLayout.addWidget(labelResult)
        thirdLayout.addWidget(loading)
        
        thirdLayout.addLayout(layoutForDropDown)
        thirdLayout.setAlignment(Qt.AlignCenter)
        # align buttons to center
        
        # add buttons to layout jeff add!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        thirdLayout.addWidget(buttonEncodeDecode.btnClearFiles)
        #thirdLayout.addWidget(buttonEncodeDecode.btnClear)


        # end of thirdLayout

        # set all 3 layouts
        # [  [Layout1, Encode][Layout2, Decode][Layout3, Doraemon]  ]
        layoutForThreeLayout = QHBoxLayout()
        layoutForThreeLayout.addLayout(firstLayout, 1)
        # OVER HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        layoutForThreeLayout.addLayout(secondLayout, 1)
        layoutForThreeLayout.addLayout(thirdLayout, 1)

        # [    Dropdown 1 & Dropdown 2    ]
        # [  [Layout1, Encode][Layout2, Decode][Layout3, Doraemon]  ]
        allLayout = QVBoxLayout()
        # allLayout.addLayout(layoutForDropDown)
        allLayout.addLayout(layoutForThreeLayout)

        # jeff test


        self.setLayout(allLayout)
        # end of set all 3 layouts

# main method to run program
if __name__ == "__main__":


    def func1():
        app = QApplication(sys.argv)
        window = Window()
        window.show()
        sys.exit(app.exec_())

    def func2(): 
        playsound('theme.mp3', True)
    
    
    Thread(target = func1).start()
    Thread(target = func2).start()
# end of main method