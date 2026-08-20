# CadMedicos - versão compatível com Python 3.8 / Windows 7 x86

## Alterações principais

- Corrigidas anotações de tipo PEP 585 (`tuple[...]`) incompatíveis com Python 3.8.
- Mantida compatibilidade com `typing.List`, `typing.Set`, `typing.Tuple` e `typing.Optional`.
- `DataManager` passa a localizar a pasta `data` ao lado do executável quando o programa estiver congelado pelo PyInstaller.
- Mantidas as dependências compatíveis com Python 3.8:
  - xlrd 1.2.0
  - openpyxl 3.0.10
- Build preparado para PyInstaller 5.13.2.
- O executável é gerado como `dist\CadMedicos.exe`.
- A pasta `data` é copiada para `dist\data`.

## Compilação

A máquina de compilação precisa ter Python 3.8 **x86 (32 bits)**.

Execute:

    COMPILAR_WIN7_X86.bat

Ou pelo CMD:

    COMPILAR_WIN7_X86.bat

O resultado será:

    dist\CadMedicos.exe
    dist\data\

Não é recomendável usar um Python 64 bits para gerar o executável destinado ao Windows 7 x86.

## Novidades - Solic NF / NF Rec

- O painel de Terceiros possui as colunas `Solic NF` e `NF Rec`.
- Clique na caixa da primeira coluna para marcar/desmarcar Solic NF.
- Clique na caixa da segunda coluna para marcar/desmarcar NF Rec.
- `Marcar todos` marca as duas colunas para todos os Terceiros.
- `Desmarcar todos` desmarca as duas colunas para todos os Terceiros.
- As marcações são gravadas em `data\\terceiros.json` e permanecem após fechar e abrir o programa.
- Ao digitar o nome de um Médico no filtro, o painel de Terceiros passa a mostrar o Terceiro ao qual o Médico pertence.
