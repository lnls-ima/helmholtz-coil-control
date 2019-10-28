unit Medicao;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  StdCtrls, Buttons, ComCtrls, Biblioteca, ExtCtrls, ShellApi;

type
  TFMedicao = class(TForm)
    GBMedicao: TGroupBox;
    Label18: TLabel;
    Label19: TLabel;
    CBGanhoMZ: TComboBox;
    ProgressM: TProgressBar;
    CBGanhoMX: TComboBox;
    CBGanhoMY: TComboBox;
    CBMX: TCheckBox;
    CBMZ: TCheckBox;
    CBMY: TCheckBox;
    GBMedicaoStartEnd: TGroupBox;
    BBIniciarMedida: TBitBtn;
    BBPararMedida: TBitBtn;
    CBDimensoes: TComboBox;
    Label1: TLabel;
    Label2: TLabel;
    EVolumeBloco: TEdit;
    Label3: TLabel;
    Label4: TLabel;
    Label5: TLabel;
    Label6: TLabel;
    TimerStatus: TTimer;
    BBResults: TBitBtn;
    SBFolder: TSpeedButton;
    CBSalvaResumo: TCheckBox;
    ESubtraiVol: TEdit;
    Label8: TLabel;
    Label9: TLabel;
    CBSubtraiVol: TCheckBox;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormShow(Sender: TObject);
    procedure AtualizaValores;
    procedure CBMZClick(Sender: TObject);
    procedure CBGanhoMZChange(Sender: TObject);
    procedure CBGanhoMXChange(Sender: TObject);
    procedure CBGanhoMYChange(Sender: TObject);
    procedure CBDimensoesChange(Sender: TObject);
    procedure SalvaSequencia;
    procedure Calcula_Volume;
    procedure BBIniciarMedidaClick(Sender: TObject);
    procedure BBPararMedidaClick(Sender: TObject);
    procedure GuardaResultados(atual : integer);
    procedure CriaArquivoSaida;
    procedure SalvaResultados;
    procedure SalvaResultadosResumo;
    procedure LimpaResultados;
    procedure TimerStatusTimer(Sender: TObject);
    procedure CBMXClick(Sender: TObject);
    procedure CBMYClick(Sender: TObject);
    procedure BBResultsClick(Sender: TObject);
    procedure SBFolderClick(Sender: TObject);
    procedure CBSubtraiVolClick(Sender: TObject);
    procedure ESubtraiVolExit(Sender: TObject);

  private
    { Private declarations }
  public
    { Public declarations }
    Pont_Jan: ^TFMedicao
  end;

var
  FMedicao: TFMedicao;
  Resultados1 : Array[0..1,0..511] of Extended;
  Resultados2 : Array[0..1,0..511] of Extended;
  Resultados3 : Array[0..1,0..511] of Extended;
  LockComp : boolean;

implementation

uses Helmholtz_v4, Conexoes, ConfGeral, ConfBob, Offset, Motores, Resultados;

{$R *.DFM}

procedure TFMedicao.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Pont_Jan^:=nil;
  Release;
  FHelmholtz.Show;
end;

procedure TFMedicao.FormShow(Sender: TObject);
begin
   AtualizaValores;
end;

procedure TFMedicao.AtualizaValores;
var
i : integer;
begin
   Case StrToInt(Aciona_MZ) of
      0: CBMZ.Checked := False;
      1: CBMZ.Checked := True;
   End;

   Case StrToInt(Aciona_MX) of
      0: CBMX.Checked := False;
      1: CBMX.Checked := True;
   End;

   Case StrToInt(Aciona_MY) of
      0: CBMY.Checked := False;
      1: CBMY.Checked := True;
   End;

   CBGanhoMZ.ItemIndex := StrToInt(Ganho_MZ);
   CBGanhoMX.ItemIndex := StrToInt(Ganho_MX);
   CBGanhoMY.ItemIndex := StrToInt(Ganho_MY);

   CBDimensoes.Items.Clear;
   for i:=0 to 4 do
   begin
      CBDimensoes.Items.Add(Dimensoes_Blocos[i]);
   end;
   CBDimensoes.Items.Add('Nova dimensão manual...');
   CBDimensoes.Items.Add('Nova dimensão automática...');
   CBDimensoes.ItemIndex := 0;

   ESubtraiVol.Text := FloatToStrF(SubtraiVol,ffFixed,10,12);

   Calcula_Volume;
