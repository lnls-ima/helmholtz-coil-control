unit Biblioteca;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs, Registry,
  ExtCtrls, Loco3, Math;

type
  TFBiblioteca = class(TForm)
    PlacaGPIB: TPlacaGPIB;
    DispGPIB: TDispGPIB;
    SDArq: TSaveDialog;
    TimerEnc: TTimer;
    Parker: TMotParker;
    RSDisplay1: TRs232;
    procedure GravarRegistro(Nome,Valor: String);
    procedure LerRegistro(var Nome, Valor: String);
    procedure CarregaDadosRegistro;
    procedure CriarRegistroInicial;
    procedure LimpaVariaveis;

    procedure ConfiguraDriver(Velocidade, Aceleracao : string);
    procedure ConfiguraPDI(Voltas, Ganho : string);
    procedure ExecutaPDI(Voltas: string);
    function StatusPDI(Registrador: Char):String;
    function ColetaDados(var Matriz: array of Double): Boolean;
    function ColetaPDI : Boolean;
    procedure Seleciona_Offset(Ganho : integer);
    procedure CalculaMediaDesvio(Ganho : integer; Voltas: string; Offset : boolean);
    procedure CalculaMag(Voltas: string);
    procedure CalculaResultados(var Dados: array of Double);
    procedure CalculaMomentos;
    procedure TF1(var Dados: array of Double; n, iSign: Integer);
    procedure TF2(var Dados: array of Double; nn1, iSign1 : Integer );
    procedure TimerEncTimer(Sender: TObject);
    function TestaLimite(Valor:string ; Min, Max : double; digits: integer) : string;
    function VerificaSaturacao : boolean;
    procedure Ler_Medidor_Pneumatico;
    procedure Ler_Display;

  private
    { Private declarations }
  public
    { Public declarations }
  end;


var
  FBiblioteca: TFBiblioteca;

   Limite    : boolean;
   Arq       : TextFile;
   NomeArq   : String;

   {Dados Registro}
   PortaDriver,
   BaudrateDriver,
   DataBitsDriver,
   StopBitsDriver,
   ParidadeDriver,

   PortaDisplay,
   BaudrateDisplay,
   DataBitsDisplay,
   StopBitsDisplay,
   ParidadeDisplay,

   EndGPIBInt,

   EndDriver,
   VelMotorMed,
   AceMotorMed,
   NVoltasMed,
   PassoExtra,
   PulsosEncoder,
   PassosMotor,

   Npontos,
   Trigger           : string;

   Bobina_em_uso     : string;

   Bobina_Espiras,
   Bobina_Raio1,
   Bobina_Raio2,
   Bobina_DistCentro : array[0..4] of string;

   VoltasOffset,
   Offset_G1,
   Offset_G2,
   Offset_G5,
   Offset_G10,
   Offset_G20,
   Offset_G50,
   Offset_G100,
   Offset_G200,
   Offset_G500,
   Offset_G1000      : string;

   Dimensoes_Blocos : array[0..4] of string;

   Aciona_MZ,
   Aciona_MX,
   Aciona_MY,

   Ganho_MZ,
   Ganho_MX,
   Ganho_MY,

   Vel_Motor_Manual,
   Ace_Motor_Manual,
   NVoltas_Manual     : string;
 {*******************}

   FalhaRegistro      : Boolean;

   tmpGPIB            : string;

   {Limites Registro}
   Limite_GPIB_Min,
   Limite_GPIB_Max,
   Limite_VelMin,
   Limite_VelMax,
   Limite_AceMin,
   Limite_AceMax,
   Limite_VoltasMin,
   Limite_VoltasMax,
   Limite_VoltasManualMin,
   Limite_VoltasManualMax,
   Limite_PulsosEncoderMin,
   Limite_PulsosEncoderMax,
   Limite_PassosMotorMin,
   Limite_PassosMotorMax,
   Limite_EndDriverMin,
   Limite_EndDriverMax,
   Limite_NEspirasMax,
   Limite_Raio1Min,
   Limite_Raio1Max,
   Limite_Raio2Min,
   Limite_Raio2Max,
   Limite_DistCentroMin,
   Limite_DistCentroMax    : double;

   Arquivo_Resumo          : String;   

   {Vetores de Cálculo}
   VetorColetas: Array[0..6000] of Double;
   VetorGrafico: Array[0..6000] of Double;
   VetorMedia  : Array[0..511] of extended;
   VetorDesvio : Array[0..511] of extended;
   VetorCalculo: Array[0..511] of Double;
   StringDados : Array[0..1000] of string;
   {**********}

  {Variáveis Transformada de Fourie}
   CoefDipoloA        : Double;
   CoefDipoloB        : Double;
   SAN, SBN, SSAN2, SSBN2, SDBDXN, SDBDXN2,Smodulo : Array [0..20] Of Double;

   Am : array[0..3] of Extended;
   Bm : array[0..3] of Extended;
  {*******}

  {Variáveis para Cálculo dos momentos magnéticos}
  Mi0                   : double;
  Mx                    : double;
  My                    : double;
  Mz                    : double;
  Mx2                   : double;
  My2                   : double;
  Mz2                   : double;
  Alfa                  : double;
  Beta                  : double;
  VolumeBloco           : double;
  Modulo                : double;
  MagNormal             : double;
  Mag2Normal            : double;
  MagSkew               : double;
  Mag2Skew              : double;
  {****************}

  NPontosPDI            : integer;
  IntervaloPDI          : double;
  Distancia             : integer;
  ValorOffset           : double;

  PararTudo             : boolean;

  ArqBruto              : TextFile;

  Coefs                 : Boolean;

  DispA,
  DispB,
  DispC                 : String;

  TemperaturaBloco,
  NumeroBloco           : String;
  ComprimentoBloco      : double;
  LarguraBloco          : double;
  EspessuraBloco        : double;

  SubtraiVol            : double;

