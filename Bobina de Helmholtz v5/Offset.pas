unit Offset;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  ComCtrls, StdCtrls, Buttons, Biblioteca, Grids, Loco3, ExtCtrls;

type
  TFOffset = class(TForm)
    GBOffsets: TGroupBox;
    Label22: TLabel;
    SGOffsets: TStringGrid;
    GBAjusteOffset: TGroupBox;
    Label23: TLabel;
    CBGanhoOffset: TComboBox;
    BBCurtoIntegrador: TBitBtn;
    BBZerarOffset: TBitBtn;
    Label1: TLabel;
    ProgressOff: TProgressBar;
    BBMedirOffset: TBitBtn;
    BBPararOffset: TBitBtn;
    Label2: TLabel;
    ENVoltasOffset: TEdit;
    TimerStatus: TTimer;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure AtualizaValores;
    procedure FormShow(Sender: TObject);
    procedure BBCurtoIntegradorClick(Sender: TObject);
    procedure BBMedirOffsetClick(Sender: TObject);
    procedure BBZerarOffsetClick(Sender: TObject);
    procedure ENVoltasOffsetExit(Sender: TObject);
    procedure BBPararOffsetClick(Sender: TObject);
    procedure TimerStatusTimer(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    Pont_Jan: ^TFOffset
  end;

var
  FOffset: TFOffset;

implementation

uses Helmholtz_v5, Conexoes, ConfGeral, ConfBob, Medicao, Motores;

{$R *.DFM}

procedure TFOffset.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Pont_Jan^:=nil;
  Release;
  FHelmholtz.Show;
end;

procedure TFOffset.AtualizaValores;
begin
   ENVoltasOffset.Text := VoltasOffset;

{Cabeçalho Tabelas de Offsets}
   SGOffsets.Cells[0,1] := 'Ganho 1';
   SGOffsets.Cells[0,2] := 'Ganho 2';
   SGOffsets.Cells[0,3] := 'Ganho 5';
   SGOffsets.Cells[0,4] := 'Ganho 10';
   SGOffsets.Cells[0,5] := 'Ganho 20';
   SGOffsets.Cells[0,6] := 'Ganho 50';
   SGOffsets.Cells[0,7] := 'Ganho 100';
   SGOffsets.Cells[0,8] := 'Ganho 200';
   SGOffsets.Cells[0,9] := 'Ganho 500';
   SGOffsets.Cells[0,10] := 'Ganho 1000';
   SGOffsets.Cells[1,0] := 'Offsets';
{********}

   FBiblioteca.GravarRegistro('Offset_G1',Offset_G1);
   FBiblioteca.GravarRegistro('Offset_G2',Offset_G2);
   FBiblioteca.GravarRegistro('Offset_G5',Offset_G5);
   FBiblioteca.GravarRegistro('Offset_G10',Offset_G10);
   FBiblioteca.GravarRegistro('Offset_G20',Offset_G20);
   FBiblioteca.GravarRegistro('Offset_G50',Offset_G50);
   FBiblioteca.GravarRegistro('Offset_G100',Offset_G100);
   FBiblioteca.GravarRegistro('Offset_G200',Offset_G200);
   FBiblioteca.GravarRegistro('Offset_G500',Offset_G500);
   FBiblioteca.GravarRegistro('Offset_G1000',Offset_G1000);

   SGOffsets.Cells[1,1] := Offset_G1;
   SGOffsets.Cells[1,2] := Offset_G2;
   SGOffsets.Cells[1,3] := Offset_G5;
   SGOffsets.Cells[1,4] := Offset_G10;
   SGOffsets.Cells[1,5] := Offset_G20;
   SGOffsets.Cells[1,6] := Offset_G50;
   SGOffsets.Cells[1,7] := Offset_G100;
   SGOffsets.Cells[1,8] := Offset_G200;
   SGOffsets.Cells[1,9] := Offset_G500;
   SGOffsets.Cells[1,10] := Offset_G1000;
  
end;

procedure TFOffset.FormShow(Sender: TObject);
begin
   AtualizaValores;
end;

procedure TFOffset.BBCurtoIntegradorClick(Sender: TObject);
var
aux : string;
begin
   if CBGanhoOffset.ItemIndex = -1 then
   begin
      MessageDlg('Selecione o ganho desejado!!!',mtWarning, [mbOk],0);
      Exit;
   end;

   try
      aux := CBGanhoOffset.Text;
      FBiblioteca.DispGPIB.Leitura(tmpGPIB,10);
      FBiblioteca.DispGPIB.Escrita(PDIConfiguraGanho + aux + CR); {Configura Ganho}
      delay(EsperaIntegrador);

      FBiblioteca.DispGPIB.Leitura(tmpGPIB,10);
      FBiblioteca.DispGPIB.Escrita(PDICurtoCircuito + '1' + CR); {Habilita Curto Entradas Integrador}
      delay(EsperaIntegrador);

      MessageDlg('Clique OK quando finalizar o ajuste offset!!!', mtInformation,[mbOk], 0);

      FBiblioteca.DispGPIB.Leitura(tmpGPIB,10);
      FBiblioteca.DispGPIB.Escrita(PDICurtoCircuito + '0' + CR);
      delay(EsperaIntegrador);
   except
      MessageDlg('Falha de comunicação com o integrador!!!', mtWarning,[mbOk], 0);
   end;
end;

procedure TFOffset.BBMedirOffsetClick(Sender: TObject);
begin
   if CBGanhoOffset.ItemIndex = -1 then
   begin
      MessageDlg('Selecione o ganho desejado!!!',mtWarning, [mbOk],0);
      Exit;
   end;

   {Desabilita botões}
   CBGanhoOffset.Enabled := False;
   BBCurtoIntegrador.Enabled := False;
   BBZerarOffset.Enabled := False;
   BBMedirOffset.Enabled :=False;
   {*****************}

   {Habilita botões}
   BBPararOffset.Enabled := True;
   {*****************}

   PararTudo := False;

   FBiblioteca.LimpaVariaveis;

   FBiblioteca.ConfiguraDriver(VelMotorMed,AceMotorMed);

   {Configura Integrador - Número de Voltas e Ganho}
   FBiblioteca.ConfiguraPDI(ENVoltasOffset.Text, CBGanhoOffset.Text);

   {Zera barra de progresso}
   ProgressOff.Position := 0;
   TimerStatus.Enabled := True;

   FBiblioteca.Seleciona_Offset(CBGanhoOffset.ItemIndex);

   {Executa Medida Integrador - Número de Voltas}
   FBiblioteca.ExecutaPDI(ENVoltasOffset.Text);

   if FBiblioteca.VerificaSaturacao then
      PararTudo := True;

   if PararTudo = False then
   begin
      if FBiblioteca.ColetaDados(VetorColetas) then
         FBiblioteca.CalculaMediaDesvio(CBGanhoOffset.ItemIndex,ENVoltasOffset.Text, True);
   end;

   AtualizaValores;

   {Habilita botões}
   CBGanhoOffset.Enabled := True;
   BBCurtoIntegrador.Enabled := True;
   BBZerarOffset.Enabled := True;
   BBMedirOffset.Enabled := True;
  {*****************}

   {Desabilita botões}
   BBPararOffset.Enabled := False;
   {*****************}

   ProgressOff.Position := 0;
   TimerStatus.Enabled := False;

   if PararTudo = False  then
      MessageDlg('Medição de Offset Finalizada!',mtInformation, [mbOk],0)
   else
      MessageDlg('Falha na Medição de Offset!',mtWarning, [mbOk],0);
end;

procedure TFOffset.BBZerarOffsetClick(Sender: TObject);
begin
   if CBGanhoOffset.ItemIndex = -1 then
   begin
      Case MessageDlg('Deseja realmente zerar todos os valores de offset?',mtConfirmation, [mbYes, mbNo],0) of
         mrYes:begin
                  Offset_G1    := '0';
                  Offset_G2    := '0';
                  Offset_G5    := '0';
                  Offset_G10   := '0';
                  Offset_G20   := '0';
                  Offset_G50   := '0';
                  Offset_G100  := '0';
                  Offset_G200  := '0';
                  Offset_G500  := '0';
                  Offset_G1000 := '0';
               end;
         mrNo:begin
                 MessageDlg('Procedimento Cancelado!',mtInformation, [mbOk],0);
                 exit;
              end;
      End;
   end
   else
   begin
      Case MessageDlg('Deseja realmente zerar o offset selecionado?',mtConfirmation, [mbYes, mbNo],0) of
         mrYes:begin
                  Case CBGanhoOffset.ItemIndex of
                     0: Offset_G1    := '0';
                     1: Offset_G2    := '0';
                     2: Offset_G5    := '0';
                     3: Offset_G10   := '0';
                     4: Offset_G20   := '0';
                     5: Offset_G50   := '0';
                     6: Offset_G100  := '0';
                     7: Offset_G200  := '0';
                     8: Offset_G500  := '0';
                     9: Offset_G1000 := '0';
                  End;
               end;
         mrNo:begin
                 MessageDlg('Procedimento Cancelado!',mtInformation, [mbOk],0);
                 exit;
              end;
      End;
   end;
   AtualizaValores;

   MessageDlg('Procedimento Finalizado. Dados salvos no registro!',mtInformation, [mbOk],0);
end;

procedure TFOffset.ENVoltasOffsetExit(Sender: TObject);
begin
   ENVoltasOffset.Text := FBiblioteca.TestaLimite(ENVoltasOffset.Text,Limite_VoltasMin,Limite_VoltasMax,0);
   VoltasOffset := ENVoltasOffset.Text;
   FBiblioteca.GravarRegistro('VoltasOffset',VoltasOffset);
end;

procedure TFOffset.BBPararOffsetClick(Sender: TObject);
begin
   PararTudo := True;
end;

procedure TFOffset.TimerStatusTimer(Sender: TObject);
begin
   TimerStatus.Enabled := False;

   ProgressOff.Max := 10;

   if (ProgressOff.Position = ProgressOff.Max) then
      ProgressOff.Position := 0;

   ProgressOff.Position := ProgressOff.Position + 1;

   TimerStatus.Enabled := True;
end;

end.
