import sys
import pandas as pd
import numpy as np
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import HestonModel

# System/About windows
class AboutForm(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("BitcoinSystem - About")
        self.resize(800, 600)
        self.centralWidget = QLabel(
        "BitcoinSystem prototype\n\n" 
        "Wintom Financial Technology Inc.\n\n"
        "GitHub: BinChian/BitcoinOptionSystem")
        self.centralWidget.setFont(QFont('Consolas', 20))
        self.centralWidget.setStyleSheet("color: red; background-color: lightyellow; border: 1px solid black;")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)

class OptionSimulation(QMainWindow):
    def __init__(self, parent = None, defaultWindow = ''):
        super(OptionSimulation, self).__init__(parent)
        
        self.defaultWindow = defaultWindow
        self.setWindowTitle('BitcoinSystem - Option Simulation')
        self.resize(1400, 900)
        self.setMinimumSize(1400, 900)
        self.setMaximumSize(1400, 900)
        
        # Load Heston model
        calibration = HestonModel.Calibration()
        params = calibration.params

        # Heston model parameters table
        hestonParamsTableHeader = []
        hestonParamsTable = QTableWidget(1, 7)
        
        ## Adding items to the table
        i = 0
        for key, value in params.items():
            hestonParamsTableHeader.append(key)
            if type(value) != str:
                value = str(round(value, 2))
            newItem = QTableWidgetItem(value)
            newItem.setFont(QFont('Consolas', 24))
            newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            hestonParamsTable.setItem(0, i, newItem)
            i += 1

        hestonParamsTable.setHorizontalHeaderLabels(hestonParamsTableHeader)
        hestonParamsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        hestonParamsTable.horizontalHeader().setFont(QFont('Consolas', 24))
        hestonParamsTable.setRowHeight(0, 1000)
        hestonParamsTable.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        hestonParamsTable.verticalHeader().setVisible(False)
        hestonParamsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Option input layout
        ## Option input layout (left)
        ### Option combobox layout
        #### Exotic option select combobox
        self.exoticOptionCombobox = QComboBox(self)
        self.exoticOptionCombobox.addItems(['Select Exotic Option', 'Vanilla Option', 'Digital Option', 'Barrier Option'])
        self.exoticOptionCombobox.insertSeparator(1)
        self.exoticOptionCombobox.setFont(QFont('Consolas', 24))
        self.exoticOptionCombobox.setFixedSize(700, 50)
        self.exoticOptionCombobox.currentIndexChanged.connect(self.exoticOptionComboboxClicked)
        
        #### Option Type select combobox
        self.optionType = ''
        self.optionTypeCombobox = QComboBox(self)
        self.optionTypeCombobox.addItems(['Option Type', 'Call', 'Put'])
        self.optionTypeCombobox.insertSeparator(1)
        self.optionTypeCombobox.setFont(QFont('Consolas', 24))
        self.optionTypeCombobox.setFixedSize(700, 50)
        self.optionTypeCombobox.currentIndexChanged.connect(self.optionTypeComboboxClicked)
        
        #### Combine option combobox layout
        optionComboboxLayout = QVBoxLayout()
        optionComboboxLayout.addWidget(self.exoticOptionCombobox)
        optionComboboxLayout.addWidget(self.optionTypeCombobox)
        
        ### Condition layout
        #### Default interface
        defaultInterfaceLabel = QLabel('Exotic Option Simulation')
        defaultInterfaceLabel.setFont(QFont('Consolas', 20))
        defaultInterfaceLabel.setStyleSheet("color: red; background-color: lightyellow; border: 1px solid black;")
        defaultInterfaceLabel.setFixedSize(700, 350)
        defaultInterfaceLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        #### Option input stack
        self.vanillaInputStackWidget = QWidget()
        self.vanillaInputStack()
        self.digitalInputStackWidget = QWidget()
        self.digitalInputStack()
        self.barrierInputStackWidget = QWidget()
        self.barrierInputStack()

        self.optionInputStack = QStackedWidget()
        self.optionInputStack.addWidget(defaultInterfaceLabel)
        self.optionInputStack.addWidget(self.vanillaInputStackWidget)
        self.optionInputStack.addWidget(self.digitalInputStackWidget)
        self.optionInputStack.addWidget(self.barrierInputStackWidget)
        
        #### Enter button
        enterBtn = QPushButton('Enter',self)
        enterBtn.clicked.connect(self.submit)
        enterBtn.setFont(QFont('Consolas', 20))
        enterBtn.setFixedSize(200,50)
        
        ### Combine condition layout
        conditionLayout = QVBoxLayout()
        conditionLayout.addLayout(optionComboboxLayout)
        conditionLayout.addWidget(self.optionInputStack)
        conditionLayout.addWidget(enterBtn, 0, Qt.AlignRight | Qt.AlignBottom)
        
        ## Option input layout (right)
        ### Expiration text
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.calLayout = QVBoxLayout()
        self.calWord = QLabel('Expiration')
        self.calWord.setFixedHeight(50)
        self.calWord.setFont(QFont('Consolas', 20))
        self.calWord.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        ### Expiration calendar
        self.cal = QCalendarWidget(self)
        self.cal.setMinimumDate(QDate(1900, 1, 1))
        self.cal.setMaximumDate(QDate(2022,11,23))
        self.cal.setGridVisible(True)
        self.cal.clicked[QDate].connect(self.showDate)
        
        ### Combine Option input layout (right)
        self.calLayout.addWidget(self.calWord)
        self.calLayout.addWidget(self.cal)
        
        ## combine option input layout 
        optionInputLayout = QHBoxLayout()
        optionInputLayout.addLayout(conditionLayout)
        optionInputLayout.addLayout(self.calLayout)
 
        # NPV Layout
        self.npvWidget = QLabel("Net Present Value")
        self.npvWidget.setFixedSize(1400, 200)
        self.npvWidget.setFont(QFont('Consolas', 20))
        self.npvWidget.setStyleSheet("color: red; background-color: lightyellow;")
        self.npvWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Combine option simulation window layout
        allLayout = QVBoxLayout()
        allLayout.addWidget(hestonParamsTable)
        allLayout.addLayout(optionInputLayout)
        allLayout.addWidget(self.npvWidget)
        
        widget = QWidget()
        widget.setLayout(allLayout)
        self.setCentralWidget(widget)
        
        if self.defaultWindow == '':
            pass
        elif self.defaultWindow == 'Vanilla Option':
            self.exoticOptionCombobox.setCurrentText('Vanilla Option')
            self.optionInputStack.setCurrentIndex(1)
        elif self.defaultWindow == 'Digital Option':
            self.exoticOptionCombobox.setCurrentText('Digital Option')
            self.optionInputStack.setCurrentIndex(2)
        elif self.defaultWindow == 'Barrier Option':
            self.exoticOptionCombobox.setCurrentText('Barrier Option')
            self.optionInputStack.setCurrentIndex(3)
        
    def exoticOptionComboboxClicked(self):
        self.exoticOptionCombobox.model().item(0).setEnabled(False)
        if self.exoticOptionCombobox.currentText() == "Vanilla Option":
            self.optionInputStack.setCurrentIndex(1)
        elif self.exoticOptionCombobox.currentText() == "Digital Option":
            self.optionInputStack.setCurrentIndex(2)
        elif self.exoticOptionCombobox.currentText() == "Barrier Option":
            self.optionInputStack.setCurrentIndex(3)
            
    def optionTypeComboboxClicked(self):
        self.optionTypeCombobox.model().item(0).setEnabled(False)
        if self.optionTypeCombobox.currentText() == 'Call':
            self.optionType = 'Call'
        elif self.optionTypeCombobox.currentText() == 'Put':
            self.optionType = 'Put'  
            
    def showDate(self,date):
        self.date = date.toString('yyyy-MM-dd')
        
    def submit(self):
        # Warning and default value
        maturity = self.date
        
        ## Check the exotic option
        if self.exoticOptionCombobox.currentText() == 'Select Exotic Option':
            if self.defaultWindow == '':
                QMessageBox.warning(self, 'Warning', 'Did not select the exotic option!')
                return
            else:
                exoticOptionType = self.defaultWindow
        else: 
            exoticOptionType = self.exoticOptionCombobox.currentText()
        
        ## Check the option type
        if self.optionType == '':
            QMessageBox.warning(self, 'Warning', 'Did not select Option Type!')
            return
        
        ## Check the barrier of barrier option
        if exoticOptionType == "Barrier Option":
            if self.barrierCombobox.currentText() == 'Barrier Type':
                QMessageBox.warning(self, 'Warning', 'Did not select barrier Type!')
                return
        
        ## Check the strike
        if not (self.vanillaStrike.text() or self.digitalStrike.text() or self.barrierStrike.text() != ''):
            QMessageBox.warning(self, 'Warning', 'Did not input strike!')
            return
        
        # Calculate the NPV
        if exoticOptionType == "Vanilla Option":
            vanilla = HestonModel.VanillaOptionSimulation()
            strike = float(self.vanillaStrike.text())
            if self.optionType == 'Call':
                NPV = vanilla.callNPV(maturity, strike)
            elif self.optionType == 'Put':
                NPV = vanilla.putNPV(maturity, strike)
                
        elif exoticOptionType == "Digital Option":
            digital = HestonModel.DigitalOptionSimulation()
            strike = float(self.digitalStrike.text())
            if self.optionType == 'Call':
                NPV = digital.callNPV(maturity, strike)
            elif self.optionType == 'Put':
                NPV = digital.putNPV(maturity, strike)

        elif exoticOptionType == "Barrier Option":
            barrier = HestonModel.BarrierOptionSimulation()
            strike = float(self.barrierStrike.text())
            
            if self.barrierType == 'DownOut':
                ## Check the down barrier
                if self.downBarrier.text() == '':
                    QMessageBox.warning(self, 'Warning', 'Did not input down barrier!')
                    return
                else:
                    downBarrier = float(self.downBarrier.text())

                if self.optionType == 'Call':
                    NPV = barrier.downoutCallNPV(maturity, strike, downBarrier)
                elif self.optionType == 'Put':
                    NPV = barrier.downoutPutNPV(maturity, strike, downBarrier)
        
        self.npvWidget.setText('Net Present Value = ' + str(round(NPV, 2)))
    
    def vanillaInputStack(self):
        layout = QVBoxLayout()
        
        # Strike Layout
        strikeLayout = QFormLayout()
        self.vanillaStrike = QLineEdit()
        self.vanillaStrike.setFixedHeight(50)
        self.vanillaStrike.setFont(QFont('Consolas', 20))
        self.vanillaStrike.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        strikeWord = QLabel('Strike: ')
        strikeWord.setFixedSize(210, 50)
        strikeWord.setFont(QFont('Consolas', 20))
        strikeWord.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        strikeLayout.addRow(strikeWord, self.vanillaStrike)

        # Total
        layout.addLayout(strikeLayout)
        self.vanillaInputStackWidget.setLayout(layout)

    def digitalInputStack(self):
        layout = QVBoxLayout()
        
        # Strike
        strikeLayout = QFormLayout()
        self.digitalStrike = QLineEdit()
        self.digitalStrike.setFixedHeight(50)
        self.digitalStrike.setFont(QFont('Consolas', 20))
        self.digitalStrike.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        strikeWord = QLabel('Strike: ')
        strikeWord.setFixedSize(210, 50)
        strikeWord.setFont(QFont('Consolas', 20))
        strikeWord.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        strikeLayout.addRow(strikeWord, self.digitalStrike)

        # Total
        layout.addLayout(strikeLayout)

        self.digitalInputStackWidget.setLayout(layout)

    def barrierInputStack(self):
        layout = QVBoxLayout()
        
        self.barrierCombobox = QComboBox(self)
        self.barrierCombobox.addItems(['Barrier Type', 'DownOut'])
        self.barrierCombobox.currentIndexChanged.connect(self.barrierComboboxClick)
        self.barrierCombobox.insertSeparator(1)
        self.barrierCombobox.setFixedHeight(50)
        self.barrierCombobox.setFont(QFont('Consolas', 20))
        
        strikeLayout = QFormLayout()
        self.barrierStrike = QLineEdit()
        self.barrierStrike.setFixedHeight(50)
        self.barrierStrike.setFont(QFont('Consolas', 20))
        self.barrierStrike.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        strikeWord = QLabel('Strike: ')
        strikeWord.setFixedSize(210, 50)
        strikeWord.setFont(QFont('Consolas', 20))
        strikeWord.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        strikeLayout.addRow(strikeWord, self.barrierStrike)
        
        self.upBarrierLayout = QFormLayout()
        self.upBarrier = QLineEdit()
        self.upBarrier.setFixedHeight(50)
        self.upBarrier.setFont(QFont('Consolas', 20))
        self.upBarrier.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.upBarrierWord = QLabel('Up Barrier: ')
        self.upBarrierWord.setFixedSize(210, 50)
        self.upBarrierWord.setFont(QFont('Consolas', 20))
        self.upBarrierWord.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.upBarrierLayout.addRow(self.upBarrierWord, self.upBarrier)
        
        self.downBarrierLayout = QFormLayout()
        self.downBarrier = QLineEdit()
        self.downBarrier.setFixedHeight(50)
        self.downBarrier.setFont(QFont('Consolas', 20))
        self.downBarrier.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.downBarrierWord = QLabel('Down Barrier: ')
        self.downBarrierWord.setFixedSize(210, 50)
        self.downBarrierWord.setFont(QFont('Consolas', 20))
        self.downBarrierWord.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.downBarrierLayout.addRow(self.downBarrierWord, self.downBarrier)

        # Total
        layout.addWidget(self.barrierCombobox)
        layout.addLayout(strikeLayout)
        layout.addLayout(self.upBarrierLayout)
        layout.addLayout(self.downBarrierLayout)

        self.barrierInputStackWidget.setLayout(layout)

    def barrierComboboxClick(self):
        self.barrierCombobox.model().item(0).setEnabled(False)
        if self.barrierCombobox.currentText() == 'DownOut':
            self.upBarrier.setEnabled(False)
            self.downBarrier.setEnabled(True)
            self.barrierType = self.barrierCombobox.currentText()

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        # MainWindow Set
        self.setWindowTitle("BitcoinSystem - Wintom Financial Technology")
        allLayout = QVBoxLayout()
        Width = 1600; Height = 900
        self.resize(Width, Height)
        self.setFixedSize(Width, Height)
        
        # Background figure
        palette = QPalette()
        fig = QPixmap('mainWindowBackground.jpg')
        fig = fig.scaled(self.width(), self.height())
        palette.setBrush(QPalette.Background, QBrush(fig))
        self.setPalette(palette)

        # Start interface
        ## Wellcome message
        wellcomeMessage = QLabel("Bitcoin System")
        wellcomeMessage.setFont(QFont('Consolas', 42))
        wellcomeMessage.setStyleSheet("color: Black;")
        wellcomeMessage.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        wellcomeMessage.setFixedSize(700, 200)
        
        ## Start interface button
        buttonHSize = 500; buttonVSize = 100
        spotButton = QPushButton('Spot Data', self)
        spotButton.clicked.connect(self.slot_spotAction)
        spotButton.setFont(QFont('Consolas', 36))
        spotButton.setFixedSize(buttonHSize, buttonVSize)
        
        optionButton = QPushButton('Option Data', self)
        optionButton.clicked.connect(self.slot_optionAction)
        optionButton.setFont(QFont('Consolas', 36))
        optionButton.setFixedSize(buttonHSize, buttonVSize)
        
        rateButton = QPushButton('Rate Data', self)
        rateButton.clicked.connect(self.slot_rateAction)
        rateButton.setFont(QFont('Consolas', 36))
        rateButton.setFixedSize(buttonHSize, buttonVSize)
        
        optionSimulationButton = QPushButton('Option Simulation', self)
        optionSimulationButton.setFont(QFont('Consolas', 36))
        optionSimulationButton.setFixedSize(buttonHSize, buttonVSize)
        optionSimulationButton.clicked.connect(self.slot_optionSimulationMainWindowAction)
        
        buttonLayout = QGridLayout()
        buttonLayout.addWidget(wellcomeMessage       , 0, 0)
        buttonLayout.addWidget(spotButton            , 1, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        buttonLayout.addWidget(optionButton          , 2, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        buttonLayout.addWidget(rateButton            , 3, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        buttonLayout.addWidget(optionSimulationButton, 4, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        
        ## Copyright text
        copyright = QLabel("Photo by Aleksi Räisä on Unsplash")
        copyright.setFont(QFont('Consolas', 12))
        copyright.setStyleSheet("color: white;")
        copyright.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        ## Start interface Layout
        startInterfaceLayout = QHBoxLayout()
        startInterfaceLayout.addLayout(buttonLayout)
        startInterfaceLayout.addWidget(copyright)
        
        # Stack Layout
        startInterfaceStackWidget = QWidget()
        startInterfaceStackWidget.setLayout(startInterfaceLayout)
        self.spotStackWidget = QWidget()
        self.spotStack()
        self.optionStackWidget = QWidget()
        self.optionStack()
        self.rateStackWidget = QWidget()
        self.rateStack()

        self.mainWindowStack = QStackedWidget()
        self.mainWindowStack.addWidget(startInterfaceStackWidget)
        self.mainWindowStack.addWidget(self.spotStackWidget)
        self.mainWindowStack.addWidget(self.optionStackWidget)
        self.mainWindowStack.addWidget(self.rateStackWidget)
        
        # Main Window
        self.setCentralWidget(self.mainWindowStack)
        self._createActions()
        self._createMenuBar()
        self._connectActions()
    
    def _createMenuBar(self):
        menuBar = self.menuBar()
        
        # System
        systemMenu = menuBar.addMenu("System")
        systemMenu.addAction(self.aboutAction) 
        systemMenu.addSeparator()              
        systemMenu.addAction(self.exitAction)  

        # MarketData
        marketdataMenu = menuBar.addMenu("MarketData")
        marketdataMenu.addAction(self.spotAction)
        marketdataMenu.addAction(self.optionAction)
        marketdataMenu.addAction(self.rateAction)

        # OptionSimulation
        simulationMenu = menuBar.addMenu("OptionSimulation")
        simulationMenu.addAction(self.vanillaAction)
        simulationMenu.addAction(self.digitalAction)
        simulationMenu.addAction(self.barrierAction)
    
    def _createActions(self):
        # System actions
        self.aboutAction = QAction(self)
        self.aboutAction.setText("About")
        self.exitAction = QAction(self)
        self.exitAction.setText("Exit")
        
        # MarketData actions
        self.spotAction = QAction(self)
        self.spotAction.setText("Spot")
        self.optionAction = QAction(self)
        self.optionAction.setText("Option")
        self.rateAction = QAction(self)
        self.rateAction.setText("Rate")
        
        # OptionSimulation actions
        self.vanillaAction = QAction(self)
        self.vanillaAction.setText("Vanilla")
        self.digitalAction = QAction(self)
        self.digitalAction.setText("Digital")
        self.barrierAction = QAction(self)
        self.barrierAction.setText("Barrier")
    
    def _connectActions(self):
        # Connect System actions
        self.aboutAction.triggered.connect(self.slot_aboutAction)
        self.exitAction.triggered.connect(self.slot_exitAction)
        
        # Connect MarketData actions
        self.spotAction.triggered.connect(self.slot_spotAction)
        self.optionAction.triggered.connect(self.slot_optionAction)
        self.rateAction.triggered.connect(self.slot_rateAction)
        
        # Connect OptionSimulation actions
        self.vanillaAction.triggered.connect(self.slot_vanillaAction)
        self.digitalAction.triggered.connect(self.slot_digitalAction)
        self.barrierAction.triggered.connect(self.slot_barrierAction)

    # Slots
    ## System actions
    def slot_aboutAction(self):
        about = AboutForm(self)
        about.show()
    
    def slot_exitAction(self):
        self.centralWidget.setText("Exit Item Selected")
        QApplication.exit(0)
    
    ## MarketData actions
    def slot_spotAction(self):
        self.mainWindowStack.setCurrentIndex(1)
    
    def slot_optionAction(self):
        self.mainWindowStack.setCurrentIndex(2)

    def slot_rateAction(self):
        self.mainWindowStack.setCurrentIndex(3)
    
    ## OptionSimulation actions
    def slot_vanillaAction(self):
        optionSimulation = OptionSimulation(self, defaultWindow = 'Vanilla Option')
        optionSimulation.show()
    
    def slot_digitalAction(self):
        optionSimulation = OptionSimulation(self, defaultWindow = 'Digital Option')
        optionSimulation.show()

    def slot_barrierAction(self):
        optionSimulation = OptionSimulation(self, defaultWindow = 'Barrier Option')
        optionSimulation.show()
    
    def slot_optionSimulationMainWindowAction(self):
        optionSimulation = OptionSimulation(self)
        optionSimulation.show()
    
    def spotStack(self):
        layout = QVBoxLayout()
        
        web = QWebEngineView()
        web.load(QUrl("https://sites.google.com/view/tradingview-bitcoin/bitcoinspotmarketdata"))

        layout.addWidget(web)
        self.spotStackWidget.setLayout(layout)
    
    # Option stack
    ## Option stack window set
    def optionStack(self):
        # Load bitcoin data
        self.df = pd.read_csv('btcOptionsData.csv')
        # Get maturity
        maturity = np.unique(self.df['maturity']).tolist()
        
        # Option imformation
        ## Time imformation
        timeImformation = QLabel('Time: 2022-05-19 01:30') 
        timeImformation.setFixedSize(600, 80)
        timeImformation.setFont(QFont('Consolas', 32))
        timeImformation.setStyleSheet("color: Black")
        timeImformation.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        ## Maturity combobox
        self.maturityCombobox = QComboBox(self)
        self.maturityCombobox.addItems(['Maturity'] + maturity)
        self.maturityCombobox.insertSeparator(1)
        self.maturityCombobox.setFont(QFont('Consolas', 24))
        self.maturityCombobox.setFixedWidth(400)
        self.maturityCombobox.currentIndexChanged.connect(self.maturityComboboxCliked)

        imformationLayout = QHBoxLayout()
        imformationLayout.addWidget(timeImformation)
        imformationLayout.addWidget(self.maturityCombobox)
        
        # Option data table Stack
        ## Default message Layout
        defaultMessage = QLabel('Option Market Data')
        defaultMessage.setFont(QFont('Consolas', 42))
        defaultMessage.setStyleSheet("color: red; background-color: lightyellow; border: 1px solid black;")
        defaultMessage.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        optionDefaultMessageLayout = QGridLayout()
        optionDefaultMessageLayout.addWidget(defaultMessage)
        self.optionDefaultInterface = QWidget()
        self.optionDefaultInterface.setLayout(optionDefaultMessageLayout)
        
        ## Option data table
        self.optionDataTable = QWidget()
        self.optionDataTableStack()
        
        # Combine stack
        self.optionDataTableStackWidget = QStackedWidget()
        self.optionDataTableStackWidget.addWidget(self.optionDefaultInterface)
        self.optionDataTableStackWidget.addWidget(self.optionDataTable)

        layout = QVBoxLayout()
        layout.addLayout(imformationLayout)
        layout.addWidget(self.optionDataTableStackWidget)
        self.optionStackWidget.setLayout(layout)
    
    ## Option maturity combobox cliked
    def maturityComboboxCliked(self):
        # Enable combobox first item
        self.maturityCombobox.model().item(0).setEnabled(False)
        
        # Specific maturity option data
        df_new = self.df.loc[self.df['maturity'] == self.maturityCombobox.currentText()]
        df_new.index = range(len(df_new))
        
        # Input option data
        self.optionTableWidget.setRowCount(len(df_new)//2 + 1)
        header_index = ['bid_iv', 'mark_iv', 'ask_iv', 'best_bid_price', 'mark_price', 'best_ask_price',
                'strike', 'best_ask_price', 'mark_price', 'best_bid_price', 'ask_iv', 'mark_iv', 'bid_iv']
        for i in range(len(df_new)//2):
            for j in range((len(header_index) - 1)//2):
                newCallItem = QTableWidgetItem(str(df_new[header_index[j]][i*2]))
                newCallItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                newCallItem.setFont(QFont('Consolas', 16))
                
                newPutItem = QTableWidgetItem(str(df_new[header_index[j + 7]][i*2 + 1]))
                newPutItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                newPutItem.setFont(QFont('Consolas', 16))
                
                self.optionTableWidget.setItem(i + 1, j, newCallItem)
                self.optionTableWidget.setItem(i + 1, j + 7, newPutItem)
            
            newStrikeItem = QTableWidgetItem(str(df_new['strike'][i*2]))
            newStrikeItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            newStrikeItem.setFont(QFont('Consolas', 16))
            self.optionTableWidget.setItem(i + 1, 6, newStrikeItem)
        
        self.optionDataTableStackWidget.setCurrentIndex(1)
    
    ## Option data table default interface
    def optionDataTableStack(self):
        # Set header
        header = ['IV(Bid)', 'IV(Mark)','IV(Ask)', 'Bid', 'Mark', 'Ask', 'Strike', 'Ask', 'Mark', 'Bid', 'IV(Ask)', 'IV(Mark)', 'IV(Bid)']
        self.optionTableWidget = QTableWidget(1, len(header))
        self.optionTableWidget.setHorizontalHeaderLabels(header)
        
        # Set call and put header
        newItem = QTableWidgetItem('Calls')
        newItem.setFont(QFont('Consolas', 24))
        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.optionTableWidget.setItem(0, 0, newItem)
        
        newItem = QTableWidgetItem('Puts')
        newItem.setFont(QFont('Consolas', 24))
        newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.optionTableWidget.setItem(0, 7, newItem)
        
        self.optionTableWidget.setSpan(0, 0, 1, 6)
        self.optionTableWidget.setSpan(0, 7, 1, 6)
        
        # Set table font
        self.optionTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.optionTableWidget.horizontalHeader().setFont(QFont('Consolas', 16))
        self.optionTableWidget.verticalHeader().setVisible(False)
        self.optionTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.optionTableWidget.verticalHeader().setDefaultSectionSize(50)
        self.optionTableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  
        
        layout = QVBoxLayout()
        layout.addWidget(self.optionTableWidget)
        self.optionDataTable.setLayout(layout)   
    
    # Rate stack
    def rateStack(self):
        # Time imformation
        timeImformation = QLabel('Time: 2021-11-22 01:30') 
        timeImformation.setFixedSize(600, 80)
        timeImformation.setFont(QFont('Consolas', 32))
        timeImformation.setStyleSheet("color: Black")
        timeImformation.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        # Curve type combobox
        self.curveTypeCombobox = QComboBox(self)
        self.curveTypeCombobox.addItems(['Curve Type', 'Zero Curve', 'Discount Curve'])
        self.curveTypeCombobox.insertSeparator(1)
        self.curveTypeCombobox.setFont(QFont('Consolas', 24))
        self.curveTypeCombobox.setFixedWidth(400)
        self.curveTypeCombobox.currentIndexChanged.connect(self.curveTypeComboboxCliked)

        imformationLayout = QHBoxLayout()
        imformationLayout.addWidget(timeImformation)
        imformationLayout.addWidget(self.curveTypeCombobox)
        
        date = ['2021-11-23', '2022-02-23', '2022-05-23', '2022-11-23']
        zeroRate = ['0.0912%', '0.1417%', '0.1790%', '0.3087%']
        
        zeroRateDataTableWidget = QTableWidget(1, len(zeroRate))
        zeroRateDataTableWidget.setHorizontalHeaderLabels(date)
        zeroRateDataTableWidget.setVerticalHeaderLabels(['Risk Free Rate'])
        for i in range(len(zeroRate)):
            newItem = QTableWidgetItem(zeroRate[i])
            newItem.setFont(QFont('Consolas', 24))
            newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            zeroRateDataTableWidget.setItem(0, i, newItem)
            
        zeroRateDataTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        zeroRateDataTableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        zeroRateDataTableWidget.horizontalHeader().setFont(QFont('Consolas', 16))
        zeroRateDataTableWidget.verticalHeader().setFont(QFont('Consolas', 24))
        # zeroRateDataTableWidget.verticalHeader().setVisible(False)
        zeroRateDataTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        zeroRateDataTableWidget.verticalHeader().setDefaultSectionSize(50)
        
        self.figure = plt.figure(figsize = (7, 7))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addLayout(imformationLayout)
        layout.addWidget(zeroRateDataTableWidget)
        layout.addWidget(self.canvas)
        
        # Get Rate data
        self.rateData = HestonModel.RateData()
        
        # reference: https://www.geeksforgeeks.org/how-to-embed-matplotlib-graph-in-pyqt5/
        self.rateStackWidget.setLayout(layout)
    
    def curveTypeComboboxCliked(self):
        self.curveTypeCombobox.model().item(0).setEnabled(False)
        curveType = self.curveTypeCombobox.currentText()
        self.figure.clear()
        if curveType == 'Zero Curve':
            data = self.rateData.getZeroCurve()
        elif curveType == 'Discount Curve':
            data = self.rateData.getDiscountCurve()
        
        ax = self.figure.add_subplot()
        ax.plot(data, '-o', color = 'b')
        ax.xaxis.set_ticks([0,1,2,3,4,5,6,7,8,9,10,11,12]) 
        xlabels = ['2021-11-23', '2021-12-23', '2022-01-23', '2022-02-23', '2022-03-23', '2022-04-23', '2022-05-23', '2022-06-23', '2022-07-23', '2022-08-23', '2022-09-23', '2022-10-23', '2022-11-23']
        ax.set_xticklabels(xlabels, rotation = 45)
        # self.figure.set_size_inches(15, 15)
        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)

    # Create and show the main window
    mainwin = MainWindow()
    mainwin.show()

    # Run the event loop
    sys.exit(app.exec_())