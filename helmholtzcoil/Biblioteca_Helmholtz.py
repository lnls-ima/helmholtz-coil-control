# -*- coding: utf-8 -*-
"""
Created on 13/01/2013
Versão 1.0
@author: James Citadini
"""
# Importa bibliotecas
import time
import Parker_Drivers as Parker
import Display_Heidenhain as Heidenhain
import PDI5150_GPIB
import Agilent34401A as Agilent
import numpy as np

from PyQt4 import QtCore, QtGui
# ******************************************

# Parâmetros
class Parametros(object):
    def __init__(self):
        self.NomeRegistro = np.array([])
        self.ValorRegistro = np.array([])   

        self.DictPar = {}

class Variaveis(object):
    def __init__(self):
        self.Dados = np.array([])
        self.Dados_Media = np.array([])
        self.Dados_Desvio = np.array([])

        self.MagNormalMedia = 0
        self.MagNormalDesvio = 0
        self.MagSkewMedia = 0
        self.MagSkewDesvio = 0


class Bib(object):
    def __init__(self):
        self.Par = Parametros()

        self.Var = Variaveis()

        self.IntDic = {-1:-1,0:4,1:8,2:16,3:32,4:64,5:128,6:256,7:512}
        
        self.Drivers = None
        self.Display = None
        self.Integrador = None
        self.Multimetro = None
        self.PararTudo = False

    def ConectaDispositivos(self):
        try:
            # Configura Porta e Conecta Drivers
            self.Drivers = Parker.SerialCom(int(self.Par.DictPar['Porta Driver']) + 1)
            self.Drivers.Conectar()
        except:
            print('erro driver')
    
        try:
            # Configura e Conecta Display
            self.Display = Heidenhain.SerialCom(int(self.Par.DictPar['Porta Display']) + 1)
            self.Display.Conectar()
        except:
            print('erro display')

        try:
            # Configura Porta e Conecta Multimetro
            self.Multimetro = Agilent.SerialCom(int(self.Par.DictPar['Porta Multimetro']) + 1)
            self.Multimetro.Conectar()
        except:
            print('erro multimetro') 

        try:
            # Configura e Conecta Integrador
            self.Integrador = PDI5150_GPIB.GPIBCom(int(self.Par.DictPar['End Integrador']))
            return True
        except:
            print('erro integrador')

    def DesconectaDispositivos(self):
        try:
            self.Drivers.Desconectar()
            self.Display.Desconectar()
            self.Multimetro.Desconectar()
            return True
        except:
            return False

    def CarregaRegistro(self):
        self.Par.NomeRegistro = np.array([])
        self.Par.ValorRegistro = np.array([])
        try:
            f = open('BiblioPar.dat')
            dados = f.readline()
            i = 0
            while (dados != 'END'):
                dados = f.readline()
                if (dados != '\n') and (dados !='END'):
                    nome = dados.split('\t')[0]
                    valor = dados.split('\t')[1].split('\n')[0]
                    
                    self.Par.NomeRegistro = np.append(self.Par.NomeRegistro,nome)
                    self.Par.ValorRegistro = np.append(self.Par.ValorRegistro,valor)
            f.close()
            
            self.Par.DictPar = dict(zip(self.Par.NomeRegistro,self.Par.ValorRegistro))
            
        except:
            print ('Falha ao abrir os parâmetros')
            
    def SalvaRegistro(self):
        try:
            self.Par.NomeRegistro = np.array([])
            self.Par.ValorRegistro = np.array([])

            for key,val in sorted(self.Par.DictPar.items()):
                self.Par.NomeRegistro = np.append(self.Par.NomeRegistro,key)
                self.Par.ValorRegistro = np.append(self.Par.ValorRegistro,val)
            
            f = open('BiblioPar.dat','w')
            f.writelines('Biblioteca de Parâmetros Helmholtz\n')
            f.writelines('\n')
            for i in range(self.Par.NomeRegistro.size):
                f.writelines(self.Par.NomeRegistro[i]+'\t'+self.Par.ValorRegistro[i]+'\n')

            f.writelines('\n')
            f.writelines('END')
            f.close()
        except:
            print ('Falha ao salvar os parâmetros')

    def set_item(self,lin,col,Text):
        item = QtGui.QTableWidgetItem()
        self.App.myapp.ui.tw_GanhosOffsets.setItem(lin, col, item)
        item.setText(Text)

    def TesteVar(self,strvar,minimo,maximo):
        try:
            valor = float(strvar)
            if ( (valor >= minimo) and (valor <= maximo) ):
                return valor,True
            else:
                return 0,False
        except:
            return 0,False

##    def Temperatura(self):
##        self.Multimetro.Enviar(self.Multimetro.)

    def Configurar_Integrador(self,ganho,nvoltas):
        tempoespera = 0.1

        # Configurar Resolução
        self.Integrador.Enviar(self.Integrador.PDIResolutionSet)
        time.sleep(tempoespera)
        
        # Cálculo do intervalo de integração
        IntervaloIntegrador = int( float(self.Par.DictPar['Pulsos Encoder']) / float(self.Par.DictPar['Pontos Integracao']) )

        # Parar todas as coletas e preparar integrador
        self.Integrador.Enviar(self.Integrador.PDIParaColeta)
        time.sleep(tempoespera)

##        # Configurar Canal a ser utilizado - Fixo no canal A
##        self.Integrador.Enviar(self.Integrador.PDIEscolheCanal)
##        time.sleep(tempoespera)

        # Configurar Tipo de encoder e n pulsos
        self.Integrador.Enviar(self.Integrador.PDITipodeTrigger + str(int(float(self.Par.DictPar['Pulsos Encoder'])/4)))
        time.sleep(tempoespera)

        # Configurar intervalo e direção do trigger
        ajuste = self.Integrador.PDISequenciaTrigger + \
                               str(int(float((self.Par.DictPar['Pulsos para Trigger'])))) + '/' + \
                               str(int(float(self.Par.DictPar['Pontos Integracao'])*float(nvoltas))) + ',' + \
                               str(IntervaloIntegrador)

        self.Integrador.Enviar(ajuste)
        time.sleep(tempoespera)

        # Configurar para armazenamento em bloco
        self.Integrador.Enviar(self.Integrador.PDIArmazenaBloco)
        time.sleep(tempoespera)

        # Preparar para armazenamento
        self.Integrador.Enviar(self.Integrador.PDIArmazena)
        time.sleep(tempoespera)

        # Configurar End of Data
        self.Integrador.Enviar(self.Integrador.PDIEndofData)
        time.sleep(tempoespera)

        # Parar todas as coletas e preparar integrador
        self.Integrador.Enviar(str(self.Integrador.PDIConfiguraGanho + ganho))
        time.sleep(tempoespera)

    class VarDados(object):
        def __init__(self):
            self.StringDados = np.array([])
            self.StringFFT = np.array([])

            self.Alfa        = 0
            self.Beta        = 0
            self.Modulo      = 0

            self.MagNormal   = 0
            self.MagSkew     = 0

            self.SAN     = np.array([])
            self.SBN     = np.array([])
            self.SSAN2   = np.array([])
            self.SSBN2   = np.array([])
            self.SDBDXN  = np.array([])
            self.SDBDXN2 = np.array([])
            self.Smodulo = np.array([])
            self.Angulo  = np.array([])
##            self.PulsosEncoder = np.array([])
            self.PulsosEncoder = []
            
            self.CoefDipA = 0
            self.CoefDipB = 0

            self.Identificacao = 0
            self.Temperatura = []
            