end;

procedure TFMedicao.CBMZClick(Sender: TObject);
begin
   if CBMZ.Checked = True then
   begin
      Aciona_MZ := '1';
      CBGanhoMZ.Enabled := True;
   end
   else
   begin
      Aciona_MZ := '0';
      CBGanhoMZ.Enabled := False;
   end;
   FBiblioteca.GravarRegistro('Aciona_MZ',Aciona_MZ);
end;

procedure TFMedicao.CBGanhoMZChange(Sender: TObject);
begin
   Ganho_MZ := IntToStr(CBGanhoMZ.ItemIndex);
   FBiblioteca.GravarRegistro('Ganho_MZ',Ganho_MZ);
end;

procedure TFMedicao.CBGanhoMXChange(Sender: TObject);
begin
   Ganho_MX := IntToStr(CBGanhoMX.ItemIndex);
   FBiblioteca.GravarRegistro('Ganho_MX',Ganho_MX);
end;

procedure TFMedicao.CBGanhoMYChange(Sender: TObject);
begin
   Ganho_MY := IntToStr(CBGanhoMY.ItemIndex);
   FBiblioteca.GravarRegistro('Ganho_MY',Ganho_MY);
end;

procedure TFMedicao.CBDimensoesChange(Sender: TObject);
var
aux : string;
valor : double;
Dim : string;
begin
   Case CBDimensoes.ItemIndex of
      0: begin
            SalvaSequencia;
         end;
      1: begin
            aux := Dimensoes_Blocos[0];
            Dimensoes_Blocos[0] := Dimensoes_Blocos[CBDimensoes.ItemIndex];
            Dimensoes_Blocos[CBDimensoes.ItemIndex] := aux;
            SalvaSequencia;
         end;
      2: begin
            aux := Dimensoes_Blocos[0];
            Dimensoes_Blocos[0] := Dimensoes_Blocos[CBDimensoes.ItemIndex];
            Dimensoes_Blocos[CBDimensoes.ItemIndex] := aux;
            SalvaSequencia;
         end;
      3: begin
            aux := Dimensoes_Blocos[0];
            Dimensoes_Blocos[0] := Dimensoes_Blocos[CBDimensoes.ItemIndex];
            Dimensoes_Blocos[CBDimensoes.ItemIndex] := aux;
            SalvaSequencia;
         end;
      4: begin
            aux := Dimensoes_Blocos[0];
            Dimensoes_Blocos[0] := Dimensoes_Blocos[CBDimensoes.ItemIndex];
            Dimensoes_Blocos[CBDimensoes.ItemIndex] := aux;
            SalvaSequencia;
         end;
      5: begin
            {Primeira dimensáo}
            try
               valor := StrToFloat(InputBox('Dimensão bloco - Primeira', 'Entre com o comprimento do bloco em milímetros.', '1'));
               Dim:= FloatToStr(valor);
            except
               MessageDlg('Valor inconsistente. Entradas Canceladas!!!',mtWarning, [mbOk],0);
               CBDimensoes.ItemIndex := -1;
               exit;
            end;
            {Segunda dimensáo}
            try
               valor := StrToFloat(InputBox('Dimensão bloco - Segunda', 'Entre com a largura do bloco em milímetros.', '1'));
               Dim:= Dim + ' mm x '+ FloatToStr(valor);
            except
               MessageDlg('Valor inconsistente. Entradas Canceladas!!!',mtWarning, [mbOk],0);
               CBDimensoes.ItemIndex := -1;
               exit;
            end;

            {Terceira dimensáo}
            try
               valor := StrToFloat(InputBox('Dimensão bloco - Terceira', 'Entre com a espessura do bloco em milímetros.', '1'));
               Dim:= Dim + ' mm x '+ FloatToStr(valor);
               Dim:= Dim + ' mm';
            except
               MessageDlg('Valor inconsistente. Entradas Canceladas!!!',mtWarning, [mbOk],0);
               CBDimensoes.ItemIndex := -1;
               exit;
            end;

            Dimensoes_Blocos[4] := Dimensoes_Blocos[3];
            Dimensoes_Blocos[3] := Dimensoes_Blocos[2];
            Dimensoes_Blocos[2] := Dimensoes_Blocos[1];
            Dimensoes_Blocos[1] := Dimensoes_Blocos[0];
            Dimensoes_Blocos[0] := Dim;
            SalvaSequencia;
         end;
      6: begin
            MessageDlg('Insira o bloco no sistema de apalpadores para medir as dimensões!!!',mtInformation, [mbOk],0);
            FBiblioteca.Ler_Medidor_Pneumatico;

            Dim := DispA + ' mm x ' + DispB + ' mm x ' + DispC + ' mm';

            Dimensoes_Blocos[4] := Dimensoes_Blocos[3];
            Dimensoes_Blocos[3] := Dimensoes_Blocos[2];
            Dimensoes_Blocos[2] := Dimensoes_Blocos[1];
            Dimensoes_Blocos[1] := Dimensoes_Blocos[0];
            Dimensoes_Blocos[0] := Dim;
            SalvaSequencia;
         end;
   End;
   CBDimensoes.ItemIndex := 0;
   Calcula_Volume;
