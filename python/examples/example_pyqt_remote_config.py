#!/usr/bin/python

#
# Project MOST - Moving Outcomes to Standard Telemedicine Practice
# http://most.crs4.it/
#
# Copyright 2014, CRS4 srl. (http://www.crs4.it/)
# Dual licensed under the MIT or GPL Version 2 licenses.
# See license-GPLv2.txt or license-MIT.txt
#

import sys
import logging
from PyQt4 import QtGui, QtCore  
from PyQt4.QtCore import pyqtSignal

from most.voip.api import VoipLib
from most.voip.constants import VoipEvent, VoipEventType, CallState, ServerState,\
    AccountState

import urllib2
import json

logger = None

class AccountPickerDialog(QtGui.QDialog):
    
    
    def __init__(self,web_address, parent = None):
        super(AccountPickerDialog, self).__init__(parent)
        self.setWindowTitle("Account Selection")
        
        self.js_account_details = None
        self.js_buddies_details = None
        self.selected_account = None
        
        self.web_address = web_address
        self.layout = QtGui.QVBoxLayout(self)

        self.layout.addLayout(self._buildAccountsPanel(self))
        # OK and Cancel buttons
        self.butOk = QtGui.QPushButton('Ok', self)
        self.butCancel = QtGui.QPushButton('Cancel', self)
        hBox1 = QtGui.QHBoxLayout()
        hBox1.setSpacing(5)
        hBox1.addWidget(self.butOk)
        hBox1.addWidget(self.butCancel)
        
        self.layout.addLayout(hBox1)
        self.connect(self.butOk, QtCore.SIGNAL('clicked()'), self.on_ok_clicked);
        self.connect(self.butCancel, QtCore.SIGNAL('clicked()'), self.on_cancel_clicked);
        self.updateAccountsList()

    def on_ok_clicked(self):
        
        selAccounts = self.accountsList.selectedIndexes()
        print "SEl acc:%s" % selAccounts
        if len(selAccounts)>0:
            self.selected_account = self.js_accounts["data"]["accounts"][selAccounts[0].row()]
            print "SELECTED ACCOUNT:%s" % self.selected_account
            self.get_account_details(self.selected_account["uid"])
            self.get_buddies_details(self.selected_account["uid"])
        self.accept()
     
    def get_account_details(self, account_id):
        url = self.web_address + "/voip/accounts/%s/" % account_id
        print "URL:**%s**"  %str(url)
        myAccount_details =  urllib2.urlopen(str(url)).read()
        print "ACCOUNT DETAILS:" + myAccount_details
        self.js_account_details = json.loads(myAccount_details)["data"]["account"]
        return self.js_account_details
    
    def get_buddies_details(self, account_id):
        url = self.web_address + "/voip/buddies/%s/" % account_id
        print "URL:**%s**"  %str(url)
        myBuddies_details =  urllib2.urlopen(str(url)).read()
        print "BUDDIES DETAILS:" + myBuddies_details
        self.js_buddies_details = json.loads(myBuddies_details)["data"]["buddies"]
        return self.js_buddies_details
           
    def on_cancel_clicked(self):
        self.reject()
   
    def updateAccountsList(self):
        url = self.web_address + "/voip/accounts/"
        print "URL:**%s**"  %str(url)
        myAccounts=  urllib2.urlopen(str(url)).read()
        print "ACCOUNTS:" + myAccounts
        self.js_accounts = json.loads(myAccounts)
        for a in self.js_accounts["data"]["accounts"]:
            item = QtGui.QStandardItem(a["name"])
            self.accountsModel.appendRow(item)
        
    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getSelectedAccount(web_address,parent = None):
        dialog = AccountPickerDialog(web_address,parent)
        result = dialog.exec_()
       
        return (dialog.selected_account, dialog.js_account_details, dialog.js_buddies_details, result == QtGui.QDialog.Accepted)
    
    def _buildAccountsPanel(self, cWidget):
        vBox = QtGui.QVBoxLayout()
        vBox.setSpacing(5)
        self.accountsList = QtGui.QListView()
        self.accountsList.setWindowTitle('Buddies')
        #self.buddiesList.setMinimumSize(600, 400)
        
        # Create an empty model for the list's data
        self.accountsModel = QtGui.QStandardItemModel(self.accountsList)
        self.accountsList.setModel(self.accountsModel)
        self.accountsList.show()
        vBox.addWidget(self.accountsList) 
        return vBox
    
    
