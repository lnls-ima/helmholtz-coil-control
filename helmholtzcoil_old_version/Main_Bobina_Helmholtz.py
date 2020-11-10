# -*- coding: utf-8 -*-
"""
Created on 14/06/2014
Versão 3.0
@author: James Citadini

Versão 4.0
@author: Lídia Florenziano
"""
# Importa bibliotecas
import time
import datetime
import math
import Biblioteca_Helmholtz as Biblioteca
import threading
import numpy as np
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random

from PyQt5 import QtCore, QtWidgets as QtCore, QtGui
from Interface_Helmholtz import *
import sys
import traceback

class Principal(QtGui.QMainWindow):
    def __init__(self, parent=None):
        # Inicializa Interface
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Helmholtz()
        self.ui.setupUi(self)

        self.ui.tabWidget.setTabEnabled(0,True)
        for i in range(1,8):
            self.ui.tabWidget.setTabEnabled(i,False)

        QtCore.QObject.connect(self.ui.pb_ConectarDispositivos,QtCore.SIGNAL("clicked()"), self.Conectar) # -> ok
        QtCore.QObject.connect(self.ui.cb_PortaDisplay,QtCore.SIGNAL("activated(const QString&)"), self.Port_change) # -> ok
        QtCore.QObject.connect(self.ui.cb_PortaDriver,QtCore.SIGNAL("activated(const QString&)"), self.Port_change) # -> ok
        QtCore.QObject.connect(self.ui.le_EndIntegrador,QtCore.SIGNAL("activated(const QString&)"), self.Port_change) # -> ok

        QtCore.QObject.connect(self.ui.pb_SalvarParametros,QtCore.SIGNAL("clicked()"), self.Par_Check_Change) # -> ok
        QtCore.QObject.connect(self.ui.pb_SalvarBobina,QtCore.SIGNAL("clicked()"), self.Bobina_Check_Change) # -> ok

        QtCore.QObject.connect(self.ui.le_VelMotor,QtCore.SIGNAL("editingFinished()"), self.Motores_Change) # -> ok
        QtCore.QObject.connect(self.ui.le_AceMotor,QtCore.SIGNAL("editingFinished()"), self.Motores_Change) # -> ok
        QtCore.QObject.connect(self.ui.le_NVoltasMotor,QtCore.SIGNAL("editingFinished()"), self.Motores_Change) # -> ok

        QtCore.QObject.connect(self.ui.cb_HabilitaEncoder,QtCore.SIGNAL("clicked()"), self.HabilitaLeituraEncoder) # -> ok
        QtCore.QObject.connect(self.ui.pb_MoverMotor,QtCore.SIGNAL("clicked()"), self.MoverMotor_Manual) # -> ok
        QtCore.QObject.connect(self.ui.pb_PararMotor,QtCore.SIGNAL("clicked()"), self.PararMotor) # -> ok

        QtCore.QObject.connect(self.ui.le_NVoltasOffset,QtCore.SIGNAL("editingFinished()"), self.NVoltasOffset_change) # -> ok
        QtCore.QObject.connect(self.ui.pb_AjusteOffset,QtCore.SIGNAL("clicked()"), self.AjusteOffsetIntegrador) # -> ok
        QtCore.QObject.connect(self.ui.pb_IniciarMedOffset,QtCore.SIGNAL("clicked()"), self.IniciarMedidaOffset) # -> ok
        QtCore.QObject.connect(self.ui.pb_PararMedOffset,QtCore.SIGNAL("clicked()"), self.PararMedidaOffset) # -> ok
        QtCore.QObject.connect(self.ui.pb_ZerarOffsets,QtCore.SIGNAL("clicked()"), self.ZerarOffsets) # -> ok

        QtCore.QObject.connect(self.ui.le_VolumeBloco,QtCore.SIGNAL("editingFinished()"), self.Manual) # -> ok
        QtCore.QObject.connect(self.ui.le_NVoltasOffset,QtCore.SIGNAL("editingFinished()"), self.NVoltasOffset_change)

        QtCore.QObject.connect(self.ui.le_VolumeSubtracao,QtCore.SIGNAL("editingFinished()"), self.VolumeSubtracao_change) # -> ok
        QtCore.QObject.connect(self.ui.rb_DimensaoManual,QtCore.SIGNAL("clicked()"), self.DimensoesBloco) # -> ok
        QtCore.QObject.connect(self.ui.rb_DimensaoAuto,QtCore.SIGNAL("clicked()"), self.DimensoesBloco) # -> ok
        QtCore.QObject.connect(self.ui.pb_IniciarMedicao,QtCore.SIGNAL("clicked()"), self.IniciarMedicao)
        QtCore.QObject.connect(self.ui.pb_PararMedicao,QtCore.SIGNAL("clicked()"), self.PararMedicao) # -> ok

        QtCore.QObject.connect(self.ui.pb_IniciaColeta,QtCore.SIGNAL("clicked()"), self.Medida_Temperatura)
        QtCore.QObject.connect(self.ui.pb_PararColeta,QtCore.SIGNAL("clicked()"), self.PararMultimetro)
       
    def Conectar(self):
        if (self.ui.pb_ConectarDispositivos.text() == 'Conectar Dispositivos'):

            if Bib.ConectaDispositivos() == True:
                for i in range(1,7):
                    self.ui.tabWidget.setTabEnabled(i,True)

                self.ui.cb_PortaDisplay.setEnabled(False)
                self.ui.cb_PortaDriver.setEnabled(False)
                self.ui.le_EndIntegrador.setEnabled(False)
                self.ui.cb_PortaMultimetro.setEnabled(False)

                self.Port_change()

                self.ui.pb_ConectarDispositivos.setText('Desconectar Dispositivos')
                self.ui.pb_ConectarDispositivos.setStatusTip('Desconecta Dispositivos')
            else:
                QtGui.QMessageBox.warning(self,'Falha de Conexão','Falha na Conexão com os Dispositivos',QtGui.QMessageBox.Ok)
        else:
            Bib.DesconectaDispositivos()

            for i in range(1,8):
                self.ui.tabWidget.setTabEnabled(i,False)

            self.ui.cb_PortaDisplay.setEnabled(True)
            self.ui.cb_PortaDriver.setEnabled(True)
            self.ui.le_EndIntegrador.setEnabled(True)
            self.ui.cb_PortaMultimetro.setEnabled(True)
            
            self.ui.pb_ConectarDispositivos.setText('Conectar Dispositivos')

    def Port_change(self):
        Bib.Par.DictPar['Porta Display'] = self.ui.cb_PortaDisplay.currentIndex()
        Bib.Par.DictPar['Porta Driver'] = self.ui.cb_PortaDriver.currentIndex()
        Bib.Par.DictPar['Porta Integrador'] = int(self.ui.le_EndIntegrador.text())
        Bib.Par.DictPar['Porta Multimetro'] = self.ui.cb_PortaMultimetro.currentIndex()
        self.AtualizaTela()
        Bib.SalvaRegistro()

    def Par_Check_Change(self):
        Falha = False
        
        # Endereco Driver
        strvar = self.ui.le_EndDriver.text()
        valor,status = Bib.TesteVar(strvar,1,8)
        if status == True:
            Bib.Par.DictPar['Endereco Driver'] = valor
        else:
            Falha = True

        # Velocidade Medida
        strvar = self.ui.le_VelMedida.text()
        valor,status = Bib.TesteVar(strvar,0.1,5)
        if status == True:
            Bib.Par.DictPar['Velocidade Medida'] = valor
        else:
            Falha = True

        # Aceleracao Medida
        strvar = self.ui.le_AceMedida.text()
        valor,status = Bib.TesteVar(strvar,1,10)
        if status == True:
            Bib.Par.DictPar['Aceleracao Medida'] = valor
        else:
            Falha = True

        # #Voltas Medida
        strvar = self.ui.le_NVoltas.text()
        valor,status = Bib.TesteVar(strvar,1,100)
        if status == True:
            Bib.Par.DictPar['#Voltas Medida'] = valor            
        else:
            Falha = True

        # Pulsos Encoder
        strvar = self.ui.le_PulsosEncoder.text()
        valor,status = Bib.TesteVar(strvar,128,20000)
        if status == True:
            Bib.Par.DictPar['Pulsos Encoder'] = valor            
        else:
            Falha = True

        # Passos Motor
        strvar = self.ui.le_PassosMotor.text()
        valor,status = Bib.TesteVar(strvar,-50000,50000)
        if status == True:
            Bib.Par.DictPar['Passos Motor'] = valor
        else:
            Falha = True

        # Pontos Integracao
        Bib.Par.DictPar['Pontos Integracao'] = Bib.IntDic[self.ui.cb_PontosIntegracao.currentIndex()]

        # Pulsos para Trigger
        strvar = self.ui.le_TriggerAlinhamento.text()
        valor,status = Bib.TesteVar(strvar,0,4095)
        if status == True:
            Bib.Par.DictPar['Pulsos para Trigger'] = valor              
        else:
            Falha = True

        self.AtualizaTela()
        Bib.SalvaRegistro()

        if Falha == False:
            QtGui.QMessageBox.warning(self,'Sucesso','Ajustes atualizados com sucesso',QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.warning(self,'Falha nos dados','Um ou mais parâmetros não foram ajustados corretamente, favor verificar limites e caracteres',QtGui.QMessageBox.Ok)

    def AtualizaTela(self):
        # Tela Bobina de Helmholtz
        self.ui.cb_PortaDriver.setCurrentIndex(int(Bib.Par.DictPar['Porta Driver']))
        self.ui.cb_PortaDisplay.setCurrentIndex(int(Bib.Par.DictPar['Porta Display']))
        self.ui.le_EndIntegrador.setText(str(Bib.Par.DictPar['End Integrador']))
        
        # Tela Parametros
        self.ui.le_EndDriver.setText('{0:0d}'.format(int(float(Bib.Par.DictPar['Endereco Driver']))))
        self.ui.le_VelMedida.setText('{0:0.2f}'.format(float(Bib.Par.DictPar['Velocidade Medida'])))
        self.ui.le_AceMedida.setText('{0:0.2f}'.format(float(Bib.Par.DictPar['Aceleracao Medida'])))
        self.ui.le_NVoltas.setText('{0:0d}'.format(int(float(Bib.Par.DictPar['#Voltas Medida']))))

        self.ui.le_PulsosEncoder.setText('{0:0d}'.format(int(float(Bib.Par.DictPar['Pulsos Encoder']))))
        self.ui.le_PassosMotor.setText('{0:0d}'.format(int(float(Bib.Par.DictPar['Passos Motor']))))
        self.ui.cb_PontosIntegracao.setCurrentIndex(int(list(Bib.IntDic.keys())[list(Bib.IntDic.values()).index(int(float(Bib.Par.DictPar['Pontos Integracao'])))]))
        self.ui.le_TriggerAlinhamento.setText('{0:0d}'.format(int(float(Bib.Par.DictPar['Pulsos para Trigger']))))
        
        # Tela Bobina
        self.ui.le_nEspiras.setText('{0:0d}'.format(int(float(Bib.Par.DictPar['#Espiras']))))
        self.ui.le_Raio1.setText('{0:0.6f}'.format(float(Bib.Par.DictPar['Raio1'])))
        self.ui.le_Raio2.setText('{0:0.6f}'.format(float(Bib.Par.DictPar['Raio2'])))
        self.ui.le_DistCentro.setText('{0:0.6f}'.format(float(Bib.Par.DictPar['Dist Centro'])))

        # Tela Motores
        self.ui.le_VelMotor.setText('{0:0.2f}'.format(float(Bib.Par.DictPar['Velocidade Motor'])))
        self.ui.le_AceMotor.setText('{0:0.2f}'.format(float(Bib.Par.DictPar['Aceleracao Motor'])))
        self.ui.le_NVoltasMotor.setText('{0:0.2f}'.format(float(Bib.Par.DictPar['#Voltas Motor'])))
##        self.ui.cb_HabilitaEncoder.setChecked(False)
        self.ui.le_LeituraEncoder.setText('')        

        # Tela Medir Offsets
        self.ui.le_NVoltasOffset.setText('{0:0d}'.format(int(float(Bib.Par.DictPar['#Voltas Offset']))))
        self.ui.cb_GanhoOffset.setCurrentIndex(0)

        self.set_item(0,1,Bib.Par.DictPar['Offset Ganho1'])
        self.set_item(1,1,Bib.Par.DictPar['Offset Ganho2'])
        self.set_item(2,1,Bib.Par.DictPar['Offset Ganho5'])
        self.set_item(3,1,Bib.Par.DictPar['Offset Ganho10'])
        self.set_item(4,1,Bib.Par.DictPar['Offset Ganho20'])
        self.set_item(5,1,Bib.Par.DictPar['Offset Ganho50'])
        self.set_item(6,1,Bib.Par.DictPar['Offset Ganho100'])

        # Tela Medir Componentes
        if (Bib.Par.DictPar['Volume Bloco'] == Bib.Par.DictPar['Volume Novo']):
            self.ui.le_VolumeBloco.setText(Bib.Par.DictPar['Volume Bloco'])
        elif  self.ui.cb_SubtrairVolume.isChecked() == True:
            self.ui.le_VolumeBloco.setText(Bib.Par.DictPar['Volume Novo'])
        else:
            self.ui.le_VolumeBloco.setText(str(Bib.Par.DictPar['Volume Bloco']))
        self.ui.le_VolumeSubtracao.setText(Bib.Par.DictPar['Subtrair Volume'])
##        self.ui.cb_SubtrairVolume.setChecked(False)
        self.ui.cb_CompPriMz.setChecked(bool(Bib.Par.DictPar['Principal Mz']))
        self.ui.cb_CompSecMx.setChecked(bool(Bib.Par.DictPar['Secundária Mx']))
        self.ui.cb_CompSecMy.setChecked(bool(Bib.Par.DictPar['Secundária My']))
        self.ui.cb_SalvarDadosGerais.setChecked(bool(Bib.Par.DictPar['SalvarGeral']))

##        self.ui.le_VolumeBloco.setEnabled(False)
##        self.ui.cb_SubtrairVolume.setEnabled(False)
##        self.ui.le_VolumeSubtracao.setEnabled(False)
##        self.ui.cb_CompPriMz.setEnabled(False)
##        self.ui.cb_CompSecMx.setEnabled(False)
##        self.ui.cb_CompSecMy.setEnabled(False)
##        self.ui.cb_GanhoOffset_Mz.setEnabled(False)
##        self.ui.cb_GanhoOffset_Mx.setEnabled(False)
##        self.ui.cb_GanhoOffset_My.setEnabled(False)
##        self.ui.pb_IniciarMedicao.setEnabled(False)
##        self.ui.cb_SalvarDadosGerais.setEnabled(False)

        self.ui.pb_Medicao.setValue(0)

    def Medida_Temperatura(self):
        i = 0
        self.ui.widget_3.canvas.draw()
        if self.ui.pb_IniciaColeta.isEnabled() == True:
            try:               
                # Habilita Timer para leitura
                self.TLeituraMultimetro = threading.Thread(target=self.TimerMultimetro,args={})
                self.TLeituraMultimetro.setDaemon = True
                self.TLeituraMultimetro.start()
            except:
                traceback.print_exc(file=sys.stdout)
                QtGui.QMessageBox.warning(self,'Falha Multimetro','Falha no loop de leitura do multimetro',QtGui.QMessageBox.Ok)
        else:
            try:
                self.TLeituraMultimetro.Parar = True
                time.sleep(0.3)
                self.ui.label_atual.setText('')
            except:
                 QtGui.QMessageBox.warning(self,'Falha Multimetro','Falha no loop de leitura de temperaturas',QtGui.QMessageBox.Ok)

    def TimerMultimetro(self):
        i = 1
        Bib.PararTudo = False
        Bib.VarDados.Temperatura = []
        soma = 0
        loop = int(self.ui.le_Medidas.text())

        Bib.Multimetro.Enviar(Bib.Multimetro.limpacomando)
        Bib.Multimetro.Enviar(Bib.Multimetro.reset)
        time.sleep(.5)
        Bib.Multimetro.Enviar(Bib.Multimetro.conectar)
        Bib.Multimetro.Enviar(Bib.Multimetro.conftemperatura)

        time.sleep(.5)

        while i <= loop and Bib.PararTudo == False:
            Bib.Multimetro.Enviar(Bib.Multimetro.ler)
            time.sleep(.5)
            temp = Bib.Multimetro.Ler()
            time.sleep(float(Bib.App.myapp.ui.le_Intervalo.text()))
            
            leitura = temp
            try:
                leitura = float(temp)
                
            except:
                if temp == '':
                    leitura = 0
            
            resistencia = float(self.ui.le_resistencia.text())
            self.ui.le_res.setText(str('{0:0.4f}'.format(leitura)))
##            print(leitura)

            temperatura = (leitura - 100)/resistencia #formula de Van Dusen para PT 100, por padrão resistencia é 0,385
            
            self.ui.le_medida.setText(str('{0:0.2f}'.format(temperatura)))
            Bib.VarDados.Temperatura.append('{0:0.2f}'.format(temperatura))
            self.PlotFuncTemp()
            self.ui.label_atual.setText(str(i))
            i = i+1

        if Bib.PararTudo == True:
            Bib.PararTudo = False
        
    def PararMultimetro(self):
        Bib.PararTudo = True
        
    def Bobina_Check_Change(self):
        
        Falha = False
        
        # #Espiras
        strvar = self.ui.le_nEspiras.text()
        valor,status = Bib.TesteVar(strvar,1,100000)
        if status == True:
            Bib.Par.DictPar['#Espiras'] = valor
        else:
            Falha = True

        # Raio1
        strvar = self.ui.le_Raio1.text()
        valor,status = Bib.TesteVar(strvar,0,1)
        if status == True:
            Bib.Par.DictPar['Raio1'] = valor
        else:
            Falha = True

        # Raio2
        strvar = self.ui.le_Raio2.text()
        valor,status = Bib.TesteVar(strvar,0,1)
        if status == True:
            Bib.Par.DictPar['Raio2'] = valor
        else:
            Falha = True

        # Dist Centro
        strvar = self.ui.le_DistCentro.text()
        valor,status = Bib.TesteVar(strvar,0,1)
        if status == True:
            Bib.Par.DictPar['Dist Centro'] = valor
        else:
            Falha = True

        self.AtualizaTela()
        Bib.SalvaRegistro()

        if Falha == False:
            QtGui.QMessageBox.warning(self,'Sucesso','Ajustes atualizados com sucesso',QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.warning(self,'Falha nos dados','Um ou mais ajustes da bobina não estão corretos, favor verificar limites e caracteres',QtGui.QMessageBox.Ok)

    def Motores_Change(self):
        Falha = False
        
        # Velocidade Motor
        strvar = self.ui.le_VelMotor.text()
        valor,status = Bib.TesteVar(strvar,0.1,30)
        if status == True:
            Bib.Par.DictPar['Velocidade Motor'] = valor
        else:
            Falha = True

        # Aceleracao Motor
        strvar = self.ui.le_AceMotor.text()
        valor,status = Bib.TesteVar(strvar,1,10)
        if status == True:
            Bib.Par.DictPar['Aceleracao Motor'] = valor
        else:
            Falha = True

        # #Voltas Motor
        strvar = self.ui.le_NVoltasMotor.text()
        valor,status = Bib.TesteVar(strvar,-50000,50000)
        if status == True:
            Bib.Par.DictPar['#Voltas Motor'] = valor
        else:
            Falha = True
            
        self.AtualizaTela()
        Bib.SalvaRegistro()

        if Falha == True:
            QtGui.QMessageBox.warning(self,'Falha nos dados','Um ou mais ajustes não estão corretos, favor verificar limites e caracteres',QtGui.QMessageBox.Ok)

    def HabilitaLeituraEncoder(self):
        if self.ui.cb_HabilitaEncoder.checkState() == 2:
            try:
                # Configura Integrador para utilização do Encoder
                Bib.Integrador.Enviar(Bib.Integrador.PDITipodeTrigger + str(int(float(Bib.Par.DictPar['Pulsos Encoder'])/4)))
                
                # Habilita Timer para leitura
                self.TLeituraEncoder = threading.Thread(target=self.TimerLeituraEncoder,args={})
                self.TLeituraEncoder.setDaemon = True
                self.TLeituraEncoder.start()
            except:
                traceback.print_exc(file=sys.stdout)
                QtGui.QMessageBox.warning(self,'Falha Encoder','Falha no loop de leitura do encoder',QtGui.QMessageBox.Ok)
        else:
            try:
                self.TLeituraEncoder.Parar = True
                time.sleep(0.3)
                self.ui.le_LeituraEncoder.setText('')
            except:
                QtGui.QMessageBox.warning(self,'Falha Encoder','Falha no loop de leitura do encoder',QtGui.QMessageBox.Ok)
        
    def MoverMotor_Manual(self):
        self.ui.pb_MoverMotor.setEnabled(False)
        self.ui.pb_PararMotor.setEnabled(True)
    
        Bib.Drivers.ConfMotor(int(float(Bib.Par.DictPar['Endereco Driver'])),\
                              int(float(Bib.Par.DictPar['Velocidade Motor'])),\
                              int(float(Bib.Par.DictPar['Aceleracao Motor'])),\
                              int(float(Bib.Par.DictPar['#Voltas Motor'])*int(float(Bib.Par.DictPar['Passos Motor']))))
                
        Bib.Drivers.MoverMotor(int(float(Bib.Par.DictPar['Endereco Driver'])))
        while (Bib.Drivers.ready(int(float(Bib.Par.DictPar['Endereco Driver']))) == False) and (Bib.PararTudo == False):
            QtGui.QApplication.processEvents()

        if Bib.PararTudo == True:
            Bib.Drivers.PararMotor(int(float(Bib.Par.DictPar['Endereco Driver'])))
            Bib.PararTudo = False
            QtGui.QMessageBox.warning(self,'Interrompido','Movimentação Interrompida.',QtGui.QMessageBox.Ok)

        self.ui.pb_PararMotor.setEnabled(False)
        self.ui.pb_MoverMotor.setEnabled(True)
        
    def PararMotor(self):
        Bib.PararTudo = True

    def NVoltasOffset_change(self):
        Falha = False

        # #Voltas Offset
        strvar = self.ui.le_NVoltasOffset.text()
        valor,status = Bib.TesteVar(strvar,0,100)
        if status == True:
            Bib.Par.DictPar['#Voltas Offset'] = valor
        else:
            Falha = True
            
        self.AtualizaTela()
        Bib.SalvaRegistro()

        if Falha == True:
            QtGui.QMessageBox.warning(self,'Falha nos dados','Número de Voltas incorreto, favor verificar limites e caracteres',QtGui.QMessageBox.Ok)

    def ProcuraIndiceEncoder(self):
        tempoespera = 0.1

        if Bib.PararTudo == False:
            # Zera Contador
            Bib.Integrador.Enviar(Bib.Integrador.PDIZerarContador)
            time.sleep(tempoespera)

            # Configura Motor
            pulsosmover = int(float(Bib.Par.DictPar['Passos Motor'])*1.25)

            Bib.Drivers.ConfMotor(int(float(Bib.Par.DictPar['Endereco Driver'])),\
                                  (float(Bib.Par.DictPar['Velocidade Medida'])),\
                                  int(float(Bib.Par.DictPar['Aceleracao Medida'])),\
                                  pulsosmover)

            # Busca índice encoder
            Bib.Integrador.Enviar(Bib.Integrador.PDIProcuraIndice)
            time.sleep(tempoespera)

            #Move Motor
            Bib.Drivers.MoverMotor(int(float(Bib.Par.DictPar['Endereco Driver'])))
            time.sleep(0.2)
            while (Bib.Drivers.ready(int(float(Bib.Par.DictPar['Endereco Driver']))) == False) and (Bib.PararTudo == False):
                time.sleep(0.2)
                QtGui.QApplication.processEvents()

    def AjusteOffsetIntegrador(self):
        self.ui.pb_AjusteOffset.setEnabled(False)
        Bib.Integrador.Enviar(Bib.Integrador.PDIClearStatus)
        time.sleep(0.1)

        Bib.Integrador.Enviar(Bib.Integrador.PDIConfiguraGanho + self.ui.cb_GanhoOffset.currentText())
        time.sleep(0.3)

        Bib.Integrador.Enviar(Bib.Integrador.PDICurtoCircuitoON)
        QtGui.QMessageBox.warning(self,'Ajuste Automático de Offset','Clique para finalizar o ajuste!',QtGui.QMessageBox.Ok)
        Bib.Integrador.Enviar(Bib.Integrador.PDICurtoCircuitoOFF)
        self.ui.pb_AjusteOffset.setEnabled(True)

    def IniciarMedidaOffset(self): 
        self.ui.pb_IniciarMedOffset.setEnabled(False)
        self.ui.pb_PararMedOffset.setEnabled(True)
        self.ui.pb_AjusteOffset.setEnabled(False)
        
        Bib.PararTudo = False

        QtGui.QMessageBox.warning(self,'Medição de Offset','Retire o magneto para medir o offset das bobinas!',QtGui.QMessageBox.Ok)

        # Limpa Variáveis
        Bib.Var = Biblioteca.Variaveis()
        Bib.Var.Dados = np.array([])
        Bib.Var.Dados_Media = np.array([])
        Bib.Var.Dados_Desvio = np.array([])
        
        # Clear Status
        Bib.Integrador.Enviar(Bib.Integrador.PDIClearStatus)
        time.sleep(0.1)

        # Configura Integrador
        Bib.Configurar_Integrador(self.ui.cb_GanhoOffset.currentText(),Bib.Par.DictPar['#Voltas Offset'])
##        Bib.Configurar_Integrador(Bib.Par.DictPar['Velocidade Medida'],Bib.Par.DictPar['Aceleracao Medida'])

        tmp = Bib.Integrador.Ler()
        while (tmp == ''):
            Bib.Configurar_Integrador(self.ui.cb_GanhoOffset.currentText(),Bib.Par.DictPar['#Voltas Offset'])
            
            # Procura Indice 
            self.ProcuraIndiceEncoder()
            time.sleep(1)
            
            # Executa PDI
            pulsosmover = (int(float(Bib.Par.DictPar['#Voltas Offset']) + 2) * int(float(Bib.Par.DictPar['Passos Motor']))) - int(float(Bib.Par.DictPar['Passos Motor'])*0.25)

            # Configura Driver
            Bib.Drivers.ConfMotor(int(float(Bib.Par.DictPar['Endereco Driver'])),\
                                  (float(Bib.Par.DictPar['Velocidade Medida'])),\
                                  (float(Bib.Par.DictPar['Aceleracao Medida'])),pulsosmover)

            # Esvazia buffer
            tmp = Bib.Integrador.Ler()
            print(tmp)

            # Iniciar Coleta PDI
            Bib.Integrador.Enviar(Bib.Integrador.PDIIniciaColeta)
            time.sleep(2)

            # Move motor
            Bib.Drivers.MoverMotor(int(float(Bib.Par.DictPar['Endereco Driver']))) - int(float(Bib.Par.DictPar['Passos Motor'])*0.25)

        status = -1
        valor = ''
        self.leituras = np.array([])
        while (status == -1) and (Bib.PararTudo == False):
            tmp = Bib.Integrador.Ler()
            if tmp != '':
                status = tmp.find('\x1a')
                time.sleep(1)
                if status == -1:
                    valor = float(tmp.replace('A','')) * Bib.Integrador.ConversaoPDI / (float(Bib.Par.DictPar['#Espiras'])/2)
                    self.leituras = np.append(self.leituras,valor)

        if Bib.PararTudo == False:                    
            # Separa dados em arrays e calcula media
            Bib.Var.Dados_Media = np.zeros(int(float(Bib.Par.DictPar['Pontos Integracao'])))
            for i in range(int(float(Bib.Par.DictPar['#Voltas Offset']))):
                Bib.Var.Dados = np.append(Bib.Var.Dados,Bib.VarDados())
                
                tmp = self.leituras.reshape([int(float(Bib.Par.DictPar['#Voltas Offset'])),int(float(Bib.Par.DictPar['Pontos Integracao']))])

                Bib.Var.Dados[i].StringDados = tmp[i]
                
                Bib.Var.Dados_Media = Bib.Var.Dados_Media + Bib.Var.Dados[i].StringDados
                
            Bib.Var.Dados_Media = Bib.Var.Dados_Media / float(Bib.Par.DictPar['#Voltas Offset'])

            # Calcula Desvio
            Bib.Var.Dados_Desvio = np.zeros(int(float(Bib.Par.DictPar['Pontos Integracao'])))
            for i in range(int(float(Bib.Par.DictPar['#Voltas Offset']))):
                Bib.Var.Dados_Desvio = Bib.Var.Dados_Desvio + (Bib.Var.Dados[i].StringDados - Bib.Var.Dados_Media)**2

            Bib.Var.Dados_Desvio = Bib.Var.Dados_Desvio / float(Bib.Par.DictPar['#Voltas Offset'])

            auxGanho = 'Offset Ganho' + self.ui.cb_GanhoOffset.currentText()
            Bib.Par.DictPar[auxGanho] = str(np.average(Bib.Var.Dados_Media))

            # Salvar arquivo
            np.savetxt('out.dat',self.leituras,fmt='%.12f',newline='\r\n')

            Bib.Integrador.Enviar(Bib.Integrador.PDICurtoCircuitoOFF)

        while (Bib.Drivers.ready(int(float(Bib.Par.DictPar['Endereco Driver']))) == False) and (Bib.PararTudo == False):
            QtGui.QApplication.processEvents()

        # Atualiza tela
        self.AtualizaTela()
        Bib.SalvaRegistro()

        if Bib.PararTudo == True:
            Bib.Drivers.PararMotor(int(float(Bib.Par.DictPar['Endereco Driver'])))
            Bib.PararTudo = False
            QtGui.QMessageBox.warning(self,'Interrompido','Movimentação Interrompida.',QtGui.QMessageBox.Ok)       
        else:
            QtGui.QMessageBox.warning(self,'Finalizado','Medição finalizada.',QtGui.QMessageBox.Ok)
            
        self.ui.pb_PararMedOffset.setEnabled(False)
        self.ui.pb_IniciarMedOffset.setEnabled(True)
        self.ui.pb_AjusteOffset.setEnabled(True)

    def PararMedidaOffset(self):
        Bib.PararTudo = True

    def ZerarOffsets(self):
        if QtGui.QMessageBox.question(self,'Warning!','Deseja realmente zerar todos os offsets?',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Cancel) == 1024:
            for i in range(7):
                self.set_item(i,1,'0.0')

            Bib.Par.DictPar['Offset Ganho1'] = '0.0'
            Bib.Par.DictPar['Offset Ganho2'] = '0.0'
            Bib.Par.DictPar['Offset Ganho5'] = '0.0'
            Bib.Par.DictPar['Offset Ganho10'] = '0.0'
            Bib.Par.DictPar['Offset Ganho20'] = '0.0'
            Bib.Par.DictPar['Offset Ganho50'] = '0.0'
            Bib.Par.DictPar['Offset Ganho100'] = '0.0'
            

            # Atualiza tela
            self.AtualizaTela()
            Bib.SalvaRegistro()
        else:
            pass

    def Verifica_Saturacao(self):
            status = Bib.Integrador.Status('1')
            bitstatus = int(status[3:4])
            if bitstatus != 0:
                # Configura Motor
                Bib.Drivers.ConfMotor(Bib.Par.DictPar['Endereco Driver'],\
                                      Bib.Par.DictPar['Velocidade Medida'],\
                                      Bib.Par.DictPar['Aceleracao Medida'],\
                                      (int(Bib.Par.DictPar['Passos Motor'])*-0.25))

                #Move Motor
                Bib.Drivers.MoverMotor(Bib.Par.DictPar['Endereco Driver'])
                while (Bib.Drivers.ready(Bib.Par.DictPar['Endereco Driver']) == False) and (Bib.PararTudo == False):
                    QtGui.QApplication.processEvents()
                
                Bib.PararTudo = True
                return True
            else:
                return False

    def set_item(self,lin,col,Text):
        item = QtGui.QTableWidgetItem()
        self.ui.tw_GanhosOffsets.setItem(lin, col, item)
        item.setText(Text)
                
    def Subtracao(self):
        if self.ui.cb_SubtrairVolume.isChecked():
            self.ui.le_VolumeSubtracao.setReadOnly(False)
            self.ui.le_VolumeSubtracao.setText('{0:0.6e}'.format(float(Bib.Par.DictPar['Subtrair Volume'])))
            self.VolumeSubtracao_change()
        else:
            self.ui.le_VolumeSubtracao.setText('0.0')
            self.ui.le_VolumeSubtracao.setReadOnly(True)
            Bib.Display.Volume = float(Bib.Par.DictPar['Volume Bloco'])
            self.ui.le_VolumeBloco.setText('{0:0.6e}'.format(Bib.Display.Volume))

    def VolumeSubtracao_change(self):
        Falha = False
        subtrair = self.ui.le_VolumeSubtracao.text()
        volume = self.ui.le_VolumeBloco.text()
        Bib.Display.Volume = Bib.Par.DictPar['Volume Bloco']
        valor,status = Bib.TesteVar(subtrair,0,100)

        if status == True:
            Bib.Par.DictPar['Subtrair Volume'] = str(valor)
            Volume_Novo = float(volume) - float(subtrair)
            Bib.Par.DictPar['Volume Novo'] = str(Volume_Novo)
        else:
            Falha = True
        
        self.AtualizaTela()
        Bib.SalvaRegistro()

        if Falha == True:
            QtGui.QMessageBox.warning(self,'Falha nos dados','Volume para subtração incorreto, favor verificar limites e caracteres',QtGui.QMessageBox.Ok)

    def DimensoesBloco(self):
        Falha = False
        QtGui.QApplication.processEvents()

##        if ((self.ui.rb_DimensaoAuto.isChecked()) or (self.ui.rb_DimensaoManual.isChecked())):
        self.ui.le_VolumeBloco.setEnabled(True)
        self.ui.cb_SubtrairVolume.setEnabled(True)
        self.ui.le_VolumeSubtracao.setEnabled(True)
        self.ui.cb_CompPriMz.setEnabled(True)
        self.ui.cb_CompSecMx.setEnabled(True)
        self.ui.cb_CompSecMy.setEnabled(True)
        self.ui.cb_GanhoOffset_Mz.setEnabled(True)
        self.ui.cb_GanhoOffset_Mx.setEnabled(True)
        self.ui.cb_GanhoOffset_My.setEnabled(True)
        self.ui.pb_IniciarMedicao.setEnabled(True)
        self.ui.cb_SalvarDadosGerais.setEnabled(True)
            
        if self.ui.rb_DimensaoAuto.isChecked():
            #Define Leitura Automatica do Volume dos Blocos
            #Volume dos blocos em metros 
            self.ui.le_VolumeBloco.setReadOnly(True)                #Impede escrita do volume
##            self.ui.le_VolumeBloco.set
            Bib.Drivers.Enviar(Bib.Drivers.HabilitaSaidaDigital + '\r')    #Habilita os Apalpadores
            QtGui.QApplication.processEvents()
            time.sleep(3)                                           #Tempo de Espera para realizar medida
            leitura = Bib.Display.LerDisplay()                      #Lê as dimensões do bloco
            VolumeBloco = float(Bib.Display.DisplayPos[0]*Bib.Display.DisplayPos[1]*Bib.Display.DisplayPos[2])
            valor,status = Bib.TesteVar(VolumeBloco,0,100)

            if Bib.Display.X == 0.0:
                QtGui.QMessageBox.warning(self,'Warning!','A Dimensão X é 0 (zero)!\n Por favor, verifique!\n\n'
                                              'NÃO foi possivel obter o VOLUME do bloco!!',QtGui.QMessageBox.Ok)
            if Bib.Display.Y == 0.0:
                QtGui.QMessageBox.warning(self,'Warning!','A Dimensão Y é 0 (zero)!\n Por favor, verifique!\n\n'
                                              'NÃO foi possivel obter o VOLUME do bloco!!',QtGui.QMessageBox.Ok)
            if Bib.Display.Z == 0.0:
                QtGui.QMessageBox.warning(self,'Warning!','A Dimensão Z é 0 (zero)!\n Por favor, verifique!\n\n'
                                              'NÃO foi possivel obter o VOLUME do bloco!!',QtGui.QMessageBox.Ok)
            
            if status == True:
                Bib.Par.DictPar['Volume Bloco'] = '{0:0.6e}'.format(valor)
                self.ui.le_VolumeBloco.setText('{0:0.6e}'.format(valor)) #Escreve Volume do Bloco
                time.sleep(0.3)
                self.ui.le_X.setText('{0:0.3e}'.format(Bib.Display.X))
                self.ui.le_Y.setText('{0:0.3e}'.format(Bib.Display.Y))
                self.ui.le_Z.setText('{0:0.3e}'.format(Bib.Display.Z))
                Bib.Drivers.Enviar(Bib.Drivers.DesabilitaSaidaDigital)  #Desabilita os Apalpadores
            else:
                Falha = True

            self.AtualizaTela()
            Bib.SalvaRegistro()
            
            if Falha == True:
                QtGui.QMessageBox.warning(self,'Falha nos dados','Volume incorreto, favor verificar!',QtGui.QMessageBox.Ok)
                Bib.Drivers.Enviar(Bib.Drivers.DesabilitaSaidaDigital)
                Bib.Par.DictPar['Volume Bloco'] = 0.0
            
        if self.ui.rb_DimensaoManual.isChecked():
            msgBox = QtGui.QMessageBox()
            msgBox.setText('Com quais medidas deseja entrar?')
            msgBox.setWindowTitle('Entrada MANUAL')
            btnQS = QtGui.QPushButton('Volume')#0
            msgBox.addButton(btnQS, QtGui.QMessageBox.YesRole)
            btnNo = QtGui.QPushButton('As Duas Medidas')#1
            msgBox.addButton(btnNo, QtGui.QMessageBox.NoRole)
            btn = QtGui.QPushButton('Dimensões')#2
            msgBox.addButton(btn, QtGui.QMessageBox.AcceptRole)
            ret = msgBox.exec_()

            if ret == 0:
                try:
                    #Define Volume Manual dos Blocos
                    self.ui.le_VolumeBloco.setReadOnly(False) #Habilita escrita do volume
                    QtGui.QMessageBox.information(self,'Informação!','As dimensões X,Y e Z serão consideradas zero!\n'
                                           'Entre com o volume na caixa de texto e pressione ENTER!',QtGui.QMessageBox.Ok)
                except:
                    pass

            if ret == 2:
                try:
                    self.ui.le_VolumeBloco.setReadOnly(True)
                    QtGui.QMessageBox.information(self,'Informação!','O volume será calculado de acordo com as dimensões fornecidas!',QtGui.QMessageBox.Ok)
                    x, ok = QtGui.QInputDialog.getText(self,'Dimensão do Bloco','Entre com a dimensão X em metros (m):')
                    Bib.Display.X = float(x)
                    y, ok = QtGui.QInputDialog.getText(self,'Dimensão do Bloco','Entre com a dimensão Y em metros (m):')
                    Bib.Display.Y = float(y)
                    z, ok = QtGui.QInputDialog.getText(self,'Dimensão do Bloco','Entre com a dimensão Z em metros (m):')
                    Bib.Display.Z = float(z)
                    
                    Bib.Display.Volume = float(Bib.Display.X)*float(Bib.Display.Y)*float(Bib.Display.Z)
                    time.sleep(1)
                    self.ui.le_VolumeBloco.setText('{0:0.5e}'.format(Bib.Display.Volume))
                    Bib.Par.DictPar['Volume Bloco'] = Bib.Display.Volume
                except:
                    QtGui.QInputDialog.Rejected
                    pass

            if ret == 1:
                try:
                    self.ui.le_VolumeBloco.setReadOnly(False)
                    x, ok = QtGui.QInputDialog.getText(self,'Dimensão do Bloco','Entre com a dimensão X em metros (m):')
                    Bib.Display.X = float(x)
                    y, ok = QtGui.QInputDialog.getText(self,'Dimensão do Bloco','Entre com a dimensão Y em metros (m):')
                    Bib.Display.Y = float(y)
                    z, ok = QtGui.QInputDialog.getText(self,'Dimensão do Bloco','Entre com a dimensão Z em metros (m):')
                    Bib.Display.Z = float(z)
                    QtGui.QMessageBox.information(self,'Informação!','Entre com o volume na caixa de texto e pressione ENTER!',QtGui.QMessageBox.Ok)
                except:
                    pass

    def Manual(self):
        try:
            Bib.Display.Volume = float(self.ui.le_VolumeBloco.displayText())
            self.ui.le_VolumeBloco.setText('{0:0.3f}'.format(Bib.Display.Volume))
            Bib.Par.DictPar['Volume Bloco'] = Bib.Display.Volume
        except:
            QtGui.QMessageBox.warning(self,'Warning!',
                                      'Por favor, verificar o valor de entrada !!\nUtilize apenas ponto [.], números e exponencial [e ou E]\n\n'
                                      'Exemplos de possíveis entradas: 0.0005 ou 3.0e-6',QtGui.QMessageBox.Ok)   

    def IniciarMedicao(self):
        self.ui.tabWidget.setTabEnabled(7,False)
        self.ui.gb_MedirComponentes.setEnabled(False)
        self.ui.pb_IniciarMedicao.setEnabled(False)
        self.ui.pb_PararMedicao.setEnabled(True)
        self.ui.cb_SalvarDadosGerais.setEnabled(False)
        self.ui.le_VolumeBloco.setReadOnly(True)
        self.ui.le_VolumeBloco_3.setText('')
        self.ui.le_VolumeBloco_4.setText('')
        self.ui.le_VolumeBloco_5.setText('')
        self.ui.le_VolumeBloco_6.setText('')
        self.ui.le_VolumeBloco_7.setText('')
        self.ui.le_VolumeBloco_8.setText('')

        Bib.PararTudo = False
        LockComp = False

        QtGui.QMessageBox.warning(self,'Medição','Selecione a chave de configuração da bobina: série ou paralela!',QtGui.QMessageBox.Ok)

        if ((self.ui.cb_CompSecMy.isChecked() == True) and (self.ui.cb_CompSecMx.isChecked() == True) ):
            if QtGui.QMessageBox.question(self,'Medição','Deseja medir as componentes secundárias juntas?',QtGui.QMessageBox.Yes,QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes :
                LockComp = True
                QtGui.QMessageBox.warning(self,'Medição','Será utilizado o ganho selecionado para Mx',QtGui.QMessageBox.Ok)
            else:
                LockComp = False
            
        # Identificação Bloco
        identificacao, ok = QtGui.QInputDialog.getText(self,'Identificação do bloco','Entre com a identificação do bloco para registro.')
        Bib.VarDados.Identificacao = identificacao

        # Temperatura Bloco
        temperatura, ok = QtGui.QInputDialog.getText(self,'Temperatura do Bloco','Entre com a temperatura do bloco (°C).',text='23.0')
        Bib.VarDados.Temperatura = temperatura
    
        # Medir Principal - Mz
        if (self.ui.cb_CompPriMz.isChecked() == True) and (Bib.PararTudo == False):
            QtGui.QMessageBox.warning(self,'Warning!','Insira o magneto para medir a componente Mz!',QtGui.QMessageBox.Ok)

            # Medir Componente Mz
            self.Executa_Medicao(self.ui.cb_GanhoOffset_Mz.currentText())
            Bib.Par.DictPar['Ganho Mz'] = self.ui.cb_GanhoOffset_Mz.currentText()
            # Guarda dados de Mz
            self.DadosMz = Bib.Var      

        # Medir Secundária - Mx / My
        if (self.ui.cb_CompSecMx.isChecked() == True) and (Bib.PararTudo == False):
            if LockComp == True:
                QtGui.QMessageBox.warning(self,'Warning!','Insira o magneto para medir as componentes MX e MY!',QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.warning(self,'Warning!','Insira o magneto para medir a componente MX!',QtGui.QMessageBox.Ok)

            # Medir Componente Mx
            self.Executa_Medicao(self.ui.cb_GanhoOffset_Mx.currentText())
            Bib.Par.DictPar['Ganho Mx'] = self.ui.cb_GanhoOffset_Mx.currentText()
            # Guarda dados de Mx
            self.DadosMx = Bib.Var
            
            if LockComp == True:               
                self.DadosMy = self.DadosMx
                Bib.Par.DictPar['Ganho My'] = Bib.Par.DictPar['Ganho Mx']
            
        # Medir Secundária - My
        if (self.ui.cb_CompSecMy.isChecked() == True) and (LockComp == False) and (Bib.PararTudo == False):
            QtGui.QMessageBox.warning(self,'Warning!','Insira o magneto para medir a componente My!',QtGui.QMessageBox.Ok)

            # Medir Componente My
            self.Executa_Medicao(self.ui.cb_GanhoOffset_My.currentText())
            Bib.Par.DictPar['Ganho My'] = self.ui.cb_GanhoOffset_My.currentText()
            # Guarda dados de My
            self.DadosMy = Bib.Var
                
        self.ui.gb_MedirComponentes.setEnabled(True)
        self.ui.pb_IniciarMedicao.setEnabled(True)
        self.ui.pb_PararMedicao.setEnabled(False)
        self.ui.cb_SalvarDadosGerais.setEnabled(True)

        QtGui.QMessageBox.warning(self,'Medição','Medição Finalizada!',QtGui.QMessageBox.Ok)

        self.ui.tabWidget.setTabEnabled(7,True)

        self.PlotFunc2y()
        self.PlotFunc()
        
        self.SalvaRegistro()

    def SalvaRegistro(self):
        if self.ui.cb_SalvarDadosGerais.isChecked() == True:
            try:
                self.fileName = QtGui.QFileDialog.getSaveFileName(self, "Save File", "", "Files (*.*)")
                if self.fileName.count('.') == 0:
                    self.fileName = self.fileName + '.dat'
            except:
                pass

            f = open(self.fileName,'w')
            f.writelines('Resultados da caracterização com bobina de helmholtz\n')
            f.writelines('\n')

            data = datetime.datetime.fromtimestamp(time.time()).strftime('%d/%m/%Y')
            hora = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')

            if self.ui.cb_CompPriMz.isChecked() == True:
                MagNormalMediaMz = str(Bib.App.myapp.DadosMz.MagNormalMedia)
                MagNormalDesvioMz = str(Bib.App.myapp.DadosMz.MagNormalDesvio)
            else:
                MagNormalMediaMz = 0
                MagNormalDesvioMz = 0

            if self.ui.cb_CompSecMx.isChecked() == True:
                MagNormalMediaMx = str(Bib.App.myapp.DadosMx.MagNormalMedia)
                MagNormalDesvioMx = str(Bib.App.myapp.DadosMx.MagNormalDesvio)
            else:
                MagNormalMediaMx = 0
                MagNormalDesvioMx = 0

            if self.ui.cb_CompSecMy.isChecked() == True:
                MagNormalMediaMy = str(Bib.App.myapp.DadosMy.MagNormalMedia)
                MagNormalDesvioMy = str(Bib.App.myapp.DadosMy.MagNormalDesvio)
            else:
                MagNormalMediaMy = 0
                MagNormalDesvioMy = 0

            dados = ('Data.............................: ' + str(data) + '\n' +\
                     'Hora.............................: ' + str(hora) + '\n' +\
                     'Temperatura......................: ' + str(Bib.Multimetro.MediaTemp) + '\n' +\
                     'Identificação do Bloco...........: ' + str(Bib.VarDados.Identificacao) + '\n\n' +\
                     'Numero de Voltas.................: ' + str(Bib.Par.DictPar['#Voltas Medida']) + '\n' +\
                     'Offset Ganho1....................: ' + str(Bib.Par.DictPar['Offset Ganho1'])+ '\n' +\
                     'Offset Ganho2....................: ' + str(Bib.Par.DictPar['Offset Ganho2'])+ '\n' +\
                     'Offset Ganho5....................: ' + str(Bib.Par.DictPar['Offset Ganho5'])+ '\n' +\
                     'Offset Ganho10...................: ' + str(Bib.Par.DictPar['Offset Ganho10'])+ '\n' +\
                     'Offset Ganho20...................: ' + str(Bib.Par.DictPar['Offset Ganho20'])+ '\n' +\
                     'Offset Ganho50...................: ' + str(Bib.Par.DictPar['Offset Ganho50'])+ '\n' +\
                     'Offset Ganho100..................: ' + str(Bib.Par.DictPar['Offset Ganho100'])+ '\n' +\
                     'Temperatura do Bloco.............: ' + str(Bib.VarDados.Temperatura)+ '°C' + '\n' +\
                     'Dimensão do Bloco................: ' + str(Bib.Display.X) + ' m x ' + str(Bib.Display.Y) + ' m x ' + str(Bib.Display.Z) + ' m' + '\n' +\
                     'Volume do Bloco..................: ' + str(Bib.Display.Volume) + ' m²' + '\n' +\
                     'Ganho Mz.........................: ' + str(Bib.Par.DictPar['Ganho Mz'])+ '\n' +\
                     'Ganho Mx.........................: ' + str(Bib.Par.DictPar['Ganho Mx'])+ '\n' +\
                     'Ganho My.........................: ' + str(Bib.Par.DictPar['Ganho My'])+ '\n' +\
                     '\nMagnetizações\n\n' +\
                     'Media Mz.........................: ' + str(MagNormalMediaMz) + '\n'+\
                     'Desvio Mz........................: ' + str(MagNormalDesvioMz) + '\n'+\
                     'Media Mx.........................: ' + str(MagNormalMediaMx) + '\n'+\
                     'Desvio Mx........................: ' + str(MagNormalDesvioMx) + '\n'+\
                     'Media My.........................: ' + str(MagNormalMediaMy) + '\n'+\
                     'Desvio My........................: ' + str(MagNormalDesvioMy) + '\n'+\
                     '\nDados Brutos\n\n')

            f.writelines(dados)

            # NENHUMA COMPONENTE SELECIONADA
            if((self.ui.cb_CompPriMz.isChecked() == False) and (self.ui.cb_CompSecMx.isChecked() == False) and (self.ui.cb_CompSecMy.isChecked() == False)):
                f.writelines('Nenhuma Componente selecionada')

            # TODAS AS COMPONENTES SELECIONADAS
            elif((self.ui.cb_CompPriMz.isChecked() == True) and (self.ui.cb_CompSecMx.isChecked() == True) and (self.ui.cb_CompSecMy.isChecked() == True)):
                f.writelines('Media Mz\t\tDesvio Mz\t\tMedia Mx\t\tDesvio Mx\t\tMedia My\t\tDesvio My\n')
                for i in range(len(Bib.App.myapp.DadosMz.Dados_Desvio)):
                    dados2 = '{0:0.12e}\t{1:0.12e}\t{2:0.12e}\t{3:0.12e}\t{4:0.12e}\t{5:0.12e}\n'.format(
                        Bib.App.myapp.DadosMz.Dados_Media[i],Bib.App.myapp.DadosMz.Dados_Desvio[i],
                        Bib.App.myapp.DadosMx.Dados_Media[i],Bib.App.myapp.DadosMx.Dados_Desvio[i],
                        Bib.App.myapp.DadosMy.Dados_Media[i],Bib.App.myapp.DadosMy.Dados_Desvio[i])
                    f.writelines(dados2)

            # COMPONENTES MZ E MX SELECIONADAS
            elif((self.ui.cb_CompPriMz.isChecked() == True) and (self.ui.cb_CompSecMx.isChecked() == True) and (self.ui.cb_CompSecMy.isChecked() == False)):
                f.writelines('Media Mz\t\tDesvio Mz\t\tMedia Mx\t\tDesvio Mx\n')
                for i in range(len(Bib.App.myapp.DadosMz.Dados_Desvio)):
                    dados2 = '{0:0.12e}\t{1:0.12e}\t{2:0.12e}\t{3:0.12e}\n'.format(
                        Bib.App.myapp.DadosMz.Dados_Media[i],Bib.App.myapp.DadosMz.Dados_Desvio[i],
                        Bib.App.myapp.DadosMx.Dados_Media[i],Bib.App.myapp.DadosMx.Dados_Desvio[i])
                    f.writelines(dados2)

            # COMPONENTES MZ E MY SELECIONADAS
            elif((self.ui.cb_CompPriMz.isChecked() == True) and (self.ui.cb_CompSecMx.isChecked() == False) and (self.ui.cb_CompSecMy.isChecked() == True)):
                f.writelines('Media Mz\t\tDesvio Mz\t\tMedia My\t\tDesvio My\n')
                for i in range(len(Bib.App.myapp.DadosMz.Dados_Desvio)):
                    dados2 = '{0:0.12e}\t{1:0.12e}\t{2:0.12e}\t{3:0.12e}\n'.format(
                        Bib.App.myapp.DadosMz.Dados_Media[i],Bib.App.myapp.DadosMz.Dados_Desvio[i],
                        Bib.App.myapp.DadosMy.Dados_Media[i],Bib.App.myapp.DadosMy.Dados_Desvio[i])
                    f.writelines(dados2)

            # COMPONENTES MX E MY SELECIONADAS
            elif((self.ui.cb_CompPriMz.isChecked() == False) and (self.ui.cb_CompSecMx.isChecked() == True) and (self.ui.cb_CompSecMy.isChecked() == True)):
                f.writelines('Media Mx\t\tDesvio Mx\t\tMedia My\t\tDesvio My\n')
                for i in range(len(Bib.App.myapp.DadosMx.Dados_Desvio)):
                    dados2 = '{0:0.12e}\t{1:0.12e}\t{2:0.12e}\t{3:0.12e}\n'.format(
                        Bib.App.myapp.DadosMx.Dados_Media[i],Bib.App.myapp.DadosMx.Dados_Desvio[i],
                        Bib.App.myapp.DadosMy.Dados_Media[i],Bib.App.myapp.DadosMy.Dados_Desvio[i])
                    f.writelines(dados2)

            # SOMENTE COMPONENTE MZ SELECIONADA
            elif((self.ui.cb_CompPriMz.isChecked() == True) and (self.ui.cb_CompSecMx.isChecked() == False) and (self.ui.cb_CompSecMy.isChecked() == False)):
                f.writelines('Media Mz\t\tDesvio Mz\n')
                for i in range(len(Bib.App.myapp.DadosMz.Dados_Desvio)):
                    dados2 = '{0:0.12e}\t{1:0.12e}\n'.format(
                        Bib.App.myapp.DadosMz.Dados_Media[i],Bib.App.myapp.DadosMz.Dados_Desvio[i])
                    f.writelines(dados2)

            # SOMENTE COMPONENTE MX SELECIONADA
            elif((self.ui.cb_CompPriMz.isChecked() == False) and (self.ui.cb_CompSecMx.isChecked() == True) and (self.ui.cb_CompSecMy.isChecked() == False)):
                f.writelines('Media Mx\t\tDesvio Mx\n')
                for i in range(len(Bib.App.myapp.DadosMx.Dados_Desvio)):
                    dados2 = '{0:0.12e}\t{1:0.12e}\n'.format(
                        Bib.App.myapp.DadosMx.Dados_Media[i],Bib.App.myapp.DadosMx.Dados_Desvio[i])
                    f.writelines(dados2)

            # SOMENTE COMPONENTE MY SELECIONADA
            elif((self.ui.cb_CompPriMz.isChecked() == False) and (self.ui.cb_CompSecMx.isChecked() == False) and (self.ui.cb_CompSecMy.isChecked() == True)):
                f.writelines('Media My\t\tDesvio My\n')
                for i in range(len(Bib.App.myapp.DadosMy.Dados_Desvio)):
                    dados2 = '{0:0.12e}\t{1:0.12e}\n'.format(
                        Bib.App.myapp.DadosMy.Dados_Media[i],Bib.App.myapp.DadosMy.Dados_Desvio[i])
                    f.writelines(dados2)
    
            f.close()
        else:
            pass
        
    def Executa_Medicao(self, Ganho):
        # Limpa Variáveis
        Bib.Var = Biblioteca.Variaveis()
        Bib.Var.Dados = np.array([])
        Bib.Var.Dados_Media = np.array([])
        Bib.Var.Dados_Desvio = np.array([])

        # Configura Integrador
        Bib.Configurar_Integrador(Ganho,Bib.Par.DictPar['#Voltas Medida'])

        # Procura Indice
        self.ProcuraIndiceEncoder()

        # Calcula Numero de voltas
        pulsosmover = (int(float(Bib.Par.DictPar['#Voltas Medida']) + 2) * int(float(Bib.Par.DictPar['Passos Motor']))) - int(float(Bib.Par.DictPar['Passos Motor'])*0.25)

        # Configura Driver
        Bib.Drivers.ConfMotor(int(float(Bib.Par.DictPar['Endereco Driver'])),
                              (float(Bib.Par.DictPar['Velocidade Medida'])),\
                              (float(Bib.Par.DictPar['Aceleracao Medida'])),\
                              pulsosmover)

        # Esvazia buffer
        tmp = Bib.Integrador.Ler()

        # Iniciar Coleta PDI
        Bib.Integrador.Enviar(Bib.Integrador.PDIIniciaColeta)
        time.sleep(0.5)

        # Move motor
        Bib.Drivers.MoverMotor(int(float(Bib.Par.DictPar['Endereco Driver'])))

        # Configura Barra de progresso
        self.ui.pb_Medicao.setValue(0)
        self.ui.pb_Medicao.setMaximum(float(Bib.Par.DictPar['#Voltas Medida'])*float(Bib.Par.DictPar['Pontos Integracao']))

        # Aguarda leitura de todos os dados
        status = -1
        valor = ''
        self.leituras = np.array([])
        while (status == -1) and (Bib.PararTudo == False):
            tmp = Bib.Integrador.Ler()
            if tmp != '':
                status = tmp.find('\x1a')
                if status == -1:
                    valor = float(tmp.replace('A','')) * Bib.Integrador.ConversaoPDI / (float(Bib.Par.DictPar['#Espiras'])/2)
                    self.leituras = np.append(self.leituras,valor)
                    # Atualiza Barra de progresso
                    self.ui.pb_Medicao.setValue(self.ui.pb_Medicao.value()+1)
                    QtGui.QApplication.processEvents()

##            # Carrega Arquivo Manual para verificação de cálculo.    
##            self.leituras = np.loadtxt('outIN.dat')
##            self.leituras = self.leituras * Bib.Integrador.ConversaoPDI / (float(Bib.Par.DictPar['#Espiras'])/2)
        if Bib.PararTudo == False:
            # Separa dados em arrays e calcula Media
            auxGanho = 'Offset Ganho' + Ganho
            Bib.Var.Dados_Media = np.zeros(int(float(Bib.Par.DictPar['Pontos Integracao'])))

            for i in range(int(float(Bib.Par.DictPar['#Voltas Medida']))):
                Bib.Var.Dados = np.append(Bib.Var.Dados,Bib.VarDados())
                
                tmp = self.leituras.reshape([int(float(Bib.Par.DictPar['#Voltas Medida'])),int(float(Bib.Par.DictPar['Pontos Integracao']))])

                Bib.Var.Dados[i].StringDados = tmp[i]
                
                # Acumula media e subtrai offset do ganho medido.
                Bib.Var.Dados_Media = Bib.Var.Dados_Media + Bib.Var.Dados[i].StringDados - float(Bib.Par.DictPar[auxGanho])

            Bib.Var.Dados_Media = Bib.Var.Dados_Media / float(Bib.Par.DictPar['#Voltas Medida'])

            # Calcula Desvio
            Bib.Var.Dados_Desvio = np.zeros(int(float(Bib.Par.DictPar['Pontos Integracao'])))
            for i in range(int(float(Bib.Par.DictPar['#Voltas Offset']))):
                Bib.Var.Dados_Desvio = Bib.Var.Dados_Desvio + (Bib.Var.Dados[i].StringDados - Bib.Var.Dados_Media)**2

            Bib.Var.Dados_Desvio = np.sqrt(Bib.Var.Dados_Desvio / float(Bib.Par.DictPar['#Voltas Medida']))

            # Calcula FFT e Magnetizacao
            self.CalculaFFT_Magnetizacao()

##            # Salvar arquivo
##            np.savetxt('outmed.dat',self.leituras,fmt='%.12f',newline='\r\n')

        # Aguarda fim do movimento do motor
        while (Bib.Drivers.ready(int(float(Bib.Par.DictPar['Endereco Driver']))) == False) and (Bib.PararTudo == False):
            QtGui.QApplication.processEvents()
        
    def CalculaFFT_Magnetizacao(self):
        NPontosPDI = float(Bib.Par.DictPar['Pontos Integracao'])
        dAlfa = (2*np.pi) / NPontosPDI
        n = float(Bib.Par.DictPar['Pontos Integracao']) / 2
        
        # Calcula FFT para todas as voltas
        for i in range(int(float(Bib.Par.DictPar['#Voltas Medida']))):
            Bib.Var.Dados[i].StringFFT = np.fft.fft(Bib.Var.Dados[i].StringDados)
            
            Bib.Var.Dados[i].StringFFT = Bib.Var.Dados[i].StringFFT / n
            Bib.Var.Dados[i].StringFFT[0] = Bib.Var.Dados[i].StringFFT[0] / 2
            
            Bib.Var.Dados[i].StringFFT = Bib.Var.Dados[i].StringFFT[1:] # Elimina primeiro pontos

            # Calcula harmonicos
            nPot = 0
            harmMax = 20
            
            Bib.Var.Dados[i].SAN = np.zeros(harmMax + 1)
            Bib.Var.Dados[i].SBN = np.zeros(harmMax + 1)
            Bib.Var.Dados[i].SSAN2 = np.zeros(harmMax + 1)
            Bib.Var.Dados[i].SSBN2 = np.zeros(harmMax + 1)
            Bib.Var.Dados[i].SdbdXN = np.zeros(harmMax + 1)
            Bib.Var.Dados[i].SdbdXN2 = np.zeros(harmMax + 1)
            Bib.Var.Dados[i].Smodulo = np.zeros(harmMax + 1)
            Bib.Var.Dados[i].Angulo = np.zeros(harmMax + 1)

            while nPot <= harmMax:
                FatorR = (float(Bib.Par.DictPar['Raio1'])**(nPot+1)) - ( (-1**(nPot+1))* float(Bib.Par.DictPar['Raio2'])**(nPot+1))

                # Coeficientes de Fourier
                af = Bib.Var.Dados[i].StringFFT[nPot].real
                bf = Bib.Var.Dados[i].StringFFT[nPot].imag * -1 # Inversão para manter mesmo sentido do software em Delphi

                if nPot == 0:
                    Bib.Var.Dados[i].CoefDipA = af
                    Bib.Var.Dados[i].CoefDipB = bf

                # Cálculo de Kn e Jn
                # Jn
                an = (af*np.sin((nPot+1)*dAlfa) + bf*(np.cos((nPot+1)*dAlfa)-1)) / (2*FatorR*(np.cos((nPot+1)*dAlfa)-1))
                # Kn
                bn = (bf*np.sin((nPot+1)*dAlfa) - af*(np.cos((nPot+1)*dAlfa)-1)) / (2*FatorR*(np.cos((nPot+1)*dAlfa)-1))

                dbdXN = (nPot+1)*((an*an + bn*bn)**(1/2))
                Bib.Var.Dados[i].SAN[nPot] = Bib.Var.Dados[i].SAN[nPot] + an
                Bib.Var.Dados[i].SBN[nPot] = Bib.Var.Dados[i].SBN[nPot] + bn
                Bib.Var.Dados[i].SSAN2[nPot] = Bib.Var.Dados[i].SSAN2[nPot] + an**2
                Bib.Var.Dados[i].SSBN2[nPot] = Bib.Var.Dados[i].SSBN2[nPot] + bn**2
                Bib.Var.Dados[i].SdbdXN[nPot] = Bib.Var.Dados[i].SdbdXN[nPot] + dbdXN
                Bib.Var.Dados[i].SdbdXN2[nPot] = Bib.Var.Dados[i].SdbdXN2[nPot] + dbdXN**2
                Bib.Var.Dados[i].Smodulo[nPot] = Bib.Var.Dados[i].Smodulo[nPot] + (an*an + bn*bn)**(1/2)

                self.Calcula_Angulos(i,nPot)
                
                nPot = nPot + 1
               
                QtGui.QApplication.processEvents()

            # Calcula Momentos de todas as medidas.
            self.Calcula_Momentos(i)

            QtGui.QApplication.processEvents()

        # Calcula Magnetizacao Media e Desvio - Zera Variaveis
        Bib.Var.MagNormalMedia = 0
        Bib.Var.MagNormalDesvio = 0
        Bib.Var.MagSkewMedia = 0
        Bib.Var.MagSkewDesvio = 0
        Mi0 = np.pi*4e-7
        
        # Media Magnetizacao
        for i in range(int(float(Bib.Par.DictPar['#Voltas Medida']))):
            Bib.Var.MagNormalMedia = Bib.Var.MagNormalMedia + Bib.Var.Dados[i].MagNormal
            Bib.Var.MagSkewMedia = Bib.Var.MagSkewMedia + Bib.Var.Dados[i].MagSkew

        Bib.Var.MagNormalMedia = Bib.Var.MagNormalMedia / float(Bib.Par.DictPar['#Voltas Medida'])
        Bib.Var.MagSkewMedia = Bib.Var.MagSkewMedia / float(Bib.Par.DictPar['#Voltas Medida'])

        # Desvio Magnetizacao
        for i in range(int(float(Bib.Par.DictPar['#Voltas Medida']))):
            Bib.Var.MagNormalDesvio = Bib.Var.MagNormalDesvio + (Bib.Var.Dados[i].MagNormal - Bib.Var.MagNormalMedia)**2
            Bib.Var.MagSkewDesvio = Bib.Var.MagSkewDesvio + (Bib.Var.Dados[i].MagSkew - Bib.Var.MagSkewMedia)**2

        Bib.Var.MagNormalDesvio = np.sqrt(Bib.Var.MagNormalDesvio / float(Bib.Par.DictPar['#Voltas Medida']))
        Bib.Var.MagSkewDesvio = np.sqrt(Bib.Var.MagSkewDesvio / float(Bib.Par.DictPar['#Voltas Medida']))

        # Divide pelo volume - Normal
        Bib.Var.MagNormalMedia = Bib.Var.MagNormalMedia / float(Bib.Par.DictPar['Volume Bloco']) * Mi0
        Bib.Var.MagNormalDesvio = Bib.Var.MagNormalDesvio / float(Bib.Par.DictPar['Volume Bloco']) * Mi0
        # Divide pelo volume - Skew
        Bib.Var.MagSkewMedia = Bib.Var.MagSkewMedia / float(Bib.Par.DictPar['Volume Bloco']) * Mi0
        Bib.Var.MagSkewDesvio = Bib.Var.MagSkewDesvio / float(Bib.Par.DictPar['Volume Bloco']) * Mi0

    def Calcula_Momentos(self,i):
        Mi0 = np.pi*4e-7
        dTeta = 2 * np.pi / float(Bib.Par.DictPar['Pontos Integracao'])
        TetaR = 0

        Bib.Var.Dados[i].Modulo = (float(Bib.Par.DictPar['Raio1'])**2) / (((float(Bib.Par.DictPar['Raio1'])**2) + (float(Bib.Par.DictPar['Dist Centro'])**2))**(3/2))

        Bib.Var.Dados[i].Alfa = (Bib.Var.Dados[i].CoefDipA * np.cos(TetaR)) - (Bib.Var.Dados[i].CoefDipB * np.sin(TetaR))

        Bib.Var.Dados[i].Beta = (Bib.Var.Dados[i].CoefDipB * np.cos(TetaR)) - (Bib.Var.Dados[i].CoefDipA * np.sin(TetaR))

        aux = (1/(Mi0*Bib.Var.Dados[i].Modulo))*( (-Bib.Var.Dados[i].Beta*np.sin(dTeta) + Bib.Var.Dados[i].Alfa*(1-np.cos(dTeta))) / (2*(1-np.cos(dTeta))))
        Bib.Var.Dados[i].MagNormal = Bib.Var.Dados[i].MagNormal + aux

        aux = (1/(Mi0*Bib.Var.Dados[i].Modulo))*( (Bib.Var.Dados[i].Alfa*np.sin(dTeta) + Bib.Var.Dados[i].Beta*(1-np.cos(dTeta))) / (2*(1-np.cos(dTeta))));
        Bib.Var.Dados[i].MagSkew = Bib.Var.Dados[i].MagSkew + aux

    def Calcula_Angulos(self,i,nPot):
        
        if( Bib.Var.Dados[i].SAN[nPot] > 0 and  Bib.Var.Dados[i].SBN[nPot] > 0):
            angulo = (1/(nPot+1))*np.arctan( Bib.Var.Dados[i].SAN[nPot]/ Bib.Var.Dados[i].SBN[nPot])
            angulo = (angulo/np.pi)*180
            angulo = 360 - angulo
            
        elif( Bib.Var.Dados[i].SAN[nPot] > 0 and  Bib.Var.Dados[i].SBN[nPot] < 0):
            angulo = (1/(nPot+1))*np.arctan( Bib.Var.Dados[i].SAN[nPot]/ Bib.Var.Dados[i].SBN[nPot])
            angulo = ((np.pi + angulo)/np.pi)*180
            angulo = 360 - angulo

        elif( Bib.Var.Dados[i].SAN[nPot] < 0 and  Bib.Var.Dados[i].SBN[nPot] < 0):
            angulo = (1/(nPot+1))*np.arctan( Bib.Var.Dados[i].SAN[nPot]/ Bib.Var.Dados[i].SBN[nPot])
            angulo = ((np.pi + angulo)/np.pi)*180
            angulo = 360 - angulo

        elif( Bib.Var.Dados[i].SAN[nPot] < 0 and  Bib.Var.Dados[i].SBN[nPot] > 0):
            angulo = (1/(nPot+1))*np.arctan( Bib.Var.Dados[i].SAN[nPot]/ Bib.Var.Dados[i].SBN[nPot])
            angulo = ((2*np.pi + angulo)/np.pi)*180
            angulo = 360 - angulo

        Bib.Var.Dados[i].Angulo[nPot] = angulo
        
    def PararMedicao(self):
        Bib.PararTudo = True

    def PlotFuncTemp(self):
        self.ui.widget_3.canvas.ax.clear()
        self.ui.widget_3.canvas.ax.set_ylabel('Temperatura (°C)',fontsize = 10)
        self.ui.widget_3.canvas.ax.set_title("Temperatura",fontsize = 10)
        self.ui.widget_3.canvas.ax.grid(True)
##        time = np.array(time.time())
##        time.sleep(1)
##        self.ui.widget_3.canvas.ax.plot(Bib.VarDados.Temperatura, time)
        self.ui.widget_3.canvas.ax.plot(Bib.VarDados.Temperatura, color = 'blue')
##        self.ui.widget_3.canvas.y.plot(time.localtime())
        self.ui.widget_3.canvas.draw()
    
    def PlotFunc(self):        
        if self.ui.cb_CompPriMz.isChecked() == True:
            self.ui.le_VolumeBloco_3.setText(str(Bib.App.myapp.DadosMz.MagNormalMedia))
            self.ui.le_VolumeBloco_4.setText(str(Bib.App.myapp.DadosMz.MagNormalDesvio))
            self.ui.widget.canvas.ax.clear()
            self.ui.widget.canvas.ax.set_ylabel('Tensão Integrada(1E-8)',fontsize = 8)
            self.ui.widget.canvas.ax.set_title("Componente Mz",fontsize = 10)
            self.ui.widget.canvas.ax.grid(True)
            self.ui.widget.canvas.ax.plot(Bib.App.myapp.DadosMz.Dados_Media, color = 'blue')
            self.ui.widget.canvas.draw()
            

    def PlotFunc2y(self):
        self.ui.widget_2.canvas.ax2 = self.ui.widget_2.canvas.ax.twinx()
        if self.ui.cb_CompSecMx.isChecked() == True:
            if self.ui.cb_CompSecMy.isChecked() == True:             
                self.ui.le_VolumeBloco_5.setText(str(Bib.App.myapp.DadosMx.MagNormalMedia))
                self.ui.le_VolumeBloco_6.setText(str(Bib.App.myapp.DadosMx.MagNormalDesvio))
                self.ui.widget_2.canvas.ax.clear()
                self.ui.widget_2.canvas.ax.set_ylabel('Tensão Integrada Mx(1E-8)',fontsize = 8)
                self.ui.widget_2.canvas.ax.set_title("Componente Mx e My",fontsize = 10)
                self.ui.widget_2.canvas.ax.grid(True)
                self.ui.widget_2.canvas.ax.plot(Bib.App.myapp.DadosMx.Dados_Media, alpha = 0.75, color = 'red')
                
                if self.ui.widget_2.canvas.ax2 != None:
                    self.ui.le_VolumeBloco_7.setText(str(Bib.App.myapp.DadosMy.MagNormalMedia))
                    self.ui.le_VolumeBloco_8.setText(str(Bib.App.myapp.DadosMy.MagNormalDesvio))
                    self.ui.widget_2.canvas.ax2.clear()
                    self.ui.widget_2.canvas.ax2.set_ylabel('Tensão Integrada My(1E-8)',fontsize = 8)
                    self.ui.widget_2.canvas.ax2.grid(True)
                    self.ui.widget_2.canvas.ax2.plot(Bib.App.myapp.DadosMy.Dados_Media, alpha = 0.75, color = 'green')
                self.ui.widget_2.canvas.draw()
                
            self.ui.le_VolumeBloco_5.setText(str(Bib.App.myapp.DadosMx.MagNormalMedia))
            self.ui.le_VolumeBloco_6.setText(str(Bib.App.myapp.DadosMx.MagNormalDesvio))    
            self.ui.widget_2.canvas.ax.clear()
            self.ui.widget_2.canvas.ax.set_ylabel('Tensão Integrada Mx(1E-8)',fontsize = 8)
            self.ui.widget_2.canvas.ax.set_title("Componente Mx",fontsize = 10)
            self.ui.widget_2.canvas.ax.grid(True)
            self.ui.widget_2.canvas.ax.plot(Bib.App.myapp.DadosMx.Dados_Media, alpha = 0.75, color = 'red')
            self.ui.widget_2.canvas.draw()

        elif ((self.ui.cb_CompSecMy.isChecked() == True) and (self.ui.cb_CompSecMx.isChecked() == False)):
            self.ui.le_VolumeBloco_7.setText(str(Bib.App.myapp.DadosMy.MagNormalMedia))
            self.ui.le_VolumeBloco_8.setText(str(Bib.App.myapp.DadosMy.MagNormalDesvio))
            self.ui.widget_2.canvas.ax.clear()
            self.ui.widget_2.canvas.ax.set_ylabel('Tensão Integrada My(1E-8)',fontsize = 8)
            self.ui.widget_2.canvas.ax.set_title("Componente My",fontsize = 10)
            self.ui.widget_2.canvas.ax.grid(True)
            self.ui.widget_2.canvas.ax.plot(Bib.App.myapp.DadosMy.Dados_Media, alpha = 0.75, color = 'green')
            self.ui.widget_2.canvas.draw()
            
    def TimerDisplay(self):
        while (Bib.Globals.DriverTimerDisp > 0):
            if (Bib.Globals.DriverTimerDisp == 1):
                try:
                    Bib.Display.LimpaTxRx()
                    Bib.Display.LerDisplay()
                    time.sleep(0.15)
                except:
                    Bib.Display.LimpaTxRx()
                    print('Erro de Leitura Display')

    def TimerLeituraEncoder(self):
        self.Parar = False
        Bib.VarDados.PulsosEncoder = []
        while self.Parar == False:
            try:
                Bib.Integrador.Enviar(Bib.Integrador.PDILerEncoder)
                time.sleep(0.3)
                leitura = Bib.Integrador.Ler()
                self.ui.le_LeituraEncoder.setText(leitura)
                Bib.VarDados.PulsosEncoder.append(leitura)
            except:
                QtGui.QApplication.processEvents()
                
class Interface(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()
    def run(self):
        self.App = QtGui.QApplication(sys.argv)
        self.myapp = Principal()
        self.myapp.show()
        self.App.exec_()
        
if __name__ == '__main__':
    
    # Carrega Biblioteca
    Bib = Biblioteca.Bib()

    # Exibe Tela Principal
    Bib.App = Interface()

    # Carrega Registro de Parâmetros
    Bib.CarregaRegistro()

    time.sleep(2)

    # Atualiza Variáveis na Tela
    Bib.App.myapp.AtualizaTela()
