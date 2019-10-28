unit Helmholtz_v5;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs,
  ExtCtrls, Loco3, StdCtrls, Menus, Buttons, Registry, Biblioteca;

type
  TFHelmholtz = class(TForm)
    GBInicio: TGroupBox;
    Image1: TImage;
    Menu: TMainMenu;
    MConexao: TMenuItem;
    MConfigGeral: TMenuItem;
    MConfigBob: TMenuItem;
    MExecutar: TMenuItem;
    BBAjusteOffset: TMenuItem;
    MMedidaCompleta: TMenuItem;
    MMotores: TMenuItem;
    MAjuda: TMenuItem;
    MSair: TMenuItem;
    procedure MSairClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure MConexaoClick(Sender: TObject);
    procedure MConfigGeralClick(Sender: TObject);
    procedure MConfigBobClick(Sender: TObject);
    procedure MMedidaCompletaClick(Sender: TObject);
    procedure MMotoresClick(Sender: TObject);
    procedure BBAjusteOffsetClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);

  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  FHelmholtz: TFHelmholtz;

implementation

uses Conexoes, ConfGeral, ConfBob, Offset, Medicao, Motores;

{$R *.DFM}

procedure TFHelmholtz.MSairClick(Sender: TObject);
begin
   FBiblioteca.Parker.Fecha;
   FBiblioteca.RsDisplay1.Fecha;
   FechaLoco;
   Close;
end;

procedure TFHelmholtz.FormClose(Sender: TObject; var Action: TCloseAction);
begin
   FBiblioteca.Parker.Fecha;
   FBiblioteca.RsDisplay1.Fecha;
   FechaLoco;
end;

procedure TFHelmholtz.MConexaoClick(Sender: TObject);
begin
  if FConexoes<>nil then
  begin
    FConexoes.BringToFront;
    FHelmholtz.Hide;
    FConexoes.Show;
  end
  else
    try
      Application.CreateForm(TFConexoes, FConexoes);
      FConexoes.Pont_Jan:=@FConexoes;
      FHelmholtz.Hide;
      FConexoes.Show;
    except
      FConexoes.Release;
    end;
end;

procedure TFHelmholtz.MConfigGeralClick(Sender: TObject);
begin
  if FConfGeral<>nil then
  begin
    FConfGeral.BringToFront;
    FHelmholtz.Hide;
    FConfGeral.Show;
  end
  else
    try
      Application.CreateForm(TFConfGeral, FConfGeral);
      FConfGeral.Pont_Jan:=@FConfGeral;
      FHelmholtz.Hide;
      FConfGeral.Show;
    except
      FConfGeral.Release;
    end;
end;

procedure TFHelmholtz.MConfigBobClick(Sender: TObject);
begin
  if FConfBob<>nil then
  begin
    FConfBob.BringToFront;
    FHelmholtz.Hide;
    FConfBob.Show;
  end
  else
    try
      Application.CreateForm(TFConfBob, FConfBob);
      FConfBob.Pont_Jan:=@FConfBob;
      FHelmholtz.Hide;
      FConfBob.Show;
    except
      FConfBob.Release;
    end;
end;

procedure TFHelmholtz.MMedidaCompletaClick(Sender: TObject);
begin
  if FMedicao<>nil then
  begin
    FMedicao.BringToFront;
    FHelmholtz.Hide;
    FMedicao.Show;
  end
  else
    try
      Application.CreateForm(TFMedicao, FMedicao);
      FMedicao.Pont_Jan:=@FMedicao;
      FHelmholtz.Hide;
      FMedicao.Show;
    except
      FMedicao.Release;
    end;
end;

procedure TFHelmholtz.MMotoresClick(Sender: TObject);
begin
  if FMotores<>nil then
  begin
    FMotores.BringToFront;
    FHelmholtz.Hide;
    FMotores.Show;
  end
  else
    try
      Application.CreateForm(TFMotores, FMotores);
      FMotores.Pont_Jan:=@FMotores;
      FHelmholtz.Hide;
      FMotores.Show;
    except
      FMotores.Release;
    end;
end;

procedure TFHelmholtz.BBAjusteOffsetClick(Sender: TObject);
begin
  if FOffset<>nil then
  begin
    FOffset.BringToFront;
    FHelmholtz.Hide;
    FOffset.Show;
  end
  else
    try
      Application.CreateForm(TFOffset, FOffset);
      FOffset.Pont_Jan:=@FOffset;
      FHelmholtz.Hide;
      FOffset.Show;
    except
      FOffset.Release;
    end;
end;

procedure TFHelmholtz.FormCreate(Sender: TObject);
begin
   FBiblioteca.GravarRegistro('DirAnterior','0');
   FBiblioteca.CarregaDadosRegistro;
end;

end.
