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
    Label5: TLabel;
    Label6: TLabel;
    BBResults: TBitBtn;
    SBFolder: TSpeedButton;
    CBSalvaResumo: TCheckBox;
    ESubtraiVol: TEdit;
    Label8: TLabel;
    Label9: TLabel;
    CBSubtraiVol: TCheckBox;
    TimerStatus: TTimer;
    ENomeBloco: TEdit;
    Label10: TLabel;
    ETemperaturaBloco: TEdit;
    Label11: TLabel;
    CBMXMY: TCheckBox;
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
    procedure EVolumeBlocoExit(Sender: TObject);
    procedure ENomeBlocoChange(Sender: TObject);
    procedure ETemperaturaBlocoChange(Sender: TObject);

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

uses Helmholtz_v5, Conexoes, ConfGeral, ConfBob, Offset, Motores, Resultados;

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
   CBDimensoes.Items.Add('Nova dimens�o manual...');
   CBDimensoes.Items.Add('Nova dimens�o autom�tica...');
   CBDimensoes.ItemIndex := 0;

   ESubtraiVol.Text := FloatToStr(SubtraiVol*1E9);

   ENomeBloco.Text := NumeroBloco;
   ETemperaturaBloco.Text := TemperaturaBloco;

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
            {Primeira dimens�o}
            try
               valor := StrToFloat(InputBox('Dimens�o bloco - Primeira', 'Entre com o comprimento do bloco em mil�metros.', '1'));
               Dim:= FloatToStr(valor);
            except
               MessageDlg('Valor inconsistente. Entradas Canceladas!!!',mtWarning, [mbOk],0);
               CBDimensoes.ItemIndex := -1;
               exit;
            end;
            {Segunda dimens�o}
            try
               valor := StrToFloat(InputBox('Dimens�o bloco - Segunda', 'Entre com a largura do bloco em mil�metros.', '1'));
               Dim:= Dim + ' mm x '+ FloatToStr(valor);
            except
               MessageDlg('Valor inconsistente. Entradas Canceladas!!!',mtWarning, [mbOk],0);
               CBDimensoes.ItemIndex := -1;
               exit;
            end;

            {Terceira dimens�o}
            try
               valor := StrToFloat(InputBox('Dimens�o bloco - Terceira', 'Entre com a espessura do bloco em mil�metros.', '1'));
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
            MessageDlg('Insira o bloco no sistema de apalpadores para medir as dimens�es!!!',mtInformation, [mbOk],0);
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
   CBDimensoes.Items.Add('Nova dimens�o manual...');
   CBDimensoes.Items.Add('Nova dimens�o autom�tica...');
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

   {Converte de mil�metros para metros}
   VolumeBloco := (ComprimentoBloco * LarguraBloco * EspessuraBloco)/1E9;

   if CBSubtraiVol.Checked = True then
   begin
        VolumeBloco := VolumeBloco - SubtraiVol;
   end;

   EVolumeBloco.Text := FloatToStr(VolumeBloco*1E9);
end;

