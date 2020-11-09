program Bobina_Helmholtz_v4;

uses
  Forms,
  Helmholtz_v4 in 'Helmholtz_v4.pas' {FHelmholtz},
  Motores in 'Motores.pas' {FMotores},
  Medicao in 'Medicao.pas' {FMedicao},
  ConfBob in 'ConfBob.pas' {FConfBob},
  ConfGeral in 'ConfGeral.pas' {FConfGeral},
  Conexoes in 'Conexoes.pas' {FConexoes},
  Offset in 'Offset.pas' {FOffset},
  Biblioteca in 'Biblioteca.pas' {FBiblioteca},
  Resultados in 'Resultados.pas' {FResults};

{$R *.RES}

begin
  Application.Initialize;
  Application.CreateForm(TFHelmholtz, FHelmholtz);
  Application.CreateForm(TFBiblioteca, FBiblioteca);
  Application.Run;
end.