const

  Dir = 'C:\Arq\Work_at_LNLS\IMA\Bobina de Helmholtz v4\Resultados\';
  CR = #13;
  CRLF = #13#10;

 {Biblioteca Integrador}
  PDIProcuraIndice    = 'IND,+'+CR;  {Habilita a procura de indice do integrador}
  PDIIniciaColeta     = 'RUN'+CR;    {Inicia coleta com o integrador}
  PDIParaColeta       = 'BRK'+CR;    {Inicia coleta com o integrador}
  PDILerStatus        = 'STB,';      {Le status do integrador}
  PDIBuscaResultados  = 'ENQ'+CR;    {Busca Resultados do integrador}
  PDIEscolheCanal     = 'CHA,A'+CR;  {Escolha de Canal}
  PDIConfiguraGanho   = 'SGA,A,';    {Configura ganho integrador}
  PDIClearStatus      = 'CRV,A'+CR;    {Limpa Saturacao}
  PDITipodeTrigger    = 'TRS,E,';    {Tipo de Trigger}
  PDISequenciaTrigger = 'TRI,-,';{Sequencia Trigger}
  PDIMotorAutomatico  = 'MOT,S'+CR;  {Configura Motor em automático}
  PDIArmazenaBloco    = 'IMD,0'+CR;  {Configura Dados para serem armazenados em blocos}
  PDIArmazena         = 'CUM,0'+CR;  {Configura Dados para serem armazenados}
  PDIZerarContador    = 'ZCT'+CR;    {Zerar contador de pulsos}
  PDIEndofData        = 'EOD'+CR;    {End of Data}
  PDISincroniza       = 'SYN,1'+CR;  {Sincroniza}
  PDICurtoCircuito    = 'ADJ,A,';     {Curto Integrador}
 {*********************}

 EsperaDriver         = 20; {ms}
 EsperaIntegrador     = 20; {ms}

 ResolucaoMotor    = 'MR';

 ConversaoPDI = 1E-8;

 TetaR  = 0;

 implementation

uses Helmholtz_v4, Conexoes, ConfGeral, ConfBob, Offset, Medicao, Motores;

{$R *.DFM}

procedure TFBiblioteca.GravarRegistro(Nome,Valor: String);
var ArqReg: TRegIniFile;
begin
     ArqReg := TRegIniFile.Create('Software\Helmholtz_v4');
     Try
        ArqReg.WriteString('Dados', Nome, Valor);
     Finally
        ArqReg.Free;
     end;
end;

procedure TFBiblioteca.LerRegistro(var Nome, Valor: String);
var ArqReg: TRegIniFile;
begin
     ArqReg := TRegIniFile.Create('Software\Helmholtz_v4');
     Try
        Valor := ArqReg.ReadString('Dados', Nome, Valor);
     Finally
        ArqReg.Free;
     end;

     if Valor = '' then
     begin
        FalhaRegistro := True;
        CriarRegistroInicial;
        LerRegistro(Nome, Valor);
     end;
end;