procedure TFMedicao.BBIniciarMedidaClick(Sender: TObject);
begin
   if CBDimensoes.ItemIndex = -1 then
   begin
      MessageDlg('Selecione a dimens�o do bloco desejada!!!',mtWarning, [mbOk],0);
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

   PararTudo := False;

   LockComp := False;
   if (CBMX.Checked = True) and (CBMY.Checked = True) and (CBMXMY.Checked = True) then
   begin
      LockComp:= True;
   end;

   CriaArquivoSaida;

   LimpaResultados;

   {Componente 1 - MZ}
   if (CBMZ.Checked = True) and (PararTudo = False) then
   begin
      MessageDlg('Insira o magneto para medir a componente MZ!',mtWarning, [mbOk],0);

      FBiblioteca.LimpaVariaveis;
      FBiblioteca.ConfiguraDriver(VelMotorMed,AceMotorMed);

      {Configura Integrador - N�mero de Voltas e Ganho}
      FBiblioteca.ConfiguraPDI(NVoltasMed, CBGanhoMZ.Text);

      {Zera barra de progresso}
      ProgressM.Position := 0;
      TimerStatus.Enabled := True;

      FBiblioteca.Seleciona_Offset(CBGanhoMZ.ItemIndex);

      {Executa Medida Integrador - N�mero de Voltas}
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

      {Configura Integrador - N�mero de Voltas e Ganho}
      FBiblioteca.ConfiguraPDI(NVoltasMed, CBGanhoMX.Text);

      {Zera barra de progresso}
      ProgressM.Position := 0;
      TimerStatus.Enabled := True;

      FBiblioteca.Seleciona_Offset(CBGanhoMX.ItemIndex);

      {Executa Medida Integrador - N�mero de Voltas}
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

      {Configura Integrador - N�mero de Voltas e Ganho}
      FBiblioteca.ConfiguraPDI(NVoltasMed, CBGanhoMY.Text);

      {Zera barra de progresso}
      ProgressM.Position := 0;            
      TimerStatus.Enabled := True;

      FBiblioteca.Seleciona_Offset(CBGanhoMY.ItemIndex);

      {Executa Medida Integrador - N�mero de Voltas}
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
      MessageDlg('Caracteriza��o Finalizada!!!',mtInformation, [mbOk],0);
   end
   else
   begin
      MessageDlg('Caracteriza��o Cancelada!!!',mtInformation, [mbOk],0);
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
var
Nome: string;
Valor: string;
InitialDir: string;
aux: string;
begin
Volta:
   try
      Nome := 'DirAnterior';
      FBiblioteca.LerRegistro(Nome,Valor);
      if Valor = '0' then
      begin
         InitialDir := Dir;
      end
      else
      begin
         InitialDir := Valor;
      end;
   except
      InitialDir := Dir;
   end;

   FBiblioteca.SDArq.InitialDir := InitialDir;
   FBiblioteca.SDArq.FileName := InitialDir + FormatDateTime('"HelmHoltz_"dd-mm-yy_hh"h"mm"min_"',now) + NumeroBloco + '.dat' ;
   if FBiblioteca.SDArq.Execute then
   begin
      try
         aux := ExtractFileDir(FBiblioteca.SDArq.FileName);
         if Length(aux) = 0 then
         begin
            aux := '0';
         end
         else
         begin
            aux := aux + '\';
         end;
         FBiblioteca.GravarRegistro('DirAnterior',aux);
      except
      end;

      if fileexists(FBiblioteca.SDArq.FileName) then
      begin
         Case MessageDlg('Arquivo j� existente, deseja substituir?',mtConfirmation, [mbYes, mbNo],0) of
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
volume: string;
tmp: double;
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

   try
      tmp := StrToFloat(EVolumeBloco.Text);
      tmp := tmp/1E9;
      volume := FloatToStr(tmp);
   except
      volume := '---';
   end;

   AssignFile(Arq,FBiblioteca.SDArq.FileName);
   Rewrite(Arq);
   Writeln(Arq,'Resultados da caracteriza��o com bobina de helmholtz');
   Writeln(Arq,'');
   Writeln(Arq, 'Data..................: ' + data);
   Writeln(Arq, 'Hora..................: ' + hora);
   Writeln(Arq, 'N. de Voltas..........: ' + NVoltasMed);
   Writeln(Arq, 'Offset................: ' + FloatToStr(ValorOffset));
   Writeln(Arq, 'Temperatura do Bloco..: ' + TemperaturaBloco);
   Writeln(Arq, 'Dimens�o do Bloco.....: ' + CBDimensoes.Text);
   Writeln(Arq, 'Volume do Bloco (m3)..: ' + volume);
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
   Writeln(Arq,'Magnetiza��es');
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

   if (CBMX.Checked = True) and (CBMY.Checked = True) then
      begin
         CBMXMY.Enabled := True;
         CBMXMY.Checked := True;
      end
   else
      begin
         CBMXMY.Enabled := False;
         CBMXMY.Checked := False;
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

   if (CBMX.Checked = True) and (CBMY.Checked = True) then
      begin
         CBMXMY.Enabled := True;
         CBMXMY.Checked := True;
      end
   else
      begin
         CBMXMY.Enabled := False;
         CBMXMY.Checked := False;
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
      MessageDlg('Sem nenhum endere�o na mem�ria!!!',mtInformation, [mbOk],0);

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
aux : string;
tmp : double;
begin
   aux := ESubtraiVol.Text;
   try
      tmp := StrToFloat(aux);
   except
      tmp := 0;
   end;

   SubtraiVol := tmp/1E9;
   FBiblioteca.GravarRegistro('Subtrai_Volume',FloatToStr(SubtraiVol));

   Calcula_Volume;
end;

procedure TFMedicao.EVolumeBlocoExit(Sender: TObject);
var
aux : string;
valor : double;
Dim : string;
begin
   aux := EVolumeBloco.Text;
   try
      valor := StrToFloat(aux);
      valor := valor;
      aux := FloatToStr(valor);
      Dim := aux + ' mm x 1 mm x 1 mm';

      Dimensoes_Blocos[4] := Dimensoes_Blocos[3];
      Dimensoes_Blocos[3] := Dimensoes_Blocos[2];
      Dimensoes_Blocos[2] := Dimensoes_Blocos[1];
      Dimensoes_Blocos[1] := Dimensoes_Blocos[0];
      Dimensoes_Blocos[0] := Dim;
      SalvaSequencia;
      CBDimensoes.ItemIndex := 0;

      Calcula_Volume;
   except
      MessageDlg('Valor inconsistente!!!',mtWarning, [mbOk],0);
      exit;
   end;

end;

procedure TFMedicao.ENomeBlocoChange(Sender: TObject);
begin
   NumeroBloco := ENomeBloco.Text;
   FBiblioteca.GravarRegistro('NumeroBloco',NumeroBloco);
end;

procedure TFMedicao.ETemperaturaBlocoChange(Sender: TObject);
begin
   TemperaturaBloco := ETemperaturaBloco.Text;
   FBiblioteca.GravarRegistro('TemperaturaBloco',TemperaturaBloco);
end;

end.
