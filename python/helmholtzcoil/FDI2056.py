# -*- coding: utf-8 -*-
"""
Created on 11/01/2013
Versão 1.0
@author: James Citadini
"""
# Importa bibliotecas
import serial
import time
import threading
# ******************************************

class SerialCom(object):
    def __init__(self,porta):
        self.Ganho_Amplificador = 100
        self.ConversaoPDI = 10E-8
        self.porta = porta
        self.ser = serial.Serial(self.porta-1)

    def run(self):
        self.Comandos()
        
     def Comandos(self):
        CR = '\r'

        #Biblioteca Integrador
        self.PDIProcuraIndice    = 'IND,+'       #Habilita a procura de indice do integrador
        self.PDIIniciaColeta     = 'RUN'         #Inicia coleta com o integrador
        self.PDIParaColeta       = 'BRK'         #Para coleta com o integrador
        self.PDILerStatus        = 'STB,'        #Le status do integrador
        self.PDIBuscaResultados  = 'ENQ'         #Busca Resultados do integrador
        self.PDIEscolheCanal     = 'CHA,A'       #Escolha de Canal
        self.PDIConfiguraGanho   = 'SGA,A,'      #Configura ganho integrador
        self.PDIClearStatus      = 'CRV,A'       #Limpa Saturacao
        self.PDITipodeTrigger    = 'TRS,E,'      #Tipo de Trigger
        self.PDISequenciaTrigger = 'TRI,-,'      #Sequencia Trigger
        self.PDIArmazenaBloco    = 'IMD,0,T'     #Configura Dados para serem armazenados em blocos
        self.PDIArmazena         = 'CUM,0'       #Configura Dados para serem armazenados
        self.PDIZerarContador    = 'ZCT'         #Zerar contador de pulsos
        self.PDIEndofData        = 'EOD'         #End of Data
        self.PDISincroniza       = 'SYN,1'       #Sincroniza
        self.PDICurtoCircuito    = 'ADJ,A,1'     #Curto Integrador
        self.PDILerEncoder       = 'RCT'         #Leitura Pulso Encoder
        self.PDIEnquiry          = 'ENQ'         #Requisitar Resultados
        self.PDIResolutionSet    = 'FCT,1E12'    #Configurar Resoluação 1E12
        
    def Conectar(self):
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.parity = serial.PARITY_NONE
        self.ser.timeout = 0.01
        if not self.ser.isOpen():
            self.ser.open()
            
    def Desconectar(self):
        self.ser.close()
        
    def LimpaTxRx(self):
        self.ser.flushInput()
        self.ser.flushOutput()

    def Enviar(self,comando):
        self.LimpaTxRx()
        ajuste = comando + '\r'
        self.ser.write(ajuste.encode('utf-8'))

    def Ler(self,n):
        try:
            leitura = self.ser.read(n)
            leitura = leitura.decode('utf-8')
            leitura = leitura.replace('\r\n','')
        except:
            leitura = ''

        return leitura

    def Status(self,registrador):
        self.Enviar(self.PDILerStatus + registrador)
        time.sleep(0.1)
        leitura = self.Ler(10)
        return leitura
        
 
