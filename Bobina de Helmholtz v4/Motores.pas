unit Motores;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  StdCtrls, Buttons, Loco3, Biblioteca;

type
  TFMotores = class(TForm)
    GBMotor: TGroupBox;
    Label14: TLabel;
    Label15: TLabel;
    Label16: TLabel;
    Label17: TLabel;
    BBMoverMotor: TBitBtn;
    BBPararMotor: TBitBtn;
    EVelM: TEdit;
    EAceM: TEdit;
    ENVoltasM: TEdit;
    EEncoder: TEdit;
    CBLerEncoder: TCheckBox;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure AtualizaValores;
    procedure FormShow(Sender: TObject);
    procedure EVelMExit(Sender: TObject);
    procedure EAceMExit(Sender: TObject);
    procedure ENVoltasMExit(Sender: TObject);
    procedure BBPararMotorClick(Sender: TObject);
    procedure BBMoverMotorClick(Sender: TObject);
    procedure CBLerEncoderClick(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    Pont_Jan: ^TFMotores
  end;

var
  FMotores: TFMotores;

implementation

uses Helmholtz_v4, Conexoes, ConfGeral, ConfBob, Offset, Medicao;

{$R *.DFM}

procedure TFMotores.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  CBLerEncoder.Checked := False;
  Pont_Jan^:=nil;
  Release;
  FHelmholtz.Show;
end;

procedure TFMotores.FormShow(Sender: TObject);
begin
   AtualizaValores;
end;

procedure TFMotores.AtualizaValores;
begin
   EVelM.Text := Vel_Motor_Manual;
   EAceM.Text := Ace_Motor_Manual;
   ENVoltasM.Text := NVoltas_Manual;
end;

procedure TFMotores.EVelMExit(Sender: TObject);
begin
   EVelM.Text := FBiblioteca.TestaLimite(EVelM.Text,Limite_VelMin,Limite_VelMax,2);
   Vel_Motor_Manual := EVelM.Text;
   FBiblioteca.GravarRegistro('Vel_Motor_Manual',Vel_Motor_Manual);
end;

procedure TFMotores.EAceMExit(Sender: TObject);
begin
   EAceM.Text := FBiblioteca.TestaLimite(EAceM.Text,Limite_AceMin,Limite_AceMax,2);
   Ace_Motor_Manual := EAceM.Text;
   FBiblioteca.GravarRegistro('Ace_Motor_Manual',Ace_Motor_Manual);
end;

procedure TFMotores.ENVoltasMExit(Sender: TObject);
begin
   ENVoltasM.Text := FBiblioteca.TestaLimite(ENVoltasM.Text,Limite_VoltasManualMin,Limite_VoltasManualMax,6);
   NVoltas_Manual := ENVoltasM.Text;
   FBiblioteca.GravarRegistro('NVoltas_Manual',NVoltas_Manual);
end;

procedure TFMotores.BBPararMotorClick(Sender: TObject);
begin
   PararTudo := True;
end;

procedure TFMotores.BBMoverMotorClick(Sender: TObject);
begin
    {Habilita}
    BBPararMotor.Enabled := True;
    {********}

    {Desabilita}
    BBMoverMotor.Enabled := False;
    EVelM.Enabled := False;
    EAceM.Enabled := False;
    ENVoltasM.Enabled := False;
    PararTudo :=False;
    {********}

    FBiblioteca.ConfiguraDriver(Vel_Motor_Manual,Ace_Motor_Manual);

    Distancia := Round(StrToInt(PassosMotor)*StrToFloat(NVoltas_Manual));
    FBiblioteca.Parker.setDistancia(Smot(StrToInt(EndDriver)),Distancia);
    FBiblioteca.Parker.move(Smot(StrToInt(EndDriver)));
    repeat
      Application.ProcessMessages;
    until not (FBiblioteca.Parker.Movendo(Smot(StrToInt(EndDriver))) or PararTudo = True);

    if PararTudo = True then
    begin
       FBiblioteca.Parker.Pare(Smot(StrToInt(EndDriver)));
       MessageDlg('Movimento Cancelado!',mtWarning, [mbOk],0);
    end;

    {Desabilita}
    BBPararMotor.Enabled := False;
    {********}

    {Habilita}
    BBMoverMotor.Enabled := True;
    EVelM.Enabled := True;
    EAceM.Enabled := True;
    ENVoltasM.Enabled := True;
    {********}
end;

procedure TFMotores.CBLerEncoderClick(Sender: TObject);
begin
   if CBLerEncoder.Checked = True then
   begin
      FBiblioteca.DispGPIB.Leitura(tmpGPIB,10);
      FBiblioteca.DispGPIB.Escrita(PDITipodeTrigger+IntToStr(Round(StrToInt(PulsosEncoder)/4))+CR);
      delay(EsperaIntegrador);

      FBiblioteca.DispGPIB.Leitura(tmpGPIB,10);

      FBiblioteca.TimerEnc.Enabled := True;
   end
   else
   begin
      FBiblioteca.TimerEnc.Enabled := False;
   end;
end;

end.