procedure TFBiblioteca.CarregaDadosRegistro;
var
Nome : String;
Valor : String;
i : integer;
begin
     FalhaRegistro := False;

    {Conexões - Driver}
     Nome := 'PortaDriver';
     LerRegistro(Nome,Valor);
     PortaDriver := Valor;

     Nome := 'BaudrateDriver';
     LerRegistro(Nome,Valor);
     BaudrateDriver := Valor;

     Nome := 'DatabitsDriver';
     LerRegistro(Nome,Valor);
     DatabitsDriver := Valor;

     Nome := 'StopbitsDriver';
     LerRegistro(Nome,Valor);
     StopbitsDriver := Valor;

     Nome := 'ParidadeDriver';
     LerRegistro(Nome,Valor);
     ParidadeDriver := Valor;

    {Conexões - Display}
     Nome := 'PortaDisplay';
     LerRegistro(Nome,Valor);
     PortaDisplay := Valor;

     Nome := 'BaudrateDisplay';
     LerRegistro(Nome,Valor);
     BaudrateDisplay := Valor;

     Nome := 'DatabitsDisplay';
     LerRegistro(Nome,Valor);
     DatabitsDisplay := Valor;

     Nome := 'StopbitsDisplay';
     LerRegistro(Nome,Valor);
     StopbitsDisplay := Valor;

     Nome := 'ParidadeDisplay';
     LerRegistro(Nome,Valor);
     ParidadeDisplay := Valor;

    {Conexões - Integrador}
     Nome := 'EndGPIBInt';
     LerRegistro(Nome,Valor);
     EndGPIBInt := Valor;

    {Configurações Gerais - Driver e Motor}
     Nome := 'EndDriver';
     LerRegistro(Nome,Valor);
     EndDriver := Valor;

     Nome := 'VelMotorMed';
     LerRegistro(Nome,Valor);
     VelMotorMed := Valor;

     Nome := 'AceMotorMed';
     LerRegistro(Nome,Valor);
     AceMotorMed := Valor;

     Nome := 'NVoltasMed';
     LerRegistro(Nome,Valor);
     NVoltasMed := Valor;

     Nome := 'PassoExtra';
     LerRegistro(Nome,Valor);
     PassoExtra := Valor;

     Nome := 'PulsosEncoder';
     LerRegistro(Nome,Valor);
     PulsosEncoder := Valor;

     Nome := 'PassosMotor';
     LerRegistro(Nome,Valor);
     PassosMotor := Valor;

     {Configurações Gerais - Integrador}
     Nome := 'Npontos';
     LerRegistro(Nome,Valor);
     Npontos := Valor;

     Nome := 'Trigger';
     LerRegistro(Nome,Valor);
     Trigger := Valor;

     {Configurações Bobinas}
     Nome := 'Bobina_em_uso';
     LerRegistro(Nome,Valor);
     Bobina_em_uso := Valor;

     for i:=0 to 4 do
     begin
        Nome := 'Bobina'+IntToStr(i+1)+'_Espiras';
        LerRegistro(Nome,Valor);
        Bobina_Espiras[i] := Valor;

        Nome := 'Bobina'+IntToStr(i+1)+'_Raio1';
        LerRegistro(Nome,Valor);
        Bobina_Raio1[i] := Valor;

        Nome := 'Bobina'+IntToStr(i+1)+'_Raio2';
        LerRegistro(Nome,Valor);
        Bobina_Raio2[i] := Valor;

        Nome := 'Bobina'+IntToStr(i+1)+'_DistCentro';
        LerRegistro(Nome,Valor);
        Bobina_DistCentro[i] := Valor;
     end;

     {Offset}
     Nome := 'VoltasOffset';
     LerRegistro(Nome,Valor);
     VoltasOffset := Valor;

     Nome := 'Offset_G1';
     LerRegistro(Nome,Valor);
     Offset_G1 := Valor;

     Nome := 'Offset_G2';
     LerRegistro(Nome,Valor);
     Offset_G2 := Valor;

     Nome := 'Offset_G5';
     LerRegistro(Nome,Valor);
     Offset_G5 := Valor;

     Nome := 'Offset_G10';
     LerRegistro(Nome,Valor);
     Offset_G10 := Valor;

     Nome := 'Offset_G20';
     LerRegistro(Nome,Valor);
     Offset_G20 := Valor;

     Nome := 'Offset_G50';
     LerRegistro(Nome,Valor);
     Offset_G50 := Valor;

     Nome := 'Offset_G100';
     LerRegistro(Nome,Valor);
     Offset_G100 := Valor;

     Nome := 'Offset_G200';
     LerRegistro(Nome,Valor);
     Offset_G200 := Valor;

     Nome := 'Offset_G500';
     LerRegistro(Nome,Valor);
     Offset_G500 := Valor;

     Nome := 'Offset_G1000';
     LerRegistro(Nome,Valor);
     Offset_G1000 := Valor;

     {Medição - Ganho}
     for i:=0 to 4 do
     begin
        Nome := 'Dim'+IntToStr(i+1);
        LerRegistro(Nome,Valor);
        Dimensoes_Blocos[i] := Valor;
     end;

     Nome := 'Aciona_MZ';
     LerRegistro(Nome,Valor);
     Aciona_MZ := Valor;

     Nome := 'Aciona_MX';
     LerRegistro(Nome,Valor);
     Aciona_MX := Valor;

     Nome := 'Aciona_MY';
     LerRegistro(Nome,Valor);
     Aciona_MY := Valor;

     Nome := 'Ganho_MZ';
     LerRegistro(Nome,Valor);
     Ganho_MZ := Valor;

     Nome := 'Ganho_MX';
     LerRegistro(Nome,Valor);
     Ganho_MX := Valor;

     Nome := 'Ganho_MY';
     LerRegistro(Nome,Valor);
     Ganho_MY := Valor;

     {Motores}
     Nome := 'Vel_Motor_Manual';
     LerRegistro(Nome,Valor);
     Vel_Motor_Manual := Valor;

     Nome := 'Ace_Motor_Manual';
     LerRegistro(Nome,Valor);
     Ace_Motor_Manual := Valor;

     Nome := 'NVoltas_Manual';
     LerRegistro(Nome,Valor);
     NVoltas_Manual := Valor;

     {Limites}
     Nome := 'Limite_GPIB_Min';
     LerRegistro(Nome,Valor);
     Limite_GPIB_Min := StrToFloat(Valor);

     Nome := 'Limite_GPIB_Max';
     LerRegistro(Nome,Valor);
     Limite_GPIB_Max := StrToFloat(Valor);

     Nome := 'Limite_VelMin';
     LerRegistro(Nome,Valor);
     Limite_VelMin := StrToFloat(Valor);

     Nome := 'Limite_VelMax';
     LerRegistro(Nome,Valor);
     Limite_VelMax := StrToFloat(Valor);

     Nome := 'Limite_AceMin';
     LerRegistro(Nome,Valor);
     Limite_AceMin := StrToFloat(Valor);

     Nome := 'Limite_AceMax';
     LerRegistro(Nome,Valor);
     Limite_AceMax := StrToFloat(Valor);

     Nome := 'Limite_VoltasMin';
     LerRegistro(Nome,Valor);
     Limite_VoltasMin := StrToFloat(Valor);

     Nome := 'Limite_VoltasMax';
     LerRegistro(Nome,Valor);
     Limite_VoltasMax := StrToFloat(Valor);

     Nome := 'Limite_VoltasManualMin';
     LerRegistro(Nome,Valor);
     Limite_VoltasManualMin := StrToFloat(Valor);

     Nome := 'Limite_VoltasManualMax';
     LerRegistro(Nome,Valor);
     Limite_VoltasManualMax := StrToFloat(Valor);

     Nome := 'Limite_PulsosEncoderMin';
     LerRegistro(Nome,Valor);
     Limite_PulsosEncoderMin := StrToFloat(Valor);

     Nome := 'Limite_PulsosEncoderMax';
     LerRegistro(Nome,Valor);
     Limite_PulsosEncoderMax := StrToFloat(Valor);

     Nome := 'Limite_PassosMotorMin';
     LerRegistro(Nome,Valor);
     Limite_PassosMotorMin := StrToFloat(Valor);

     Nome := 'Limite_PassosMotorMax';
     LerRegistro(Nome,Valor);
     Limite_PassosMotorMax := StrToFloat(Valor);

     Nome := 'Limite_EndDriverMin';
     LerRegistro(Nome,Valor);
     Limite_EndDriverMin := StrToFloat(Valor);

     Nome := 'Limite_EndDriverMax';
     LerRegistro(Nome,Valor);
     Limite_EndDriverMax := StrToFloat(Valor);

     Nome := 'Limite_NEspirasMax';
     LerRegistro(Nome,Valor);
     Limite_NEspirasMax := StrToFloat(Valor);

     Nome := 'Limite_Raio1Min';
     LerRegistro(Nome,Valor);
     Limite_Raio1Min := StrToFloat(Valor);

     Nome := 'Limite_Raio1Max';
     LerRegistro(Nome,Valor);
     Limite_Raio1Max := StrToFloat(Valor);

     Nome := 'Limite_Raio2Min';
     LerRegistro(Nome,Valor);
     Limite_Raio2Min := StrToFloat(Valor);

     Nome := 'Limite_Raio2Max';
     LerRegistro(Nome,Valor);
     Limite_Raio2Max := StrToFloat(Valor);

     Nome := 'Limite_DistCentroMin';
     LerRegistro(Nome,Valor);
     Limite_DistCentroMin := StrToFloat(Valor);

     Nome := 'Limite_DistCentroMax';
     LerRegistro(Nome,Valor);
     Limite_DistCentroMax := StrToFloat(Valor);

     Nome := 'Arquivo_Resumo';
     LerRegistro(Nome,Valor);
     Arquivo_Resumo := Valor;

     Nome := 'Subtrai_Volume';
     LerRegistro(Nome,Valor);
     SubtraiVol := StrToFloat(Valor);

     if FalhaRegistro = True then
     begin
        FalhaRegistro := False;
        MessageDlg('Registro de dados inexistente ou desatualizado, favor configurar todos os parâmetros. Os valores padrões foram configurados!',mtError, [mbok], 0);
     end;
end;