class MostVoipGUI(QtGui.QMainWindow):
    # pyqt signal for most voip event notifications
    voip_signal = pyqtSignal(object,object,object)
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Most Voip Demo Application')
        self._setup_logger()
        self.selectedAccount = self.selectedAccountDetails = self.selectedAccountBuddies = None
        
        self.voip_signal.connect(self.notify_events)
        
        self.myVoip = VoipLib()
        self._build_GUI()
        self._setupButtonsByVoipState()
        
    def _setup_logger(self):
        global logger
        if not logger:
            logger = logging.getLogger("VoipDemo") #('Voip')
            
            handler = logging.StreamHandler()
    #         rootFormatter = logging.Formatter('%(name)s - %(levelname)s: %(msg)s')
    #         handler.setFormatter(rootFormatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            #print "NUM LOGGER HANDLERS:%s" % len(logger.handlers)
    
    def voip_notify_events(self, voip_event_type,voip_event, params):
        self.voip_signal.emit(voip_event_type,voip_event, params)
    
    def notify_events(self, voip_event_type,voip_event, params):
        msg = "%s: %s" % (voip_event_type,voip_event)
        logger.debug("\n\nEVENT:%s\n\n" % msg)
        self.statusBar().showMessage(msg)
        
        self._update_status_labels()
        self._setupButtonsByVoipState()
        
        if voip_event==VoipEvent.LIB_INITIALIZED:
            self.myVoip.register_account();
        elif voip_event==VoipEvent.ACCOUNT_REGISTERED:
            self._add_buddies()
            self._update_buddy_list()
        elif voip_event_type==VoipEventType.BUDDY_EVENT:
            self._update_buddy_list()
            
        

    def _add_buddies(self):
        if not self.selectedAccountBuddies:
            return
        
        logger.debug("Adding buddies...")
        for b in self.selectedAccountBuddies:
            # the buddy related to the current registered account is not to be included
            if b["extension"]!=self.selectedAccountDetails["extension"]:
                self.myVoip.get_account().add_buddy(b["extension"])
        
    def _update_buddy_list(self):
        buddies = self.myVoip.get_account().get_buddies()
        logger.debug("Update Buddy Model...")
        self.buddiesModel.clear();
        for b in buddies:
            msg = "%s (%s)" % (b.get_extension(), b.get_status_text())
            logger.debug("Appending buddy:%s" % msg)
            item = QtGui.QStandardItem(msg)
            self.buddiesModel.appendRow(item)
        
            
 
    
        
    def get_init_params(self):
         
        self.selectedAccount, self.selectedAccountDetails , self.selectedAccountBuddies,  ok = AccountPickerDialog.getSelectedAccount(self.txtwebServerAddress.text(), self)
        print "SELECTED ACCOUNT:%s -> Data: %s Details:%s" % (ok, self.selectedAccount, str(self.selectedAccountDetails))
        
        if (not ok):
            raise Exception("No Valid Account Configuration Loaded")
        
        voip_params0 = {u'username':   self.selectedAccount["name"], 
                   u'sip_server_pwd': self.selectedAccountDetails["sip_server"]["pwd"],
                   u'sip_server_address':self.selectedAccountDetails["sip_server"]["address"] , #'u'192.168.1.79',  
                   u'sip_server_user': self.selectedAccountDetails["sip_server"]["user"], 
                   u'sip_server_transport' :self.selectedAccountDetails["sip_server"]["transport"],
                   #u'turn_server_address': self.selectedAccountDetails["turn_server"]["address"], 
                   #u'turn_server_user': self.selectedAccountDetails["turn_server"]["user"],
                   #u'turn_server_pwd': self.selectedAccountDetails["turn_server"]["pwd"],
                   u'log_level' : 1,
                   u'debug' : True }   
        print "VOIP CONF DICT:%s" % voip_params0
        return voip_params0
    
   
    def init_voip_lib(self):
        
        print "Called init_voip_lib"
        self.voip_params = self.get_init_params()
        self._update_account_details_info()
        self.myVoip.init_lib(self.voip_params, self.voip_notify_events)

    def _update_account_details_info(self):
        if self.selectedAccount:
            accountInfo = "%s  [SIP USERMAME: %s - SIP SERVER:%s]" % (self.selectedAccount["name"],self.selectedAccountDetails["sip_server"]["user"],self.selectedAccountDetails["sip_server"]["address"] )
            self.labAccountDetails.setText(accountInfo)
        else:
            self.labAccountDetails.setText("N.A")
            

    def _update_status_labels(self):
        self._update_server_state()
        self._update_call_state()
        self._update_account_state()
        
    def _update_server_state(self):
        server_state = self.myVoip.get_server().get_state()
        self.labServerStateInfo.setText(server_state)
        
    def _update_call_state(self):
        call_state = self.myVoip.get_call().get_state()
        self.labCallStateInfo.setText(call_state)
        
    def _update_account_state(self):
        account_state = self.myVoip.get_account().get_state()
        self.labAccountStateInfo.setText(account_state)
        
    def on_buddy_selected(self,item):
        buddies = self.myVoip.get_account().get_buddies()
        buddy_ext = buddies[item.row()].get_extension()
        self.txtExtension.setText(buddy_ext)
        
    def on_make_call_button_clicked(self):
        extension = self.txtExtension.text()
        logger.debug("Making call to %s" % extension)
        self.myVoip.make_call(extension)
    
    def _setupButtonsByVoipState(self):
       #myServerState = self.myVoip.get_server().get_state()
        myAccountState = self.myVoip.get_account().get_state()
        if myAccountState==AccountState.UNREGISTERED:
            self.butMakeCall.setEnabled(False)
            self.butAnswer.setEnabled(False)
            self.butHold.setEnabled(False)
            self.butHangup.setEnabled(False)
            self.butInit.setEnabled(True)
        else:
            myCallState = self.myVoip.get_call().get_state()
            
            if myCallState==CallState.IDLE:
                self.butMakeCall.setEnabled(True)
                self.butAnswer.setEnabled(False)
                self.butHangup.setEnabled(False)
                self.butHold.setEnabled(False)
                
            elif myCallState==CallState.INCOMING:
                self.butMakeCall.setEnabled(False)
                self.butAnswer.setEnabled(True)
                self.butHangup.setEnabled(True)
                self.butHold.setEnabled(False)
                
            elif myCallState==CallState.DIALING:
                self.butMakeCall.setEnabled(False)
                self.butAnswer.setEnabled(False)
                self.butHangup.setEnabled(True)
                self.butHold.setEnabled(False)
                
            elif myCallState==CallState.HOLDING:
                self.butMakeCall.setEnabled(False)
                self.butAnswer.setEnabled(False)
                self.butHangup.setEnabled(True)
                self.butHold.setEnabled(True)
                self.butHold.setText("Unhold")
                
            elif myCallState==CallState.ACTIVE:
                self.butMakeCall.setEnabled(False)
                self.butAnswer.setEnabled(False)
                self.butHangup.setEnabled(True)
                self.butHold.setEnabled(True)
                self.butHold.setText("Hold")
                
    
    def on_hold_toggle_button_clicked(self):
        if (self.myVoip.get_call().get_state()==CallState.ACTIVE):
            self.myVoip.hold_call()
        elif(self.myVoip.get_call().get_state()==CallState.HOLDING):
            self.myVoip.unhold_call()
   
   
    def on_answer_button_clicked(self):
        self.myVoip.answer_call()
        
    def on_hangup_button_clicked(self):
        self.myVoip.hangup_call()
        
    
        
  


