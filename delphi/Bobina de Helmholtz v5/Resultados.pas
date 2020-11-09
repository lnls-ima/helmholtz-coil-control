unit Resultados;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  StdCtrls, ExtCtrls, TeeProcs, TeEngine, Chart, Biblioteca, Series,
  Buttons, ShellApi;

type
  TFResults = class(TForm)
    Chart1: TChart;
    Chart2: TChart;
    GBComponentes: TGroupBox;
    Label2: TLabel;
    EMedMz: TEdit;
    EDesvMz: TEdit;
    Label1: TLabel;
    Label3: TLabel;
    Label4: TLabel;
    EDesvMx: TEdit;
    EMedMx: TEdit;
    Label5: TLabel;
    Label6: TLabel;
    EDesvMy: TEdit;
    EMedMy: TEdit;
    Series1: TLineSeries;
    Series2: TLineSeries;
    Series3: TLineSeries;
    SBArqOut: TSpeedButton;
    SBFolder: TSpeedButton;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure AtualizaValores;
    procedure SBArqOutClick(Sender: TObject);
    procedure SBFolderClick(Sender: TObject);
    procedure FormShow(Sender: TObject);
  private
    { Private declarations }
  public
    { Public declarations }
    Pont_Jan: ^TFResults
  end;

var
  FResults: TFResults;

implementation

uses Medicao;

{$R *.DFM}

procedure TFResults.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Pont_Jan^:=nil;
  Release;
  FMedicao.Show;
end;

procedure TFResults.AtualizaValores;
var
i : integer;
begin
{Exibe Resultados}
   if ((mz = 0) and (mx = 0) and (my = 0)) then
   begin
      MessageDlg('Resultados inexistentes!!!',mtWarning, [mbOk],0);
      Pont_Jan^:=nil;
      Release;
      FMedicao.Show;
   end
   else
   begin
      EMedMz.Text := FloatToStr(Mz);
      EDesvMz.Text := FloatToStr(Mz2);

      EMedMx.Text := FloatToStr(Mx);
      EDesvMx.Text := FloatToStr(Mx2);

      EMedMy.Text := FloatToStr(My);
      EDesvMy.Text := FloatToStr(My2);

      Chart1.Series[0].Clear;
      Chart2.Series[0].Clear;
      Chart2.Series[1].Clear;
      for i:=0 to NPontosPDI-1 do
      begin
         Chart1.Series[0].AddXY(i*IntervaloPDI,Resultados1[0,i],'',clBlack);
         Chart2.Series[0].AddXY(i*IntervaloPDI,Resultados2[0,i],'',clRed);
         Chart2.Series[1].AddXY(i*IntervaloPDI,Resultados3[0,i],'',clBlue);
      end;
   end;
end;

procedure TFResults.SBArqOutClick(Sender: TObject);
begin
   ShellExecute(FResults.Handle, 'open', PChar(FBiblioteca.SDArq.Filename), nil, nil, SW_NORMAL);
end;

procedure TFResults.SBFolderClick(Sender: TObject);
begin
   ShellExecute(FResults.Handle, 'open', PChar(ExtractFilePath(FBiblioteca.SDArq.Filename)), nil, nil, SW_NORMAL);
end;

procedure TFResults.FormShow(Sender: TObject);
begin
   AtualizaValores;
end;

end.
