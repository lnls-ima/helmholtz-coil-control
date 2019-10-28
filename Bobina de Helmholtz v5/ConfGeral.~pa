unit ConfGeral;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  StdCtrls, ExtCtrls, Biblioteca;

type
  TFConfGeral = class(TForm)
    GBDriverMotor: TGroupBox;
    Label1: TLabel;
    Label3: TLabel;
    EVelocidade: TEdit;
    Label4: TLabel;
    EAceleracao: TEdit;
    Label5: TLabel;
    Label6: TLabel;
    Label7: TLabel;
    ENVoltas: TEdit;
    Label8: TLabel;
    EPulsosEncoder: TEdit;
    Label2: TLabel;
    Label9: TLabel;
    Label10: TLabel;
    EPassosMotor: TEdit;
    Label11: TLabel;
    GBIntegrador: TGroupBox;
    Label12: TLabel;
    Label14: TLabel;
    CBPontos: TComboBox;
    Label26: TLabel;
    ETrigger: TEdit;
    Image1: TImage;
    Image2: TImage;
    Label15: TLabel;
    EEndDriver: TEdit;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure AtualizaValores;
    procedure FormShow(Sender: TObject);
    procedure EVelocidadeExit(Sender: TObject);
    procedure EAceleracaoExit(Sender: TObject);
    procedure ENVoltasExit(Sender: TObject);
    procedure EPulsosEncoderExit(Sender: TObject);
    procedure EPassosMotorExit(Sender: TObject);
    procedure CBPontosExit(Sender: TObject);
    procedure ETriggerExit(Sender: TObject);
    procedure EEndDriverExit(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    Pont_Jan: ^TFConfGeral
  end;

var
  FConfGeral: TFConfGeral;

implementation

uses Helmholtz_v4, Conexoes, ConfBob, Offset, Medicao, Motores;

{$R *.DFM}

procedure TFConfGeral.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Pont_Jan^:=nil;
  Release;
  FHelmholtz.Show;
end;

procedure TFConfGeral.AtualizaValores;
begin
   EVelocidade.Text := VelMotorMed;
   EAceleracao.Text := AceMotorMed;
   ENVoltas.Text := NVoltasMed;
   EPulsosEncoder.Text := PulsosEncoder;
   EPassosMotor.Text := IntToStr(StrToInt(PassosMotor)*-1);
   CBPontos.ItemIndex := StrToInt(Npontos);
   ETrigger.Text := Trigger;
   EEndDriver.Text := IntToStr(StrToInt(EndDriver)+1);
end;

procedure TFConfGeral.FormShow(Sender: TObject);
begin
   AtualizaValores;
end;

procedure TFConfGeral.EVelocidadeExit(Sender: TObject);
begin
   EVelocidade.Text := FBiblioteca.TestaLimite(EVelocidade.Text,Limite_VelMin,Limite_VelMax,2);
   VelMotorMed := EVelocidade.Text;
   FBiblioteca.GravarRegistro('VelMotorMed',VelMotorMed);
end;

procedure TFConfGeral.EAceleracaoExit(Sender: TObject);
begin
   EAceleracao.Text := FBiblioteca.TestaLimite(EAceleracao.Text,Limite_AceMin,Limite_AceMax,2);
   AceMotorMed := EAceleracao.Text;
   FBiblioteca.GravarRegistro('AceMotorMed',AceMotorMed);
end;

procedure TFConfGeral.ENVoltasExit(Sender: TObject);
begin
   ENVoltas.Text := FBiblioteca.TestaLimite(ENVoltas.Text,Limite_VoltasMin,Limite_VoltasMax,0);
   NVoltasMed := ENVoltas.Text;
   FBiblioteca.GravarRegistro('NVoltasMed',NVoltasMed);
end;

procedure TFConfGeral.EPulsosEncoderExit(Sender: TObject);
begin
   EPulsosEncoder.Text := FBiblioteca.TestaLimite(EPulsosEncoder.Text,Limite_PulsosEncoderMin,Limite_PulsosEncoderMax,0);
   PulsosEncoder := EPulsosEncoder.Text;
   FBiblioteca.GravarRegistro('PulsosEncoder',PulsosEncoder);
end;

procedure TFConfGeral.EPassosMotorExit(Sender: TObject);
begin
   EPassosMotor.Text := FBiblioteca.TestaLimite(EPassosMotor.Text,Limite_PassosMotorMin,Limite_PassosMotorMax,0);
   PassosMotor := IntToStr(StrToInt(EPassosMotor.Text)*-1);
   FBiblioteca.GravarRegistro('PassosMotor',PassosMotor);
end;

procedure TFConfGeral.CBPontosExit(Sender: TObject);
begin
   Npontos := IntToStr(CBPontos.ItemIndex);
   CBPontos.ItemIndex := StrToInt(Npontos);
   FBiblioteca.GravarRegistro('Npontos',Npontos);
end;

procedure TFConfGeral.ETriggerExit(Sender: TObject);
begin
   ETrigger.Text := FBiblioteca.TestaLimite(ETrigger.Text,0,Limite_PulsosEncoderMax,0);
   Trigger := ETrigger.Text;
   FBiblioteca.GravarRegistro('Trigger',Trigger);
end;

procedure TFConfGeral.EEndDriverExit(Sender: TObject);
begin
   EEndDriver.Text := FBiblioteca.TestaLimite(EEndDriver.Text,Limite_EndDriverMin,Limite_EndDriverMax,0);
   EndDriver := IntToStr(StrToInt(EEndDriver.Text)-1);
   FBiblioteca.GravarRegistro('EndDriver',EndDriver);
end;

end.
