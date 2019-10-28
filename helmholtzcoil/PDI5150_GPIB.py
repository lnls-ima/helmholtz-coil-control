# -*- coding: utf-8 -*-
"""
Created on 21/05/2014
Versão 1.0
@author: James Citadini
"""
# Importa bibliotecas
import visa
import time
# ******************************************

class GPIBCom(object):
    def __init__(self,address):
        try:
            self.Ganho_Amplificador = 100
            self.ConversaoPDI = 1E-8
            self.Comandos()
            
            aux = 'GPIB::'+str(address)
            self.inst = visa.instrument(aux.encode('utf-8'))
            self.inst.timeout = 1
        except:
            return None

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
        self.PDIArmazenaBloco    = 'IMD,1'       #Configura Dados para serem armazenados em blocos
        self.PDIArmazena         = 'CUM,0'       #Configura Dados para serem armazenados
        self.PDIZerarContador    = 'ZCT'         #Zerar contador de pulsos
        self.PDIEndofData        = 'EOD'         #End of Data
        self.PDISincroniza       = 'SYN,1'       #Sincroniza
        self.PDICurtoCircuitoON  = 'ADJ,A,1'     #Curto Integrador
        self.PDICurtoCircuitoOFF = 'ADJ,A,0'     #Curto Integrador
        self.PDILerEncoder       = 'RCT'         #Leitura Pulso Encoder
        self.PDIEnquiry          = 'ENQ'         #Requisitar Resultados
        self.PDIResolutionSet    = 'FCT,1E12'    #Configurar Resoluação 1E12
        self.PDISincroniza       = 'SYN,1'       #Configurar Resoluação 1E12
        
    def Enviar(self,comando):
        try:
            self.inst.write(comando)
            return True
        except:
            return False

    def Ler(self):
        try:
            leitura = self.inst.read()
##            leitura = self.inst.read_values()
        except:
            leitura = ''

        return leitura

    def Status(self,registrador):
        self.Enviar(self.PDILerStatus + registrador)
        time.sleep(0.1)
        leitura = self.Ler()
        return leitura