end;

procedure TFMedicao.SalvaSequencia;
var
i : integer;
Nome : string;
begin
   for i:=0 to 4 do
   begin
      Nome := 'Dim'+IntToStr(i+1);
      FBiblioteca.GravarRegistro(Nome,Dimensoes_Blocos[i]);
   end;

   CBDimensoes.Items.Clear;
   for i:=0 to 4 do
   begin
      CBDimensoes.Items.Add(Dimensoes_Blocos[i]);
   end;
   CBDimensoes.Items.Add('Nova dimensão manual...');
   CBDimensoes.Items.Add('Nova dimensão automática...');
end;

procedure TFMedicao.Calcula_Volume;
var
aux: string;
tmp : string;
iPos : integer;
begin
   VolumeBloco := 0;
   tmp := CBDimensoes.Text;
   iPos := Pos(' mm',tmp)-1;
   aux := Copy(tmp,1,iPos);
   tmp := Copy(tmp,iPos+7,length(tmp));
   ComprimentoBloco := StrToFloat(aux);

   iPos := Pos(' mm',tmp)-1;
   aux := Copy(tmp,1,iPos);
   tmp := Copy(tmp,iPos+7,length(tmp));
   LarguraBloco := StrToFloat(aux);

   iPos := Pos(' mm',tmp)-1;
   aux := Copy(tmp,1,iPos);
   EspessuraBloco := StrToFloat(aux);

   {Converte de milímetros para metros}
   VolumeBloco := (ComprimentoBloco * LarguraBloco * EspessuraBloco)/1E9;

   if CBSubtraiVol.Checked = True then
   begin
        VolumeBloco := VolumeBloco - SubtraiVol;
   end;

   EVolumeBloco.Text := FloatToStr(VolumeBloco);
end;

procedure TFMedicao.BBIniciarMedidaClick(Sender: TObject);
begin
   if CBDimensoes.ItemIndex = -1 then
   begin
      MessageDlg('Selecione a dimensão do bloco desejada!!!',mtWarning, [mbOk],0);
      exit;
   end;

   if (CBMZ.Checked = False) and (CBMX.Checked = False) and (CBMY.Checked = False) then
   begin
      MessageDlg('Selecione ao menos uma componente a ser medida!!!',mtWarning, [mbOk],0);
      exit;
   end;

   if (CBMZ.Checked = True) and (CBGanhoMZ.ItemIndex = -1) then
   begin
      MessageDlg('Selecione o ganho da componente a ser medida!!!',mtWarning, [mbOk],0);
      exit;
   end;

   if (CBMX.Checked = True) and (CBGanhoMX.ItemIndex = -1) then
   begin
      MessageDlg('Selecione o ganho da componente a ser medida!!!',mtWarning, [mbOk],0);
      exit;
   end;

   if (CBMY.Checked = True) and (CBGanhoMY.ItemIndex = -1) then
   begin
      MessageDlg('Selecione o ganho da componente a ser medida!!!',mtWarning, [mbOk],0);
      exit;
   end;

   {Habilita / Desabilita}
   GBMedicao.Enabled := False;
   BBIniciarMedida.Enabled := False;
   BBPararMedida.Enabled := True;
   BBResults.Enabled := False;
   SBFolder.Enabled := False;
   //try
