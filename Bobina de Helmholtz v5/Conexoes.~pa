unit Conexoes;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  StdCtrls, Buttons, Loco3, Biblioteca;

type
  TFConexoes = class(TForm)
    GBDriver: TGroupBox;
    Label1: TLabel;
    Label2: TLabel;
    CBPorta: TComboBox;
    Label3: TLabel;
    Label4: TLabel;
    Label5: TLabel;
    Label6: TLabel;
    GBIntegrador: TGroupBox;
    Label7: TLabel;
    EEndGPIB: TEdit;
    Label10: TLabel;
    GBConectar: TGroupBox;
    BBConectar: TBitBtn;
    CBParidade: TComboBox;
    CBStopBits: TComboBox;
    CBBaudrate: TComboBox;
    CBDataBits: TComboBox;
    GBDisplay: TGroupBox;
    Label8: TLabel;
    Label9: TLabel;
    Label11: TLabel;
    Label12: TLabel;
    Label13: TLabel;
    Label14: TLabel;
    CBPortaDisplay: TComboBox;
    CBParidadeDisplay: TComboBox;
    CBStopBitsDisplay: TComboBox;
    CBBaudrateDisplay: TComboBox;
    CBDataBitsDisplay: TComboBox;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormShow(Sender: TObject);
    procedure AtualizaValores;
    procedure CBBaudratChange(Sender: TObject);
    procedure CBDatabitsChange(Sender: TObject);
    procedure CBStopBitsChange(Sender: TObject);
    procedure CBPortaChange(Sender: TObject);
    procedure CBParidadeChange(Sender: TObject);
    procedure EEndGPIBExit(Sender: TObject);
    procedure BBConectarClick(Sender: TObject);
    procedure CBPortaDisplayChange(Sender: TObject);
    procedure CBBaudrateDisplayChange(Sender: TObject);
    procedure CBDataBitsDisplayChange(Sender: TObject);
    procedure CBStopBitsDisplayChange(Sender: TObject);
    procedure CBParidadeDisplayChange(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    Pont_Jan: ^TFConexoes
  end;

var
  FConexoes: TFConexoes;

implementation

uses Helmholtz_v4, ConfGeral, ConfBob, Offset, Medicao, Motores;

{$R *.DFM}

procedure TFConexoes.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  if BBConectar.Caption = 'Conectar Dispositivos' then
  begin
     Pont_Jan^:=nil;
     Release;
     FHelmholtz.Show;
  end
  else
  begin
     FConexoes.Hide;
     FHelmholtz.Show;
  end;
end;

procedure TFConexoes.FormShow(Sender: TObject);
begin
   AtualizaValores;
end;

procedure TFConexoes.AtualizaValores;
begin
   CBPorta.ItemIndex := StrToInt(PortaDriver);
   CBBaudrate.ItemIndex := StrToInt(BaudrateDriver);
   CBDatabits.ItemIndex := StrToInt(DatabitsDriver);
   CBStopBits.ItemIndex := StrToInt(StopbitsDriver);
   CBParidade.ItemIndex := StrToInt(ParidadeDriver);

   CBPortaDisplay.ItemIndex := StrToInt(PortaDisplay);
   CBBaudrateDisplay.ItemIndex := StrToInt(BaudrateDisplay);
   CBDatabitsDisplay.ItemIndex := StrToInt(DatabitsDisplay);
   CBStopBitsDisplay.ItemIndex := StrToInt(StopbitsDisplay);
   CBParidadeDisplay.ItemIndex := StrToInt(ParidadeDisplay);

   EEndGPIB.Text := EndGPIBInt;
end;

procedure TFConexoes.CBPortaChange(Sender: TObject);
begin
   PortaDriver := IntToStr(CBPorta.ItemIndex);
   CBPorta.ItemIndex := StrToInt(PortaDriver);
   FBiblioteca.GravarRegistro('PortaDriver',PortaDriver);
end;

procedure TFConexoes.CBBaudratChange(Sender: TObject);
begin
   BaudrateDriver := IntToStr(CBBaudrate.ItemIndex);
   CBBaudrate.ItemIndex := StrToInt(BaudrateDriver);
   FBiblioteca.GravarRegistro('BaudrateDriver',BaudrateDriver);
end;

procedure TFConexoes.CBDatabitsChange(Sender: TObject);
begin
   DatabitsDriver := IntToStr(CBDatabits.ItemIndex);
   CBDatabits.ItemIndex := StrToInt(DatabitsDriver);
   FBiblioteca.GravarRegistro('DatabitsDriver',DatabitsDriver);
end;

procedure TFConexoes.CBStopBitsChange(Sender: TObject);
begin
   StopbitsDriver := IntToStr(CBStopBits.ItemIndex);
   CBStopBits.ItemIndex := StrToInt(StopbitsDriver);
   FBiblioteca.GravarRegistro('StopbitsDriver',StopBitsDriver);
end;

procedure TFConexoes.CBParidadeChange(Sender: TObject);
begin
   ParidadeDriver := IntToStr(CBParidade.ItemIndex);
   CBParidade.ItemIndex := StrToInt(ParidadeDriver);
   FBiblioteca.GravarRegistro('ParidadeDriver',ParidadeDriver);
end;

{Display}
procedure TFConexoes.CBPortaDisplayChange(Sender: TObject);
begin
   PortaDisplay := IntToStr(CBPortaDisplay.ItemIndex);
   CBPortaDisplay.ItemIndex := StrToInt(PortaDisplay);
   FBiblioteca.GravarRegistro('PortaDisplay',PortaDisplay);
end;

procedure TFConexoes.CBBaudrateDisplayChange(Sender: TObject);
begin
   BaudrateDisplay := IntToStr(CBBaudrateDisplay.ItemIndex);
   CBBaudrateDisplay.ItemIndex := StrToInt(BaudrateDisplay);
   FBiblioteca.GravarRegistro('BaudrateDisplay',BaudrateDisplay);
end;

procedure TFConexoes.CBDataBitsDisplayChange(Sender: TObject);
begin
   DatabitsDisplay := IntToStr(CBDatabitsDisplay.ItemIndex);
   CBDatabitsDisplay.ItemIndex := StrToInt(DatabitsDisplay);
   FBiblioteca.GravarRegistro('DatabitsDisplay',DatabitsDisplay);
end;

procedure TFConexoes.CBStopBitsDisplayChange(Sender: TObject);
begin
   StopbitsDisplay := IntToStr(CBStopBitsDisplay.ItemIndex);
   CBStopBitsDisplay.ItemIndex := StrToInt(StopbitsDisplay);
   FBiblioteca.GravarRegistro('StopbitsDisplay',StopBitsDisplay);
end;

procedure TFConexoes.CBParidadeDisplayChange(Sender: TObject);
begin
   ParidadeDisplay := IntToStr(CBParidadeDisplay.ItemIndex);
   CBParidadeDisplay.ItemIndex := StrToInt(ParidadeDisplay);
   FBiblioteca.GravarRegistro('ParidadeDisplay',ParidadeDisplay);
end;

procedure TFConexoes.EEndGPIBExit(Sender: TObject);
begin
   EEndGPIB.Text := FBiblioteca.TestaLimite(EEndGPIB.Text,Limite_GPIB_Min,Limite_GPIB_Max,0);
   EndGPIBInt := EEndGPIB.Text;
   FBiblioteca.GravarRegistro('EndGPIBInt',EndGPIBInt);
end;

procedure TFConexoes.BBConectarClick(Sender: TObject);
begin
   EEndGPIB.Text := FBiblioteca.TestaLimite(EEndGPIB.Text,Limite_GPIB_Min,Limite_GPIB_Max,0);

   if (CBPorta.ItemIndex = -1) or (CBBaudrate.ItemIndex = -1) or (CBDataBits.ItemIndex = -1) or
      (CBStopBits.ItemIndex = -1) or (CBParidade.ItemIndex = -1) or (EEndGPIB.Text = '') then
   begin
      MessageDlg('Preencha todos os parâmetros de configuração antes de conectar!!!', mtInformation,[mbOk], 0);
      Exit;
   end;

   if BBConectar.Caption = 'Conectar Dispositivos' then
   begin
      {Porta Driver}
      FBiblioteca.Parker.Port := SPort232(StrToInt(PortaDriver)+1);
      if FBiblioteca.Parker.Abre then
      begin
         FBiblioteca.Parker.BaudRate := StrToInt(CBBaudrate.Text);
         FBiblioteca.Parker.Paridade := SParidade(StrToInt(ParidadeDriver));
         FBiblioteca.Parker.DataBits := StrToInt(CBDataBits.Text);
         FBiblioteca.Parker.StopBits := SStopBits(StrToInt(StopBitsDriver));
      end
      else
      begin
         MessageDlg('Falha de conexão com o Driver!!!', mtInformation,[mbOk], 0);
         exit;
      end;

      {Porta Display}
      FBiblioteca.RSDisplay1.Port := SPort232(StrToInt(PortaDisplay)+1);
      if FBiblioteca.RSDisplay1.Abre then
      begin
         FBiblioteca.RSDisplay1.BaudRate := StrToInt(CBBaudrateDisplay.Text);
         FBiblioteca.RSDisplay1.Paridade := SParidade(StrToInt(ParidadeDisplay));
         FBiblioteca.RSDisplay1.DataBits := StrToInt(CBDataBitsDisplay.Text);
         FBiblioteca.RSDisplay1.StopBits := SStopBits(StrToInt(StopBitsDisplay));
      end
      else
      begin
         MessageDlg('Falha de conexão com o Display!!!', mtInformation,[mbOk], 0);
         //exit;
      end;
      FBiblioteca.Ler_Display;

      {Endereço GPIB Integrador}
      FBiblioteca.DispGPIB.Disp := StrToInt(EndGPIBInt);

      try
         FBiblioteca.DispGPIB.inicializa;
         FBiblioteca.DispGPIB.Leitura(tmpGPIB,10);
         FBiblioteca.DispGPIB.Escrita(PDIConfiguraGanho + '10' + CR); {Configura Ganho}
         delay(EsperaIntegrador);
      except
         MessageDlg('Falha de conexão com o Integrador!!!', mtInformation,[mbOk], 0);
         //exit;
      end;

      {Habilita}
      FHelmholtz.MConfigGeral.Enabled := True;
      FHelmholtz.MConfigBob.Enabled := True;
      FHelmholtz.MExecutar.Enabled := True;
      FHelmholtz.MMotores.Enabled := True;
      {****************}

      {Desabilita}
      GBDriver.Enabled := False;
      GBDisplay.Enabled := False;                    
      GBIntegrador.Enabled := False;
      {****************}

      BBConectar.Caption := 'Desconectar Dispositivos';

      MessageDlg('Dispositivos Conectados!!!', mtInformation,[mbOk], 0);
      FConexoes.Hide;
      FHelmholtz.Show;
   end
   else
   begin
      FBiblioteca.Parker.Fecha;
      FBiblioteca.RsDisplay1.Fecha;
      FechaLoco;
      BBConectar.Caption := 'Conectar Dispositivos';

      {Desabilita}
         FHelmholtz.MConfigGeral.Enabled := False;
         FHelmholtz.MConfigBob.Enabled := False;
         FHelmholtz.MExecutar.Enabled := False;
         FHelmholtz.MMotores.Enabled := False;
      {****************}

      {Habilita}
      GBDriver.Enabled := True;
      GBDisplay.Enabled := True;
      GBIntegrador.Enabled := True;
      {****************}

      MessageDlg('Dispositivos Desconectados!!!', mtInformation,[mbOk], 0);
   end;
end;

end.