procedure TFBiblioteca.CriarRegistroInicial;
begin
   {Conexões - Driver}
   GravarRegistro('PortaDriver','0');
   GravarRegistro('BaudrateDriver','2');
   GravarRegistro('DatabitsDriver','4');
   GravarRegistro('StopbitsDriver','0');
   GravarRegistro('ParidadeDriver','0');

   {Conexões - Display}
   GravarRegistro('PortaDisplay','1');
   GravarRegistro('BaudrateDisplay','2');
   GravarRegistro('DatabitsDisplay','3');
   GravarRegistro('StopbitsDisplay','2');
   GravarRegistro('ParidadeDisplay','2');

   {Conexões - Integrador}
   GravarRegistro('EndGPIBInt','28');

   {Configurações Gerais - Driver e Motor}
   GravarRegistro('EndDriver','0');
   GravarRegistro('VelMotorMed','2');
   GravarRegistro('AceMotorMed','5');
   GravarRegistro('NVoltasMed','10');
   GravarRegistro('PassoExtra','-3125');
   GravarRegistro('PulsosEncoder','2048');
   GravarRegistro('PassosMotor','-50000');

   {Configurações Gerais - Integrador}
   GravarRegistro('Npontos','5');
   GravarRegistro('Trigger','738');

   {Configurações Bobinas}
   GravarRegistro('Bobina_em_uso','0');

   {Configurações Bobina 1}
   GravarRegistro('Bobina1_Espiras','2282');
   GravarRegistro('Bobina1_Raio1','0.347423');
   GravarRegistro('Bobina1_Raio2','0');
   GravarRegistro('Bobina1_DistCentro','0.165315');

   {Configurações Bobina 2}
   GravarRegistro('Bobina2_Espiras','0');
   GravarRegistro('Bobina2_Raio1','0');
   GravarRegistro('Bobina2_Raio2','0');
   GravarRegistro('Bobina2_DistCentro','0');

   {Configurações Bobina 3}
   GravarRegistro('Bobina3_Espiras','0');
   GravarRegistro('Bobina3_Raio1','0');
   GravarRegistro('Bobina3_Raio2','0');
   GravarRegistro('Bobina3_DistCentro','0');

   {Configurações Bobina 4}
   GravarRegistro('Bobina4_Espiras','0');
   GravarRegistro('Bobina4_Raio1','0');
   GravarRegistro('Bobina4_Raio2','0');
   GravarRegistro('Bobina4_DistCentro','0');

   {Configurações Bobina 5}
   GravarRegistro('Bobina5_Espiras','0');
   GravarRegistro('Bobina5_Raio1','0');
   GravarRegistro('Bobina5_Raio2','0');
   GravarRegistro('Bobina5_DistCentro','0');

   {Offset}
   GravarRegistro('VoltasOffset','5');
   GravarRegistro('Offset_G1','0');
   GravarRegistro('Offset_G2','0');
   GravarRegistro('Offset_G5','0');
   GravarRegistro('Offset_G10','0');
   GravarRegistro('Offset_G20','0');
   GravarRegistro('Offset_G50','0');
   GravarRegistro('Offset_G100','0');
   GravarRegistro('Offset_G200','0');
   GravarRegistro('Offset_G500','0');
   GravarRegistro('Offset_G1000','0');

   {Medição - Ganho}
   GravarRegistro('Dim1','1 mm x 1 mm x 1 mm');
   GravarRegistro('Dim2','1 mm x 1 mm x 1 mm');
   GravarRegistro('Dim3','1 mm x 1 mm x 1 mm');
   GravarRegistro('Dim4','1 mm x 1 mm x 1 mm');
   GravarRegistro('Dim5','1 mm x 1 mm x 1 mm');

   GravarRegistro('Aciona_MZ','0');
   GravarRegistro('Aciona_MX','0');
   GravarRegistro('Aciona_MY','0');

   GravarRegistro('Ganho_MZ','0');
   GravarRegistro('Ganho_MX','0');
   GravarRegistro('Ganho_MY','0');

   {Motores}
   GravarRegistro('Vel_Motor_Manual','2');
   GravarRegistro('Ace_Motor_Manual','5');
   GravarRegistro('NVoltas_Manual','1');

   {Limites campos}
   GravarRegistro('Limite_GPIB_Min','22');
   GravarRegistro('Limite_GPIB_Max','30');
   GravarRegistro('Limite_VelMin','1');
   GravarRegistro('Limite_VelMax','5');
   GravarRegistro('Limite_AceMin','1');
   GravarRegistro('Limite_AceMax','5');
   GravarRegistro('Limite_VoltasMin','1');
   GravarRegistro('Limite_VoltasMax','100');
   GravarRegistro('Limite_VoltasManualMin','-100');
   GravarRegistro('Limite_VoltasManualMax','100');
   GravarRegistro('Limite_PulsosEncoderMin','2048');
   GravarRegistro('Limite_PulsosEncoderMax','2048');
   GravarRegistro('Limite_PassosMotorMin','50000');
   GravarRegistro('Limite_PassosMotorMax','50000');
   GravarRegistro('Limite_EndDriverMin','1');
   GravarRegistro('Limite_EndDriverMax','8');
   GravarRegistro('Limite_NEspirasMax','10000');
   GravarRegistro('Limite_Raio1Min','0.001');
   GravarRegistro('Limite_Raio1Max','1000');
   GravarRegistro('Limite_Raio2Min','0');
   GravarRegistro('Limite_Raio2Max','0');
   GravarRegistro('Limite_DistCentroMin','0.001');
   GravarRegistro('Limite_DistCentroMax','1000');
   GravarRegistro('Subtrai_Volume','0.00000123857');

   GravarRegistro('Arquivo_Resumo','C:\Arq\Work_at_LNLS\IMA\Bobina de Helmholtz v4\Resultados\Resumo_Helmholtz.dat');
end;

procedure TFBiblioteca.LimpaVariaveis;
var
i : integer;
begin
   for i:=0 to 1000 do
      StringDados[i] := '';

   for i:=0 to 511 do
   begin
      VetorCalculo[i] := 0;
      VetorMedia[i]  := 0;
      VetorDesvio[i] := 0;
   end;

   for i:=0 to 6000 do
      VetorColetas[i]:= 0;

   Mi0         :=0;
   Alfa        :=0;
   Beta        :=0;
   Modulo      :=0;
   MagNormal   :=0;
   Mag2Normal  :=0;
   MagSkew     :=0;
   Mag2Skew    :=0;

   for i:=0 to 20 do
   begin
      SAN[i]     := 0;
      SBN[i]     := 0;
      SSAN2[i]   := 0;
      SSBN2[i]   := 0;
      SDBDXN[i]  := 0;
      SDBDXN2[i] := 0;
      Smodulo[i] := 0;
   end;