//      FResults.Close;
//   except
//   end;
   {*********************}

   MessageDlg('Selecione a chave de configuração da bobina: série ou paralela!',mtWarning, [mbOk],0);
   PararTudo := False;
   LockComp := False;

   if (CBMX.Checked = True) and (CBMY.Checked = True) then
   begin
      Case MessageDlg('Deseja medir as componentes secundárias juntas?',mtConfirmation, [mbYes, mbNo],0) of
         mrYes: begin
                   LockComp:= True;
                   MessageDlg('Será utilizado o ganho selecionado para Mx',mtConfirmation, [mbOk],0);
                end;
         mrNo : LockComp:= False;
      End;
   end;

   NumeroBloco := InputBox('Identificação numérica do bloco', 'Entre com a identificação do bloco para registro.', '');

   TemperaturaBloco := InputBox('Temperatura do Bloco', 'Entre com a temperatura do bloco (°C).', '23');

   CriaArquivoSaida;

   LimpaResultados;

   {Componente 1 - MZ}
   if (CBMZ.Checked = True) and (PararTudo = False) then
   begin
      MessageDlg('Insira o magneto para medir a componente MZ!',mtWarning, [mbOk],0);

      FBiblioteca.LimpaVariaveis;
      FBiblioteca.ConfiguraDriver(VelMotorMed,AceMotorMed);

      {Configura Integrador - Número de Voltas e Ganho}
      FBiblioteca.ConfiguraPDI(NVoltasMed, CBGanhoMZ.Text);

      {Zera barra de progresso}
      ProgressM.Position := 0;
      TimerStatus.Enabled := True;

      FBiblioteca.Seleciona_Offset(CBGanhoMZ.ItemIndex);

      {Executa Medida Integrador - Número de Voltas}
      FBiblioteca.ExecutaPDI(NVoltasMed);

      if PararTudo = False then
      begin
         if FBiblioteca.ColetaDados(VetorColetas) then
         begin
            FBiblioteca.CalculaMediaDesvio(CBGanhoMZ.ItemIndex,NVoltasMed, False);
            FBiblioteca.CalculaMag(NVoltasMed);
            GuardaResultados(0);
            Mz := MagNormal;
            Mz2:= Mag2Normal;
         end;
      end;

      ProgressM.Position := 0;
      TimerStatus.Enabled := False;
   end;

   {Componente 2 e 3 ou 2 - MX e MY ou MX}
   if (CBMX.Checked = True) and (PararTudo = False) then
   begin
      if (LockComp = True) then
         MessageDlg('Insira o magneto para medir as componentes MX e MY!',mtWarning, [mbOk],0)
      else
         MessageDlg('Insira o magneto para medir as componentes MX!',mtWarning, [mbOk],0);

      FBiblioteca.LimpaVariaveis;
      FBiblioteca.ConfiguraDriver(VelMotorMed,AceMotorMed);

      {Configura Integrador - Número de Voltas e Ganho}
      FBiblioteca.ConfiguraPDI(NVoltasMed, CBGanhoMX.Text);

      {Zera barra de progresso}
      ProgressM.Position := 0;
      TimerStatus.Enabled := True;

      FBiblioteca.Seleciona_Offset(CBGanhoMX.ItemIndex);

      {Executa Medida Integrador - Número de Voltas}
      FBiblioteca.ExecutaPDI(NVoltasMed);

      if PararTudo = False then
      begin
         if FBiblioteca.ColetaDados(VetorColetas) then
         begin
            FBiblioteca.CalculaMediaDesvio(CBGanhoMX.ItemIndex,NVoltasMed, False);
            FBiblioteca.CalculaMag(NVoltasMed);
            GuardaResultados(1);

            Mx := MagSkew;
            Mx2:= Mag2Skew;

            if LockComp = True then
            begin
               My := MagNormal;
               My2:= Mag2Normal;
            end;
         end;
      end;

      ProgressM.Position := 0;
      TimerStatus.Enabled := False;
   end;

   if (CBMY.Checked = True) and (LockComp = False) and (PararTudo = False) then
   begin
   {Componente 2 ou 3 - MX - MY}
      MessageDlg('Insira o magneto para medir a componente MY!',mtWarning, [mbOk],0);

      FBiblioteca.LimpaVariaveis;
      FBiblioteca.ConfiguraDriver(VelMotorMed,AceMotorMed);

      {Configura Integrador - Número de Voltas e Ganho}
      FBiblioteca.ConfiguraPDI(NVoltasMed, CBGanhoMY.Text);

      {Zera barra de progresso}
      ProgressM.Position := 0;            
      TimerStatus.Enabled := True;

      FBiblioteca.Seleciona_Offset(CBGanhoMY.ItemIndex);

      {Executa Medida Integrador - Número de Voltas}
      FBiblioteca.ExecutaPDI(NVoltasMed);

      if PararTudo = False then
      begin
         if FBiblioteca.ColetaDados(VetorColetas) then
         begin
            FBiblioteca.CalculaMediaDesvio(CBGanhoMY.ItemIndex,NVoltasMed, False);
            FBiblioteca.CalculaMag(NVoltasMed);
            GuardaResultados(2);

            My := MagNormal;
            My2:= Mag2Normal;
         end;
      end;

      ProgressM.Position := 0;
      TimerStatus.Enabled := False;
   end;

   if PararTudo = False then
   begin
      SalvaResultados;
      if CBSalvaResumo.Checked = True then
      begin
         SalvaResultadosResumo;
      end;
      MessageDlg('Caracterização Finalizada!!!',mtInformation, [mbOk],0);
   end
   else
   begin
      MessageDlg('Caracterização Cancelada!!!',mtInformation, [mbOk],0);
   end;

   {Habilita / Desabilita}
   GBMedicao.Enabled := True;
   BBIniciarMedida.Enabled := True;
   BBPararMedida.Enabled := False;
   BBResults.Enabled := True;
   SBFolder.Enabled := True;
   TimerStatus.Enabled := False;
   {*********************}
