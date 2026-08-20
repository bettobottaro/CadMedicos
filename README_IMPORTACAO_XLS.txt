CADMEDICOS - VERSAO PYTHON 3.8 / WINDOWS 7 x86

CORRECAO DE IMPORTACAO XLS

O importador agora reconhece:
1. XLS binario verdadeiro (Excel 97-2003), usando xlrd.
2. Arquivos com extensao .xls que sao, na realidade, texto delimitado por TAB.

O segundo caso e o formato do arquivo Importar.xls fornecido para teste.
Cabecalhos reconhecidos:
- Terceiro
- Medico
- Especialidade
Tambem sao aceitos Estabelecimento e Cd cgc, que sao ignorados.

A importacao mantem a regra de evitar duplicidades.

Para compilar:
    COMPILAR_WIN7_X86.bat

Requer Python 3.8 x86 (32 bits).


ATUALIZAÇÃO DO IMPORTADOR
--------------------------
- Especialidade é opcional. Se estiver vazia, o registro é importado.
- CSVs em UTF-8, CP1252 ou Latin-1 são aceitos.
- O importador identifica delimitadores ; , e TAB.
- Após a importação, a interface mostra:
  * novos registros importados;
  * duplicados ignorados, com linha e dados;
  * registros com erro, com linha e motivo.
- Duplicidade continua sendo Terceiro + Médico + Especialidade.
- O relatório exibe até 30 itens de cada categoria e informa se existem mais.