end;

procedure TFBiblioteca.ConfiguraDriver(Velocidade, Aceleracao : string);
begin
    Parker.LimpaRX;
    Parker.LimpaTX;
    delay(EsperaDriver);

    Parker.Zera(Smot(StrToInt(EndDriver)));
    Parker.setModo(Smot(StrToInt(EndDriver)),Normal);
    Parker.Escrita(ResolucaoMotor+PassosMotor+CR);
    Parker.SetVelocidade(Smot(StrToInt(EndDriver)),StrToFloat(Velocidade));
    Parker.SetAceleracao(Smot(StrToInt(EndDriver)),StrToFloat(Aceleracao));
end;

procedure TFBiblioteca.ConfiguraPDI(Voltas, Ganho : string);
begin
   Case StrToInt(Npontos) of
      0: NPontosPDI := 4;
      1: NPontosPDI := 8;
      2: NPontosPDI := 16;
      3: NPontosPDI := 32;
      4: NPontosPDI := 64;
      5: NPontosPDI := 128;
      6: NPontosPDI := 256;
      7: NPontosPDI := 512;
   End;
   IntervaloPDI := StrToInt(PulsosEncoder)/NPontosPDI;
   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIParaColeta);                                 {Parar Coletas}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIEscolheCanal);                               {Escolhe o Canal}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDITipodeTrigger+IntToStr(Round(StrToInt(PulsosEncoder)/4))+CR);{CONFIGURANDO O TRIGGER SEQUENCE MODE}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDISequenciaTrigger+Trigger+'/'+FloatToStr(NPontosPDI*StrToInt(Voltas))+','+FloatToStr(IntervaloPDI)+CR); {CONFIGURANDO O TRIGGER SEQUENCE}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIMotorAutomatico);                            {CONFIGURA O MOTOR A PARA AUTOMÁTICO}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIArmazenaBloco);                              {CONFIGURA OS DADOS PARA ARMAZENAGEM EM BLOCO}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIArmazena);                                   {CONFIGURA OS DADOS PARA ARMAZENAGEM}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIEndofData);                                  {EndOfData}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDISincroniza);                                 {sincroniza}
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIConfiguraGanho + Ganho + CR);         {Configura Ganho}
   delay(EsperaIntegrador);
end;

procedure TFBiblioteca.ExecutaPDI(Voltas: string);
var
aux: double;
tmp: integer;
indice : boolean;
begin
   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIProcuraIndice); { ACHA O INDÍCE DO INTEGRADOR }
   DispGPIB.Leitura(tmpGPIB,10);
   indice := True;
   tmp :=0;

   while ((tmp <> 1)  and (PararTudo = False)) do
   begin
      Application.ProcessMessages;
      tmp := StrToInt(Copy(StatusPDI('1'),8,1));
      if indice = true then
      begin
         Parker.LimpaRX;
         Parker.LimpaTX;
         Distancia := (StrToInt(PassosMotor) + StrToInt(PassoExtra));

         Parker.setDistancia(Smot(StrToInt(EndDriver)),Distancia);
         Parker.move(Smot(StrToInt(EndDriver)));
         repeat
           Application.ProcessMessages;
         until not Parker.Movendo(Smot(StrToInt(EndDriver)));

         indice := false;
      end;
   end;

   if VerificaSaturacao then
      PararTudo := True;

   if PararTudo = True then
      exit;

   Parker.LimpaTx;
   Parker.LimpaRx;

   Distancia := (((StrToInt(Voltas)+2)*StrToInt(PassosMotor)) - StrToInt(PassoExtra));

   Parker.setDistancia(Smot(StrToInt(EndDriver)),Distancia);

   DispGPIB.Leitura(tmpGPIB,10);
   DispGPIB.Escrita(PDIIniciaColeta);                            {Inicia a Coleta}
   DispGPIB.Leitura(tmpGPIB,10);

   Parker.move(Smot(StrToInt(EndDriver)));
   repeat
      Application.ProcessMessages;
   until not Parker.Movendo(Smot(StrToInt(EndDriver)));

   if VerificaSaturacao then
      PararTudo := True;

   aux:=0;
   while ((aux <> 1) and (PararTudo = False)) do
   begin
      Application.ProcessMessages;
      aux:=StrToFloat(Copy(StatusPDI('1'),6,1));
   end;
end;

function TFBiblioteca.StatusPDI(Registrador: Char):String;
var
aux : string;
begin
   DispGPIB.Escrita(PDILerStatus+Registrador+CR);
   delay(EsperaIntegrador);
   DispGPIB.Leitura(aux,10);
   Result := aux;
end;

function TFBiblioteca.ColetaDados(var Matriz: array of Double): Boolean;
var
i      : Integer;
j      : Integer;
dados  : string;
valor  : string;
pontos : integer;
TmpNPontos : integer;
//aux : string;
begin
  {Gerar Arquivo Bruto e a média}

  ColetaPDI;

  TmpNPontos := nPontosPDI;
  dados := '';
  i := 0;
  pontos := 0;
  AssignFile(Arq,'out.dat');
  Rewrite(Arq);

