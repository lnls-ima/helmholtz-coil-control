# -*- encoding: utf-8 -*-
"""
Created on 05/09/2013
Versão 1.0
@author: Lídia Florenziano
"""

import serial
import ctypes
import time

class SerialCom(object):
    def __init__(self,porta): 
        self.porta = porta
        self.ser = serial.Serial(self.porta-1)
        self.Comandos()

    def Comandos(self):
        self.ler             = 'READ?'                                  #ler
        self.conectar        = 'SYST:REM'                               #conecta
        self.limpacomando    = '*CLS'                                   #limpar comando
        self.reset           = '*RST'                                   #reseta multimetro

        self.conftemperatura = 'CONF:RES 100,0.0001'
        self.configuratensao = ['CONF:VOLT:DC 10,0.001\r\n',\
                                'CONF:VOLT:DC 10,0.0001\r\n',\
                                'CONF:VOLT:DC 10,0.00003\r\n',\
                                'CONF:VOLT:DC 10,0.00001\r\n',\
                                'CONF:VOLT:DC 10,0.000003\r\n']             #configura tensão
        self.erromedicao     = 'DISP:TEXT Erro!! Verifique as medidas\r\n'  #escreve erro no display
        self.limpadisplay    = 'DISP:TEXT:CLE\r\n'                          #limpa mensagem de erro display
        self.testa           = '*TST?\r\n'                                  #testa multimetro
        self.espera          = 0.5                                          #espera medidas      
        self.MediaTemp       = 0                                            #media das temperaturas
        self.resistenciacabo = 0.8202
        
        self.delays          = {'0.02':25,\
                                '0.2':30,\
                                '1':60,\
                                '10':400,\
                                '100':3400}                                 #delays

    def Conectar(self):
        try:
            self.ser.baudrate = 9600
            self.ser.bytesize = serial.EIGHTBITS
            self.ser.stopbits = serial.STOPBITS_ONE
            self.ser.parity = serial.PARITY_NONE
            self.ser.timeout = 0.2
            if not self.ser.isOpen():
                self.ser.open()
            return True
        except:
            return False

    def Desconectar(self):
        try:
            self.ser.close()
            return True
        except:
            return False

    def LimpaTxRx(self):
        try:
            self.ser.flushInput()
            self.ser.flushOutput()
            return True
        except:
            return False

    def Enviar(self,comando):
        self.LimpaTxRx()
        ajuste = comando + '\r\n'
        self.ser.write(ajuste.encode('utf-8'))

    def Ler(self):
        try:
            valor = self.ser.read(255)
            valor = valor.decode('utf-8')
            valor = valor.replace('\r\n','')
        except:
            valor = ''
        return valor

    def Status(self,registrador):
        self.Enviar(self.ler)
        time.sleep(0.5)
        resp = self.Ler(20)
        return resp

    

        
    
        
    
    

                  
  


