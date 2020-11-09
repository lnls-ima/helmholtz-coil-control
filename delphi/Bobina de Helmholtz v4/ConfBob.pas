unit ConfBob;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  Grids, StdCtrls, Buttons, Biblioteca, ExtCtrls;

type
  TFConfBob = class(TForm)
    SGBobinas: TStringGrid;
    Label10: TLabel;
    BBEditarTabBob: TBitBtn;
    RGBobAtiva: TRadioGroup;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormShow(Sender: TObject);
    procedure BBEditarTabBobClick(Sender: TObject);
    procedure AtualizaValores;
  private
    { Private declarations }
  public
    { Public declarations }
    Pont_Jan: ^TFConfBob
  end;

var
  FConfBob: TFConfBob;

implementation

uses Helmholtz_v4, Conexoes, ConfGeral, Offset, Medicao, Motores;

{$R *.DFM}

procedure TFConfBob.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Pont_Jan^:=nil;
  Release;
  FHelmholtz.Show;
end;

procedure TFConfBob.FormShow(Sender: TObject);
begin
   AtualizaValores;
end;

procedure TFConfBob.BBEditarTabBobClick(Sender: TObject);
var
i : integer;
Nome : string;
begin
   if BBEditarTabBob.Caption = 'Editar Tabela de Bobinas' then
   begin
      RGBobAtiva.Enabled := True;
      SGBobinas.Enabled := True;
      BBEditarTabBob.Caption := 'Finalizar edição da Tabela de Bobinas';
   end
   else
   begin
      RGBobAtiva.Enabled := False;
      SGBobinas.Enabled := False;

      Case MessageDlg('Deseja salvar as alterações no registro?',mtWarning,[mbYes, mbNo],0) of
         mrYes:
         begin
            Bobina_em_uso := IntToStr(RGBobAtiva.ItemIndex);
            FBiblioteca.GravarRegistro('Bobina_em_uso',Bobina_em_uso);
            for i:=0 to 4 do
            begin
               if (SGBobinas.Cells[1,i+1] <> '') and (SGBobinas.Cells[1,i+1] <> '0') then
               begin
                  SGBobinas.Cells[1,i+1] := FBiblioteca.TestaLimite(SGBobinas.Cells[1,i+1],1,Limite_NEspirasMax,0);
                  Bobina_Espiras[i] := SGBobinas.Cells[1,i+1];
                  Nome := 'Bobina'+IntToStr(i+1)+'_Espiras';
                  FBiblioteca.GravarRegistro(Nome,Bobina_Espiras[i]);

                  SGBobinas.Cells[2,i+1] := FBiblioteca.TestaLimite(SGBobinas.Cells[2,i+1],Limite_Raio1Min,Limite_Raio1Max,6);
                  Bobina_Raio1[i] := SGBobinas.Cells[2,i+1];
                  Nome := 'Bobina'+IntToStr(i+1)+'_Raio1';
                  FBiblioteca.GravarRegistro(Nome,Bobina_Raio1[i]);

                  SGBobinas.Cells[3,i+1] := FBiblioteca.TestaLimite(SGBobinas.Cells[3,i+1],Limite_Raio2Min,Limite_Raio2Max,6);
                  Bobina_Raio2[i] := SGBobinas.Cells[3,i+1];
                  Nome := 'Bobina'+IntToStr(i+1)+'_Raio2';
                  FBiblioteca.GravarRegistro(Nome,Bobina_Raio2[i]);

                  SGBobinas.Cells[4,i+1] := FBiblioteca.TestaLimite(SGBobinas.Cells[4,i+1],Limite_DistCentroMin,Limite_DistCentroMax,6);
                  Bobina_DistCentro[i] := SGBobinas.Cells[4,i+1];
                  Nome := 'Bobina'+IntToStr(i+1)+'_DistCentro';
                  FBiblioteca.GravarRegistro(Nome,Bobina_DistCentro[i]);
               end
               else
               begin
                  SGBobinas.Cells[1,i+1] := '0';
                  Bobina_Espiras[i] := SGBobinas.Cells[1,i+1];
                  Nome := 'Bobina'+IntToStr(i+1)+'_Espiras';
                  FBiblioteca.GravarRegistro(Nome,Bobina_Espiras[i]);

                  SGBobinas.Cells[2,i+1] := '0';
                  Bobina_Raio1[i] := SGBobinas.Cells[2,i+1];
                  Nome := 'Bobina'+IntToStr(i+1)+'_Raio1';
                  FBiblioteca.GravarRegistro(Nome,Bobina_Raio1[i]);

                  SGBobinas.Cells[3,i+1] := '0';
                  Bobina_Raio2[i] := SGBobinas.Cells[3,i+1];
                  Nome := 'Bobina'+IntToStr(i+1)+'_Raio2';
                  FBiblioteca.GravarRegistro(Nome,Bobina_Raio2[i]);

                  SGBobinas.Cells[4,i+1] := '0';
                  Bobina_DistCentro[i] := SGBobinas.Cells[4,i+1];
                  Nome := 'Bobina'+IntToStr(i+1)+'_DistCentro';
                  FBiblioteca.GravarRegistro(Nome,Bobina_DistCentro[i]);
               end;

            end;
         end;
         mrNo:
         begin
            AtualizaValores;
         end;
      End;
      BBEditarTabBob.Caption := 'Editar Tabela de Bobinas';
   end;
end;

procedure TFConfBob.AtualizaValores;
var
i : integer;
begin
{Cabeçalho Tabelas de Bobinas}
   SGBobinas.Cells[0,1] := 'Bobina 1';
   SGBobinas.Cells[0,2] := 'Bobina 2';
   SGBobinas.Cells[0,3] := 'Bobina 3';
   SGBobinas.Cells[0,4] := 'Bobina 4';
   SGBobinas.Cells[0,5] := 'Bobina 5';
   SGBobinas.Cells[1,0] := 'Número de Espiras';
   SGBobinas.Cells[2,0] := 'Raio1';
   SGBobinas.Cells[3,0] := 'Raio2';
   SGBobinas.Cells[4,0] := 'Distância Centro';

   RGBobAtiva.ItemIndex := StrToInt(Bobina_em_uso);

   {Configurações Bobinas}
   for i:=0 to 4 do
   begin
      SGBobinas.Cells[1,i+1] := Bobina_Espiras[i];
      SGBobinas.Cells[2,i+1] := Bobina_Raio1[i];
      SGBobinas.Cells[3,i+1] := Bobina_Raio2[i];
      SGBobinas.Cells[4,i+1] := Bobina_DistCentro[i];
   end;
end;

end.


