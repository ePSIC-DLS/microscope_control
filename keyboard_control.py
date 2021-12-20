# -*- coding: utf-8 -*-
"""
Created on Mon May 18 11:23:17 2020

@author: Tom Slater
"""

from pynput import keyboard, mouse
from PyJEM import TEM3
m_stage = TEM3.Stage3()

import time
import threading

class keyboard_controller(object):
    
    def __init__(self):
        print("Starting keyboard control of microscope, press Esc to exit.")
        self.keydown = False
        self.speed = 100
        self.f_strength = 1
        self.init_controls()
        self.a = 'test'

    def on_press(self, keyname):
        """handler for keyboard listener"""
        if self.keydown:
            return
        try:
            self.keydown = True
            keyname = str(keyname).strip('\'')
            #print('+' + keyname)
            if keyname == 'Key.esc':
                print('Exiting Keyboard Control')
                raise SystemExit()
            if keyname in self.stage_controls:
                command = self.stage_controls[keyname]
                self.execute_command(command,self.speed)
            elif keyname in self.focus_controls:
                command = self.focus_controls[keyname]
                self.execute_command(command,self.f_strength)
        except AttributeError:
            print('special key {0} pressed'.format(keyname))
    
    def on_release(self, keyname):
        """Reset on key up from keyboard listener"""
        self.keydown = False
        keyname = str(keyname).strip('\'')
        #print('-' + keyname)
        if keyname in self.stage_controls:
            key_handler = self.stage_controls[keyname]
            #self.thread._stop()
            #else:
                #key_handler(self,self.speed)
            
    def on_scroll(self,x,y,dx,dy):
        print(str(dy))
    
    def init_controls(self):
        """Define keys and add listener"""
        self.stage_controls = {
            'Key.left': self.move_left,
            'Key.right': self.move_right,
            'Key.up': self.move_up,
            'Key.down': self.move_down,
            'p': self.piezo_switch,
            'm': self.speed_up,
            'n': self.speed_down
        }
        self.focus_controls = {
            'f': self.change_foucs
        }
        self.key_listener = keyboard.Listener(on_press=self.on_press,
                                              on_release=self.on_release)
        self.key_listener.start()
        # self.key_listener.join()
    
    def start_mouse_listener(self):
        self.mouse_listener = mouse.Listener(on_scroll=self.on_scroll)
        self.mouse_listener.start()
    
    def execute_command(self, target, speed):
        self.thread = threading.Thread(target=target, args=(speed,))
        self.thread.daemon = True
        self.thread.start() 
        
    def move_left(self, speed):
        while self.keydown==True:
            m_stage.SetXRel(-speed)
            time.sleep(0.1)
    
    def move_right(self, speed):
        while self.keydown==True:
            m_stage.SetXRel(speed)
            time.sleep(0.1)
    
    def move_up(self, speed):
        while self.keydown==True:
            m_stage.SetYRel(speed)
            time.sleep(0.1)
    
    def move_down(self, speed):
        while self.keydown==True:
            m_stage.SetYRel(-speed)
            time.sleep(0.1)
    
    def piezo_switch(self, speed):
        drv_mode = m_stage.GetDrvMode()
        
        if drv_mode == 0:
            self.speed = 0.1
            m_stage.SelDrvMode(1)
        if drv_mode == 1:
            self.speed = 10
            m_stage.SelDrvMode(0)
    
    def speed_up(self, speed):
        self.speed = speed*10
    
    def speed_down(self, speed):
        self.speed = speed/10
    
    def change_focus(self, strength):
        while self.keydown==True:
            self.start_mouse_listener()
            
        
if __name__ == "__main__":
    controller = keyboard_controller()