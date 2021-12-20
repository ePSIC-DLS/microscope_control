import os
import datetime
from time import sleep
import time as cpu_time

md='C:/code/merlin-tcp-connection-master_python3'
os.chdir(md)
from connection.MERLIN_connection import *
md='C:/code/merlin-tcp-connection-master_python3'
os.chdir('C:/Users/JEOL/Documents/Python Scripts')
from microscope_parameters import microscope_parameters

from PyJEM import detector

from PyJEM import TEM3

m_scan = TEM3.Scan3()
m_def = TEM3.Def3()
m_det = TEM3.Detector3()
m_eos = TEM3.EOS3()
m_lens = TEM3.Lens3()
m_stage = TEM3.Stage3()
m_nitrogen = TEM3.Nitrogen3()
m_camera = TEM3.Camera3()
m_mds = TEM3.MDS3()

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class merlin_acquisition():
    def __init__(self):
        self.window()
        
    def window(self):
        app = QApplication(sys.argv)
        w = QWidget()
        
        self.zero_defocus = 38942
        
        self.dwell = QComboBox(w)
        self.dwell.setObjectName('dwell')
        self.dwell.addItems(['100', '600', '750', '1000','1300'])
        self.dwell.move(100, 10)
        l_dwell = QLabel(w)
        l_dwell.setText("Dwell time (us)")
        l_dwell.move(10,10)
        
        self.px = QComboBox(w)
        self.px.setObjectName('px')
        self.px.addItems(['64', '128', '256', '512'])
        self.px.move(100, 40)
        l_px = QLabel(w)
        l_px.setText('Scan px')
        l_px.move(10,40)
        
        self.bitdepth = QComboBox(w)
        self.bitdepth.setObjectName('bitdepth')
        self.bitdepth.addItems(['1', '6', '12'])
        self.bitdepth.move(100, 70)
        l_bitdepth = QLabel(w)
        l_bitdepth.setText('Bit depth')
        l_bitdepth.move(10,70)
        
        self.le = QLineEdit(w)
        self.le.setGeometry(100, 100, 70, 20)
        self.le.setObjectName("session")
        self.le.setText("cm28158-1")
        self.le.move(100,100)
        l_session = QLabel(w)
        l_session.setText('Session ID')
        l_session.move(10, 100)
        
        b = QPushButton(w)
        b.setText("Scan")
        b.move(50,190)
        b.clicked.connect(self.start_acquisition)
        
        self.defocus = QSpinBox(w)
        self.defocus.setGeometry(100, 100, 70, 20)
        self.defocus.setObjectName("defocus")
        self.defocus.move(100,160)
        self.defocus.valueChanged.connect(self.change_defocus)
        self.defocus.setRange(-10000,10000)
        l_defocus = QLabel(w)
        l_defocus.setText('Defocus (nm)')
        l_defocus.move(10, 160)
        
        zdf_button = QPushButton(w)
        zdf_button.setText("Set zero defocus")
        zdf_button.move(50,130)
        zdf_button.clicked.connect(self.get_zero_defocus)
        
        w.setWindowTitle("Merlin Acquisition")
        w.show()
        sys.exit(app.exec_())
        
    def get_zero_defocus(self):
        params = microscope_parameters()
        self.zero_defocus = params.objective_lens_value
        self.defocus_per_bit = params.defocus_per_bit

    def change_defocus(self):
        #print('Settin OL fine to:' , int(self.defocus.value()/defocus_per_bit) )
        m_lens.SetOLf(self.zero_defocus+int(self.defocus.value()/self.defocus_per_bit))
        #self.set_magnification()
    
    def set_magnification(self):
        params = microscope_parameters()
        probe_size = 2*self.defocus.value()*params.convergence*10**-9+1*10**-10
        print(probe_size)

    def start_acquisition(self):
        
        session=self.le.text()
        print(session)
        dwell_val= int(self.dwell.currentText())
        px_val = int(self.px.currentText())
        bit_val = int(self.bitdepth.currentText())
        
        #create detector instance for ADF1
        det = detector.Detector(detector.detectors[0])
        #set scan px
        det.set_scanmode(0)
        
        #set scan px
        det.set_imaging_area(Width = px_val, Height = px_val)
        #set exposure time (ms)
        det.set_exposuretime_value(dwell_val)
        #set to spot mode
        det.set_scanmode(1) #0 - fullscan, 1- spot, 3- area
        #beam blank
        m_def.SetBeamBlank(1)
        print('0')
        params = microscope_parameters(self.zero_defocus, px_val)
        
        msg = QMessageBox()
        msg.setText(params.return_message())
        msg.setWindowTitle("Scan Information")
        retval = msg.exec_()
        sleep(0.5)
        print('1')
        
        datetime_base = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = '\\data\\2021\\'+session+'\\Merlin'
        print(save_path)
        params_file_path = 'X:'+ save_path +'\\' + datetime_base +'.hdf'
        print(params_file_path)
        params.write_hdf(params_file_path)
        hostname = '10.182.0.5'
        print('2') 
        
        merlin_cmd = MERLIN_connection(hostname, channel='cmd')
        print('3')       
        data_path = 'X:' + save_path
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        
        merlin_cmd.setValue('NUMFRAMESTOACQUIRE', px_val*px_val)
        merlin_cmd.setValue('COUNTERDEPTH', bit_val)
        merlin_cmd.setValue('CONTINUOUSRW', 1)
        merlin_cmd.setValue('ACQUISITIONTIME', 0.001)
        merlin_cmd.setValue('FILEDIRECTORY', data_path)
        merlin_cmd.setValue('FILENAME', datetime_base+'_data')
        merlin_cmd.setValue('FILEENABLE',1)
        merlin_cmd.startAcq()
        
        sleep(1)
        print('4')
        #unblank beam
        m_def.SetBeamBlank(0)
        #set scan 
        det.set_scanmode(0)
        #sleep(0.1)
        #print('5')()
        #wait for scan to be finished
        scanning = 1
        #set timeout for scanning 
        #delete_TO = 1
        wait_until = (dwell_val/10**6)*(px_val**2)*1.7
        #print('6')
        #not working from here:
        start_time = cpu_time.time()
        #merlin_cmd = MERLIN_connection(hostname, channel='cmd')
        while scanning == 1:
            #print(scanning)
            #print(wait_until)
            #print(cpu_time.time())
            #print(int((merlin_cmd.getVariable('DETECTORSTATUS'))))
            #print(scanning)
            if start_time + wait_until < cpu_time.time():
                scanning = 0
                #print('timeout')
            sleep(0.1)

        #print('scanning done')   
        #merlin_cmd.__del__()
        
        #set to spot mode
        det.set_scanmode(1) #0 - fullscan, 1- spot, 3- area
        #beam blank
        m_def.SetBeamBlank(1)
        
        merlin_cmd.__del__()
        

if __name__ == '__main__':
    
    acq = merlin_acquisition()