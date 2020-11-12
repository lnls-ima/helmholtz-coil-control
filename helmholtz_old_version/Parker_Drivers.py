# -*- coding: utf-8 -*-
"""
Created on 03/07/2013
Versão 3.0
@author: James Citadini
"""
# Importa bibliotecas
import serial
import ctypes
import time
# ******************************************

class SerialCom(object):
    def __init__(self,porta):
        self.porta = porta
        self.ser = serial.Serial(self.porta-1)
        self.Comandos()
        
    def Comandos(self):
        try:
            self.Mover  = 'G' # {Comando para mover motor}
            self.Parar  = 'S' # {Comando para parar motor}
            self.Dist   = 'D' # {Comando para parar motor}
            self.Vel    = 'V' # {Velocidade motor}
            self.Ace    = 'A' # {Aceleração motor}
            self.status = 'R' # {Status motor}
            self.modocont = 'MC' # {Modo Contínuo motor}
            self.modomanual = 'MN' # {Modo Manual motor}
            self.resolucao = 'MR' # Resolução do motor
            self.sentido = 'H' # {Sentido do motor}
            self.FimdeCurso_Off = 'LD3' # {Desabilita Fim de Curso}
            self.HabilitaSaidaDigital = 'O10' #Aciona Saída Digital
            self.DesabilitaSaidaDigital = 'O00' #Desabilita Saída Digital
            return True
        except:
            return False
        
    def Conectar(self):
        try:
            self.ser.baudrate = 9600
            self.ser.bytesize = serial.EIGHTBITS
            self.ser.stopbits = serial.STOPBITS_ONE
            self.ser.parity = serial.PARITY_NONE
            self.ser.timeout = 0.01
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
        ajuste = str(comando) + '\r'
        self.ser.write(ajuste.encode('utf-8'))

    def ConfModo(self,EndDriver,Modo,Sentido):
        try:
            self.LimpaTxRx()
            # Ajusta Modo Manual ou Cotinuo
            if ((Modo == 0) or (Modo == 'Manual')):
                ajuste = str(EndDriver) + self.modomanual + '\r'
            elif ((Modo == 1) or (Modo == 'Continuo')):
                ajuste = str(EndDriver) + self.modocont + '\r'

            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)

            # Ajusta Sentido
            if ((Sentido == 0) or (Sentido == 'Horario')):
                ajuste = str(EndDriver) + self.sentido + '+\r'
            elif ((Sentido == 1) or (Sentido == 'AntiHorario')):
                ajuste = str(EndDriver) + self.sentido + '\r'

            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)
            return True
        except:
            return False
            
    def ConfMotor(self,EndDriver,Vel,Ace,Passos):
        try:
            self.LimpaTxRx()

            ajuste = str(EndDriver) + self.resolucao + str(50000) + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)
            
            # Configura Driver
            ajuste = str(EndDriver) + self.Vel + str(Vel) + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)
            
            ajuste = str(EndDriver) + self.Ace + str(Ace) + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)

            ajuste = str(EndDriver) + self.Dist + str(Passos) + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)
            return True
        except:
            return False

    def MoverMotorFimdeCursoPos(self,EndDriver,Vel=1,Ace=1):
        try:
            # Move Fim de Curso Positivo
            self.LimpaTxRx()        
            ajuste = str(int(EndDriver)) + int(self.Vel) + str(int(Vel)) + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)
            
            ajuste = str(EndDriver) + self.Ace + str(Ace) + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)

            ajuste = str(EndDriver) + self.modocont + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)

            ajuste = str(EndDriver) + self.sentido + '+\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)

            self.MoverMotor(EndDriver)
            return True
        except:
            return False

    def MoverMotorFimdeCursoNeg(self,EndDriver,Vel=1,Ace=1):
        try:
            # Move Fim de Curso Nagativo
            self.LimpaTxRx()        
            ajuste = str(EndDriver) + self.Vel + str(Vel) + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)
            
            ajuste = str(EndDriver) + self.Ace + str(Ace) + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)

            ajuste = str(EndDriver) + self.modocont + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)

            ajuste = str(EndDriver) + self.sentido + '-\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)

            self.MoverMotor(EndDriver)
            return True
        except:
            return False

    def PararMotor(self,EndDriver):
        try:
            self.LimpaTxRx()
            # Para o motor
            ajuste = str(EndDriver) + self.Parar + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)
            return True
        except:
            return False

    def MoverMotor(self,EndDriver):
        try:
            self.LimpaTxRx()
            # Mover o motor n passos
            ajuste = str(EndDriver) + self.Mover + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            leitura = self.ser.read(100)
            return True
        except:
            return False

    def ready(self,EndDriver):
        try:
            self.LimpaTxRx()
            ajuste = str(int(EndDriver)) + self.status + '\r'
            self.ser.write(ajuste.encode('utf-8'))
            time.sleep(0.01)
            leitura = str(self.ser.read(100))
            if ((leitura.find('*R') >= 0) or (leitura.find('*S') >= 0)):
                return True
            else:
                return False
        except:
            return False