end;

procedure TFMedicao.BBPararMedidaClick(Sender: TObject);
begin
    PararTudo := True;
end;

procedure TFMedicao.GuardaResultados(atual : integer);
var
i : integer;
begin
   Case atual of
   0: begin
         for i:=0 to 511 do
         begin
            Resultados1[0,i] := VetorMedia[i];
            Resultados1[1,i] := VetorDesvio[i];
         end;
      end;
   1: begin
         for i:=0 to 511 do
         begin
            Resultados2[0,i] := VetorMedia[i];
            Resultados2[1,i] := VetorDesvio[i];
         end;
      end;
   2: begin
         for i:=0 to 511 do
         begin
            Resultados3[0,i] := VetorMedia[i];
            Resultados3[1,i] := VetorDesvio[i];
         end;
      end;
   End;
end;

procedure TFMedicao.CriaArquivoSaida;
label Volta;
begin
Volta:
   FBiblioteca.SDArq.InitialDir := Dir;
   FBiblioteca.SDArq.FileName := Dir + FormatDateTime('"HelmHoltz_"dd-mm-yy_hh"h"mm"min_"',now) + NumeroBloco + '.dat' ;
   if FBiblioteca.SDArq.Execute then
   begin
      if fileexists(FBiblioteca.SDArq.FileName) then
      begin
         Case MessageDlg('Arquivo já existente, deseja substituir?',mtConfirmation, [mbYes, mbNo],0) of
         mrYes: begin
                   AssignFile(Arq,FBiblioteca.SDArq.FileName);
                   Rewrite(Arq);
                   Closefile(Arq);
                end;
         mrNo: begin
                  Goto Volta;
               end;
         End;
      end
      else
      begin
          AssignFile(Arq,FBiblioteca.SDArq.FileName);
          Rewrite(Arq);
          Closefile(Arq);
      end;
   end
   else
   begin
      PararTudo := True;
   end;
end;