# -----------------------------------------------------------------------------
# GUI BUILDING SECTION
# -----------------------------------------------------------------------------
    
    def _build_GUI(self):
        cWidget = QtGui.QWidget(self)
        
        vBox = QtGui.QVBoxLayout()
        vBox.setSpacing(5)
        vBox.addLayout(self._buildAccountDetailsPanel(cWidget))
        vBox.addLayout(self._buildStatesPanel(cWidget))
        vBox.addLayout(self._buildBuddiesPanel(cWidget))
        vBox.addLayout(self._buildMakeCallPanel(cWidget))
        vBox.addLayout(self._buildLoadConfigPanel(cWidget))
        vBox.addLayout(self._buildButtonsPanel(cWidget))
        self.setMinimumWidth(600)
        cWidget.setLayout(vBox)
        self.setCentralWidget(cWidget)
        self.statusBar().showMessage('MostVoip Event Log') # crea una veloce barra di stato
    
    def _buildAccountDetailsPanel(self,cWidget):
        hBox1 = QtGui.QHBoxLayout()
        hBox1.setSpacing(5)
        labAccountDetailsTitle = QtGui.QLabel('Account', cWidget)
        self.labAccountDetails =  QtGui.QLabel('N.A', cWidget)
        hBox1.addWidget(labAccountDetailsTitle)
        hBox1.addWidget(self.labAccountDetails)
        return hBox1
        
    def _buildBuddiesPanel(self, cWidget):
        vBox = QtGui.QVBoxLayout()
        vBox.setSpacing(5)
        self.buddiesList = QtGui.QListView()
        self.buddiesList.setWindowTitle('Buddies')
        self.buddiesList.clicked.connect(self.on_buddy_selected)
        #self.buddiesList.setMinimumSize(600, 400)
        
        # Create an empty model for the list's data
        self.buddiesModel = QtGui.QStandardItemModel(self.buddiesList)
        self.buddiesList.setModel(self.buddiesModel)
        self.buddiesList.show()
        vBox.addWidget(QtGui.QLabel('Buddies', cWidget))
        vBox.addWidget(self.buddiesList) 
        return vBox
    
    def _buildStatesPanel(self,cWidget):
        hBox1 = QtGui.QHBoxLayout()
        hBox1.setSpacing(5)
        labServerState = QtGui.QLabel('Server State', cWidget)
        self.labServerStateInfo =  QtGui.QLabel('N.A', cWidget)
        hBox1.addWidget(labServerState)
        hBox1.addWidget(self.labServerStateInfo)
        
        hBox2 = QtGui.QHBoxLayout()
        hBox2.setSpacing(5)
        labCallState = QtGui.QLabel('Call State', cWidget)
        self.labCallStateInfo =  QtGui.QLabel('N.A', cWidget)
        hBox2.addWidget(labCallState)
        hBox2.addWidget(self.labCallStateInfo)
        
        hBox3 = QtGui.QHBoxLayout()
        hBox3.setSpacing(5)
        labAccountState = QtGui.QLabel('Account State', cWidget)
        self.labAccountStateInfo =  QtGui.QLabel('N.A', cWidget)
        hBox3.addWidget(labAccountState)
        hBox3.addWidget(self.labAccountStateInfo)
        
        
        vBox = QtGui.QVBoxLayout()
        vBox.setSpacing(5)
        
        vBox.addLayout(hBox1)
        vBox.addLayout(hBox2)
        vBox.addLayout(hBox3)
        return vBox
    
    def _buildMakeCallPanel(self,cWidget):
        hBox = QtGui.QHBoxLayout()
        hBox.setSpacing(2)
        self.butMakeCall = QtGui.QPushButton('Make Call', cWidget)
        self.connect(self.butMakeCall, QtCore.SIGNAL('clicked()'), self.on_make_call_button_clicked);
        labExtension = QtGui.QLabel('Extension: ', cWidget)
        self.txtExtension = QtGui.QLineEdit(cWidget)
        hBox.addWidget(labExtension)
        hBox.addWidget(self.txtExtension)
        hBox.addWidget(self.butMakeCall)
        return hBox
    
    def _buildLoadConfigPanel(self,cWidget):
        hBox = QtGui.QHBoxLayout()
        hBox.setSpacing(2)
        labWebServerAddress = QtGui.QLabel('Web Server Address: ', cWidget)
        self.txtwebServerAddress = QtGui.QLineEdit(cWidget)
        self.txtwebServerAddress.setText("http://localhost:8000")
        hBox.addWidget(labWebServerAddress)
        hBox.addWidget(self.txtwebServerAddress)
        return hBox
        
    def _buildButtonsPanel(self,cWidget):
        hBox = QtGui.QHBoxLayout()
        hBox.setSpacing(2)
        self.butInit = QtGui.QPushButton('Init', cWidget)
        self.butAnswer = QtGui.QPushButton('Answer', cWidget)
        
        self.butHold = QtGui.QPushButton('Hold', cWidget)
        #self.butHold.setCheckable(True);
     
        self.butHangup = QtGui.QPushButton('Hangup', cWidget)
        hBox.addWidget(self.butInit)
        hBox.addWidget(self.butAnswer)
        hBox.addWidget(self.butHold)
        hBox.addWidget(self.butHangup)
        
        self.connect(self.butInit, QtCore.SIGNAL('clicked()'), self.init_voip_lib)
        self.connect(self.butHold, QtCore.SIGNAL('clicked()'), self.on_hold_toggle_button_clicked)
        self.connect(self.butAnswer, QtCore.SIGNAL('clicked()'), self.on_answer_button_clicked)
        self.connect(self.butHangup, QtCore.SIGNAL('clicked()'), self.on_hangup_button_clicked)
        
        return hBox
         
 


app = QtGui.QApplication(sys.argv)
main = MostVoipGUI()
main.show()
sys.exit(app.exec_())