//  AssignFile(Arq,'C:\Arq\Work_at_LNLS\IMA\Bobina de Helmholtz v4\outIN.dat');
//  Reset(Arq);

  repeat
     Application.ProcessMessages;
     dados := dados + StringDados[i];
     repeat
        Application.ProcessMessages;
        j := Pos('A',dados);
        if j <> 0 then
        begin
           valor := Trim(Copy(dados,1,j-1));
           dados := Copy(dados,j+3,(length(dados)));
           if (valor <> #$1A) or (PararTudo = false) then
           begin
              Matriz[pontos]:=(StrToFloat(valor)*ConversaoPDI)/(StrToFloat(Bobina_Espiras[StrToInt(Bobina_em_uso)])/2);

              //Readln(Arq,aux);
              //Matriz[pontos]:=(StrToFloat(aux)*ConversaoPDI)/(StrToFloat(Bobina_Espiras[StrToInt(Bobina_em_uso)])/2);

              Writeln(Arq,valor);

              pontos := pontos + 1;

              if pontos = TmpNPontos then
              begin
                 TmpNPontos := TmpNPontos + NPontosPDI;
              end;
           end
           else
           begin
              break;
           end;
        end
     until (j = 0) or (PararTudo = True);
     i := i + 1;
  until (dados = #$1A) or (PararTudo = True);

  Closefile(Arq);


  if PararTudo = True then
  begin
     Result:=False;
     exit;
  end;

  Result:=True;
end;

function TFBiblioteca.ColetaPDI: Boolean;
var
i : integer;
begin
  delay(500);
  i :=0;

  try
     DispGPIB.Leitura(StringDados[i],255);
     i := i+1;
     repeat
       Application.ProcessMessages;
       DispGPIB.Leitura(StringDados[i],255);
       i := i+1;
     until ((StringDados[i-1]='') or (PararTudo = True));
     Result:=True;
  except
     PararTudo := True;
     Result := False;
  end;
end;

procedure TFBiblioteca.Seleciona_Offset(Ganho : integer);
begin
   Case Ganho of
      0: ValorOffset := StrToFloat(OffSet_G1);
      1: ValorOffset := StrToFloat(OffSet_G2);
      2: ValorOffset := StrToFloat(OffSet_G5);
      3: ValorOffset := StrToFloat(OffSet_G10);
      4: ValorOffset := StrToFloat(OffSet_G20);
      5: ValorOffset := StrToFloat(OffSet_G50);
      6: ValorOffset := StrToFloat(OffSet_G100);
      7: ValorOffset := StrToFloat(OffSet_G200);
      8: ValorOffset := StrToFloat(OffSet_G500);
      9: ValorOffset := StrToFloat(OffSet_G1000);
   End;
end;

procedure TFBiblioteca.CalculaMediaDesvio(Ganho : integer; Voltas: string; Offset : boolean);
var
i : integer;
j : integer;
Soma     : extended;
Somaquad : extended;
mediaoffset : double;
begin
   for i:=0 to (nPontosPDI-1) do
   begin
      Soma := 0;
      Somaquad := 0;
      for j:=0 to (StrToInt(Voltas)-1) do
      begin
         Soma := Soma + VetorColetas[i+(j*NpontosPDI)];
         SomaQuad := SomaQuad + power(VetorColetas[i+(j*NpontosPDI)],2);
      end;
      if StrToInt(Voltas) = 1 then
         VetorDesvio[i] := 0
      else
         VetorDesvio[i] := sqrt((StrToInt(Voltas)*SomaQuad - power(Soma,2))/(StrToInt(Voltas)*(StrToInt(Voltas)-1)));

      VetorMedia[i] := Soma / StrToInt(Voltas);
   end;

   if Offset = True then
   begin
      mediaoffset := 0;

      for i:=0 to (nPontosPDI-1) do
      begin
         mediaoffset := mediaoffset + VetorMedia[i];
      end;
      mediaoffset := mediaoffset / nPontosPDI;

      Case Ganho of
         0: OffSet_G1    := FloatToStr(mediaoffset);
         1: OffSet_G2    := FloatToStr(mediaoffset);
         2: OffSet_G5    := FloatToStr(mediaoffset);
         3: OffSet_G10   := FloatToStr(mediaoffset);
         4: OffSet_G20   := FloatToStr(mediaoffset);
         5: OffSet_G50   := FloatToStr(mediaoffset);
         6: OffSet_G100  := FloatToStr(mediaoffset);
         7: OffSet_G200  := FloatToStr(mediaoffset);
         8: OffSet_G500  := FloatToStr(mediaoffset);
         9: OffSet_G1000 := FloatToStr(mediaoffset);
      End;
   end
   else
   begin
      for i:=0 to (nPontosPDI-1) do
      begin
         VetorMedia[i] := VetorMedia[i] - ValorOffset;
      end;

      for i:=0 to ((StrToInt(Voltas)*nPontosPDI)-1) do
      begin
         VetorColetas[i] := VetorColetas[i] - ValorOffset;
      end;
   end;
end;

procedure TFBiblioteca.CalculaMag(Voltas: string);
var
j : integer;
k : integer;
begin
   {Ignorar a primeira e última curva de medida}
   for j:= 1 to (StrToInt(Voltas)-2) do
   begin
      Application.ProcessMessages;

      if PararTudo = True then
         break;

      {Inicia em 1 (VetorCalculo[k+1]) por causa da rotina da FFT}
      for k:=0 to (NPontosPDI-1) do
          VetorCalculo[k+1] := VetorColetas[k+(j*NPontosPDI)];

      Coefs := True;
      CalculaResultados(VetorCalculo);
      CalculaMomentos;
   end;

   if PararTudo = True then
      exit;

   if StrToInt(Voltas) = 1 then
      Mag2Normal := 0
   else
      Mag2Normal := sqrt(((StrToInt(Voltas)-2)*Mag2Normal-power(MagNormal,2))/((StrToInt(Voltas)-2)*((StrToInt(Voltas)-2)-1)))/VolumeBloco*Mi0;

   MagNormal  := ((MagNormal/(StrToInt(Voltas)-2))/VolumeBloco)*Mi0;

   if StrToInt(Voltas) = 1 then
      Mag2Skew := 0
   else
      Mag2Skew := sqrt(((StrToInt(Voltas)-2)*Mag2Skew-power(MagSkew,2))/((StrToInt(Voltas)-2)*((StrToInt(Voltas)-2)-1)))/VolumeBloco*Mi0;

   MagSkew  := ((MagSkew/(StrToInt(Voltas)-2))/VolumeBloco)*Mi0;
end;

procedure TFBiblioteca.CalculaResultados(var Dados: array of Double);
var
  x                : Integer;
  dAlfa, af, bf, n : Double;
  nPot             : Integer;
  an, bn, FatorR   : Double;
  dbdXN            : Extended;
  pot              : integer;
begin
  dAlfa     := (2 * PI) / NPontosPDI;
  n         := NPontosPDI / 2;

  { CÁLCULO DE FOURIER }

  TF1(Dados, Round(n), 1);
  Dados[1] := Dados[1] / NPontosPDI ;
  Dados[2] := Dados[2] / NPontosPDI ;

  for x := 3 to (NPontosPDI) do
     Dados[x] := Dados[x] / n ;

  nPot  := 1;

  pot := Round(n-1);
  if n > 10 then
     pot := 10;

  while nPot <= pot do
  begin
     FatorR := power(StrToFloat(Bobina_Raio1[StrToInt(Bobina_em_uso)]), Round(nPot))-(power(-1, nPot)*power(StrToFloat(Bobina_Raio2[StrToInt(Bobina_em_uso)]), Round(nPot)));

     {Coeficientes de Fourier}
     af:= Dados[2*nPot + 1];
     bf:= Dados[2*nPot + 2];

     if nPot < 5 then
     begin
        Am[nPot-1] := af*sqrt(NPontosPDI)/2;
        Bm[nPot-1] := bf*sqrt(NPontosPDI)/2;
     end;

     {Cálculo de Kn e Jn }
     an:=(af*SIN(nPot * dAlfa)+bf*(COS(nPot * dAlfa)-1))/(2*fatorR* (COS(nPot * dAlfa)-1));  {Equivale a Jn}
     bn:=(bf*SIN(nPot * dAlfa)-af*(COS(nPot * dAlfa)-1))/(2*fatorR* (COS(nPot * dAlfa)-1));  {Equivale a Kn}

     if Coefs = True then
     begin
        Coefs := False;
        CoefDipoloA := af;
        CoefDipoloB := bf;
     end;

     dbdXN         := nPot * Sqrt((bn * bn) + (an * an));
     SAN[nPot]     := SAN[nPot] + an ;
     SBN[nPot]     := SBN[nPot] + bn ;
     SSAN2[nPot]   := SSAN2[nPot] + power(an,2);
     SSBN2[nPot]   := SSBN2[nPot] + power(bn,2);
     SdbdXN[nPot]  := SdbdXN[nPot] + dbdXN ;
     SdbdXN2[nPot] := SdbdXN2[nPot] + (dbdXN * dbdXN);
     Smodulo[nPot] := Smodulo[nPot] + Sqrt((bn * bn) + (an * an));

     nPot  := nPot + 1;
  end;
end;

procedure TFBiblioteca.CalculaMomentos;
var
MomentoDipolar : double;
Ar1            : double;
Br1            : double;
dTeta          : double;
tmp            : double;
begin
  Mi0 := pi*4E-7;
  dTeta := 2*pi/nPontosPDI;

  MomentoDipolar := (power(StrToFloat(Bobina_Raio1[StrToInt(Bobina_em_uso)]),2))/power((power(StrToFloat(Bobina_Raio1[StrToInt(Bobina_em_uso)]),2)+power(StrToFloat(Bobina_DistCentro[StrToInt(Bobina_em_uso)]),2)),(3/2));

  Ar1 := CoefDipoloA*cos(TetaR) - CoefDipoloB*sin(TetaR);

  Br1 := CoefDipoloB*cos(TetaR) + CoefDipoloA*sin(TetaR);

  MagNormal  := MagNormal + (1/(Mi0*MomentoDipolar))*( (-Br1*sin(dTeta) + Ar1*(1-cos(dTeta))) / (2*(1-cos(dTeta))));
  tmp := (1/(Mi0*MomentoDipolar))*( (-Br1*sin(dTeta) + Ar1*(1-cos(dTeta))) / (2*(1-cos(dTeta))));
  Mag2Normal := Mag2Normal + ((power(tmp,2)));

  MagSkew :=  MagSkew + (1/(Mi0*MomentoDipolar))*( (Ar1*sin(dTeta) + Br1*(1-cos(dTeta))) / (2*(1-cos(dTeta))));
  tmp := (1/(Mi0*MomentoDipolar))*( (Ar1*sin(dTeta) + Br1*(1-cos(dTeta))) / (2*(1-cos(dTeta))));
  Mag2Skew := Mag2Skew + ((power(tmp,2)));
end;

procedure TFBiblioteca.TF1(var Dados: array of Double; n, iSign : Integer );
var
  C1, C2, WPR, WI, WPI, WR,
  WRS, WIS, H1R, H1I, H2R,
  H2I, WTemp, Theta        : Double ;
  N2P3, i, i1, i2, i3, i4  : Integer ;

begin
  Theta := 6.28318530717959 / 2 / n ;
  C1 := 0.5 ;
  if (iSign = 1) then
  begin
     C2 := - 0.5 ;
     TF2(Dados, n, 1);
  end
	else
  begin
     C2 := 0.5 ;
     Theta := -Theta ;
  end;
  WPR  := -2 *(SIN(0.5 * Theta) * SIN(0.5 * Theta));
  WPI  := SIN(Theta);
  WR   := 1 + WPR ;
  WI   := WPI ;
  N2P3 := (2 * n) + 3 ;
  for i := 2 to (Round(n / 2) + 1)  do
  begin
    i1 := (2 * i) - 1 ;
    i2 := i1 + 1 ;
    i3 := N2P3 - i2 ;
    i4 := i3 + 1 ;
    WRS := WR ;
    WIS := WI ;
    H1R := C1 * (Dados[I1] + Dados[I3]);
    H1I := C1 * (Dados[I2] - Dados[I4]);
    H2R := -C2 * (Dados[I2] + Dados[I4]);
    H2I := C2 * (Dados[I1] - Dados[I3]);
    Dados[i1] := H1R  + (WRS * H2R) - (WIS * H2I) ;
    Dados[i2] := H1I  + (WRS * H2I) + (WIS * H2R) ;
    Dados[i3] := H1R  - (WRS * H2R) + (WIS * H2I) ;
    Dados[i4] := -H1I + (WRS * H2I) + (WIS * H2R) ;
    WTemp := WR ;
    WR := (WR * WPR) - (WI * WPI) + WR;
    WI := (WI * WPR) + (WTemp * WPI) + WI;
  end;
  if (iSign = 1) then
  begin
    H1R := Dados[1];
    Dados[1] := H1R + Dados[2];
    Dados[2] := H1R - Dados[2];
  end
  else
  begin
    H1R := Dados[1] ;
    Dados[1] := C1 * (H1R + Dados[2]);
    Dados[2] := C1 * (H1R - Dados[2]);
    TF2(Dados, n, -1);
  end;
end;

{ FOURIER 2 ROTINA JÁ CONFERIDA - CERTA }
procedure TFBiblioteca.TF2(var Dados: array of Double; nn1, iSign1 : Integer );
var
  n1, ii, j1, h1, iStep1, MMax1 : Integer ;
  Tr1, Ti1, m, Wpr1, Wpi1 : Double ;
  Wr1, Wi1, WTp, Theta1   : Double ;

begin
  N1 := 2 * nn1 ;
  j1 := 1 ;

  ii:=1;
  while ii<=N1 do
  begin
    if (j1>ii) then
    begin
      Tr1 := Dados[j1] ;
      Ti1 := Dados[j1 + 1];
      Dados[j1] := Dados[ii] ;
      Dados[j1 + 1] := Dados[ii + 1];
      Dados[ii] := Tr1 ;
      Dados[ii + 1] := Ti1 ;
    end;
    m :=  N1 / 2;
    while ((m >= 2) and ( j1 > m )) do
    begin
    	j1 := Round(j1 - m) ;
        m := m / 2 ;
    end;
    j1 := Round(j1 + m); ;
    ii := ii + 2;
  end;

  MMax1 := 2 ;

  while (n1 > MMax1) do
  begin
    iStep1 := 2 * MMax1 ;
    Theta1 := 6.28318530717959 / (iSign1 * MMax1) ;
    Wpr1   := -2 * ( SIN(0.5 * Theta1) * SIN(0.5 * Theta1) ) ;
    Wpi1   := SIN(Theta1);
    Wr1    := 1 ;
    Wi1    := 0 ;

    h1:=1;

    while h1<=MMax1 do //     for h1 := 1 to MMax1 do
    begin
    	ii:=h1;
      while ii<=N1 do // for ii := h1 to N1 do
      begin
      	j1             := ii + MMax1 ;
        Tr1            := (Wr1 * Dados[j1])-(Wi1 * Dados[j1 + 1]) ;
        Ti1            := (Wr1 * Dados[j1 + 1])+(Wi1 * Dados[j1]);
        Dados[j1]      := Dados[ii] - Tr1 ;
        Dados[j1 + 1]  := Dados[ii + 1] - Ti1 ;
        Dados[ii]      := Dados[ii] + Tr1 ;
        Dados[ii + 1]  := Dados[ii + 1] + Ti1 ;
        ii             := ii + iStep1;
      end;

      WTP    := Wr1 ;
      Wr1    := (Wr1 * WPR1) - (Wi1 * WPI1) + Wr1 ;
      Wi1    := (Wi1 * WPR1) + (WTP * WPI1) + Wi1 ;
      h1     := h1 + 2;
    end;

    MMax1 := iStep1;
  end;
end;

procedure TFBiblioteca.TimerEncTimer(Sender: TObject);
var
tmp : string;
begin
   TimerEnc.Enabled := False;

   DispGPIB.Escrita('RCT'+CR);
   delay(EsperaIntegrador);

   DispGPIB.Leitura(tmp,50);
   FMotores.EEncoder.Text := tmp;

   TimerEnc.Enabled := True;
end;

function TFBiblioteca.TestaLimite(Valor:string ; Min, Max : double; digits: integer) : string;
var
value : double;
begin
  if digits = 0 then
  begin
     try
        value := StrToInt(Valor);
     except
        Result := FloatToStrF(Min,ffFixed,10,digits);
        MessageDlg('Valor de entrada inválido, valor mínimo ajustado!',mtWarning, [mbok], 0);
        Exit;
     end;
  end
  else
  begin
     try
        value := StrToFloat(Valor);
     except
        Result := FloatToStrF(Min,ffFixed,10,digits);
        MessageDlg('Valor de entrada inválido, valor mínimo ajustado!',mtWarning, [mbok], 0);
        Exit;
     end;
  end;

{Verifica Limites}
  if value > Max then
  begin
    Result := FloatToStrF(Max,ffFixed,10,digits);
    exit;
  end
  else if value < Min then
  begin
     Result := FloatToStrF(Min,ffFixed,10,digits);
     exit;
  end
  else
     Result := FloatToStrF(value,ffFixed,10,digits);
end;

function TFBiblioteca.VerificaSaturacao : boolean;
var
tmp : integer;
begin
   {Verifica saturação}
   tmp := StrToInt(Copy(StatusPDI('4'),8,2));
   if not (tmp = 0) then
   begin
      Result := True;
      PararTudo := True;
      MessageDlg('Verifique o ganho e a posição do bloco. Integrador saturado!!!',mtWarning, [mbok], 0);

      Distancia := StrToInt(PassoExtra)*-1;

      Parker.setDistancia(Smot(StrToInt(EndDriver)),Distancia);
      Parker.move(Smot(StrToInt(EndDriver)));
      repeat
        Application.ProcessMessages;
      until not Parker.Movendo(Smot(StrToInt(EndDriver)));

      Exit;
   end;
   Result := False;
end;

procedure TFBiblioteca.Ler_Medidor_Pneumatico;
const
    AcionaApalpador = '1O10'+CR;
    DesacionaApalpador = '1O00'+CR;
begin
    Parker.LimpaRX;
    Parker.LimpaTX;
    delay(EsperaDriver);
    Parker.Escrita(AcionaApalpador);

    delay(3000);
    Ler_Display;

    Parker.LimpaRX;
    Parker.LimpaTX;
    delay(EsperaDriver);
    Parker.Escrita(DesacionaApalpador);
end;

procedure TFBiblioteca.Ler_Display;
var
  saux,saux2,saux3,sig: string;
begin
  RsDisplay1.LimpaTX;
  RsDisplay1.LimpaRx;
  //RsDisplay1.Escrita(#27+'A0200'+#13);
  RsDisplay1.Escrita(#2);
  delay(50);

  saux       := RsDisplay1.Leitura(60);     {Eixo A}
  saux2      := saux;                       {Eixo B}
  saux3      := saux;{Eixo C}

  sig        := Copy(saux,3,1);
  saux       := Copy(saux,4,10);
  saux       := Trim(saux);
  if sig = '-' then
     saux := sig + saux;

  sig        := Copy(saux,19,1);
  saux2      := Copy(saux2,20,10);
  saux2       := Trim(saux2);
  if sig = '-' then
     saux2 := sig + saux2;

  sig        := Copy(saux,35,1);
  saux3      := Copy(saux3,36,10);
  saux3       := Trim(saux3);
  if sig = '-' then
     saux3 := sig + saux3;

  if saux = '' then
     saux := '0';
  if saux2 = '' then
     saux2 := '0';
  if saux3 = '' then
     saux3 := '0';

  DispA := FloatToStrF(abs(StrToFloat(saux)),ffFixed,10,3);
  DispB := FloatToStrF(abs(StrToFloat(saux2)),ffFixed,10,3);
  DispC := FloatToStrF(abs(StrToFloat(saux3)),ffFixed,10,3);
end;

end.