procedure TFMedicao.SalvaResultados;
var
i : integer;
hora : string;
data : string;
begin
   try
      hora := TimeToStr(Time);
   except
      hora := '---';
   end;

   try
      data := DateToStr(Date);
   except
      data := '---';
   end;

   AssignFile(Arq,FBiblioteca.SDArq.FileName);
   Rewrite(Arq);
   Writeln(Arq,'Resultados da caracterização com bobina de helmholtz');
   Writeln(Arq,'');
   Writeln(Arq, 'Data..................: ' + data);
   Writeln(Arq, 'Hora..................: ' + hora);
   Writeln(Arq, 'N. de Voltas..........: ' + NVoltasMed);
   Writeln(Arq, 'Offset................: ' + FloatToStr(ValorOffset));
   Writeln(Arq, 'Temperatura do Bloco..: ' + TemperaturaBloco);
   Writeln(Arq, 'Dimensão do Bloco.....: ' + CBDimensoes.Text);
   Writeln(Arq, 'Volume do Bloco (m2)..: ' + EVolumeBloco.Text);
   if CBMZ.Checked = True then
      Writeln(Arq, 'Ganho MZ.........: ' + CBGanhoMZ.Text)
   else
      Writeln(Arq, 'Ganho MZ.........: ' + '---');

   if CBMX.Checked = True then
      Writeln(Arq, 'Ganho MX.........: ' + CBGanhoMX.Text)
   else
      Writeln(Arq, 'Ganho MX.........: ' + '---');

   if CBMY.Checked = True then
      Writeln(Arq, 'Ganho MY.........: ' + CBGanhoMY.Text)
   else
      Writeln(Arq, 'Ganho MY.........: ' + '---');

   Writeln(Arq,'');
   Writeln(Arq,'Magnetizações');
   Writeln(Arq,'');

   if CBMZ.Checked = True then
   begin
      Writeln(Arq,'Media MZ.....: '+ FloatToStr(Mz));
      Writeln(Arq,'Desvio MZ....: '+ FloatToStr(Mz2));
   end
   else
   begin
      Writeln(Arq,'Media MZ.....: '+ '---');
      Writeln(Arq,'Desvio MZ....: '+ '---');
   end;

   if CBMX.Checked = True then
   begin
      Writeln(Arq,'Media MX.....: '+ FloatToStr(Mx));
      Writeln(Arq,'Desvio MX....: '+ FloatToStr(Mx2));
   end
   else
   begin
      Writeln(Arq,'Media MX.....: '+ '---');
      Writeln(Arq,'Desvio MX....: '+ '---');
   end;

   if CBMY.Checked = True then
   begin
      Writeln(Arq,'Media MY.....: '+ FloatToStr(My));
      Writeln(Arq,'Desvio MY....: '+ FloatToStr(My2));
   end
   else
   begin
      Writeln(Arq,'Media MY.....: '+ '---');
      Writeln(Arq,'Desvio MY....: '+ '---');
   end;

   Writeln(Arq,'');
   Writeln(Arq,'Dados Brutos');
   Writeln(Arq,'');
   Writeln(Arq,'Media Mz'+#9+'Desvio Mz'+#9+'Media Mx'+#9+'Desvio Mx'+#9+'Media My'+#9+'Desvio My');

   for i:=0 to NPontosPDI-1 do
   begin
      Writeln(Arq,FloatToStr(Resultados1[0,i])+#9+FloatToStr(Resultados1[1,i])+#9+FloatToStr(Resultados2[0,i])+#9+FloatToStr(Resultados2[1,i])+#9+FloatToStr(Resultados3[0,i])+#9+FloatToStr(Resultados3[1,i]));
   end;

   Closefile(Arq);
end;

procedure TFMedicao.SalvaResultadosResumo;
var
data : string;
begin
   try
      data := DateToStr(Date);
   except
      data := '---';
   end;

   if fileexists(Arquivo_Resumo) then
   begin
       AssignFile(Arq,Arquivo_Resumo);
       Append(Arq);
   end
   else
   begin
       AssignFile(Arq,Arquivo_Resumo);
       Rewrite(Arq);
       WriteLn(Arq,'Data'+#9+'NumBloco'+#9+'Mx'+#9+'DesvioMx'+#9+'My'+#9+'DesvioMy'+#9+'Mz'+#9+'DesvioMz'+#9+'Comprimento'+#9+'Largura'+#9+'Espessura'+#9+'Temperatura');
   end;

   if CBMZ.Checked = False then
   begin
      Mz := 0;
      Mz2 := 0;
   end;

   if CBMX.Checked = False then
   begin
      Mx := 0;
      Mx2 := 0;
   end;

   if CBMY.Checked = False then
   begin
      My := 0;
      My2 := 0;
   end;

   WriteLn(Arq,data+#9+NumeroBloco+#9+FloatToStr(Mx)+#9+FloatToStr(Mx2)+#9+FloatToStr(My)+#9+FloatToStr(My2)+#9+FloatToStr(Mz)+#9+FloatToStr(Mz2)+#9+FloatToStrF(ComprimentoBloco,ffFixed,10,3)+#9+FloatToStrF(LarguraBloco,ffFixed,10,3)+#9+FloatToStrF(EspessuraBloco,ffFixed,10,3)+#9+TemperaturaBloco);

   Closefile(Arq);
end;


procedure TFMedicao.LimpaResultados;
var
i : integer;
begin
   for i:=0 to 511 do
   begin
      Resultados1[0,i] := 0;
      Resultados1[1,i] := 0;

      Resultados2[0,i] := 0;
      Resultados2[1,i] := 0;

      Resultados3[0,i] := 0;
      Resultados3[1,i] := 0;
   end;
   Mx := 0;
   Mx2:=0;
   My := 0;
   My2:=0;
   Mz := 0;
   Mz2:=0;
end;

procedure TFMedicao.TimerStatusTimer(Sender: TObject);
begin
   TimerStatus.Enabled := False;

   ProgressM.Max := 10;

   if (ProgressM.Position = ProgressM.Max) then
      ProgressM.Position := 0;

   ProgressM.Position := ProgressM.Position + 1;

   TimerStatus.Enabled := True;
end;

procedure TFMedicao.CBMXClick(Sender: TObject);
begin
   if CBMX.Checked = True then
   begin
      Aciona_MX := '1';
      CBGanhoMX.Enabled := True;
   end
   else
   begin
      Aciona_MX := '0';
      CBGanhoMX.Enabled := False;
   end;
   FBiblioteca.GravarRegistro('Aciona_MX',Aciona_MX);
end;

procedure TFMedicao.CBMYClick(Sender: TObject);
begin
   if CBMY.Checked = True then
   begin
      Aciona_MY := '1';
      CBGanhoMY.Enabled := True;
   end
   else
   begin
      Aciona_MY := '0';
      CBGanhoMY.Enabled := False;
   end;
   FBiblioteca.GravarRegistro('Aciona_MY',Aciona_MY);
end;


procedure TFMedicao.BBResultsClick(Sender: TObject);
begin
  if FResults<>nil then
  begin
    FResults.BringToFront;
    FMedicao.Hide;
    FResults.Show;
  end
  else
    try
      Application.CreateForm(TFResults, FResults);
      FResults.Pont_Jan:=@FResults;
      FMedicao.Hide;
      FResults.Show;
    except
      FResults.Release;
    end;
end;

procedure TFMedicao.SBFolderClick(Sender: TObject);
begin
   if FBiblioteca.SDArq.FileName <> '' then
      ShellExecute(FMedicao.Handle, 'open', PChar(ExtractFilePath(FBiblioteca.SDArq.Filename)), nil, nil, SW_NORMAL)
   else
      MessageDlg('Sem nenhum endereço na memória!!!',mtInformation, [mbOk],0);

end;

procedure TFMedicao.CBSubtraiVolClick(Sender: TObject);
begin
     if CBSubtraiVol.Checked = True then
     begin
          ESubtraiVol.Enabled := True;
     end
     else
     begin
          ESubtraiVol.Enabled := False;
     end;
     Calcula_Volume;
end;

procedure TFMedicao.ESubtraiVolExit(Sender: TObject);
var
tmp : string;
aux : double;
begin
   tmp := ESubtraiVol.Text;
   try
      aux := StrToFloat(tmp);
   except
      aux := 0;
   end;

   SubtraiVol := aux;
   FBiblioteca.GravarRegistro('Subtrai_Volume',FloatToStr(SubtraiVol));

   Calcula_Volume;
end;

end.
