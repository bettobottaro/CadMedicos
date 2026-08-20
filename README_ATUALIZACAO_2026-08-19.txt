ATUALIZAÇÃO DO CADMEDICOS - 19/08/2026

Alterações desta versão:

1. Coluna Supl
   - Exibe apenas "SIM" quando a especialidade do médico consta em
     data\especialidades_suplementadas.csv.
   - Caso contrário, fica em branco.
   - A indicação não depende do valor importado na coluna Suplementação.

2. Destaque de suplementação
   - Linha suplementada usa vermelho escuro (#8B0000) com texto branco.

3. Importação
   - XLS, XLSX e CSV continuam aceitos.
   - Arquivos CSV/TAB em UTF-8, CP1252 e Latin-1 são aceitos.
   - Especialidade vazia é importada normalmente.
   - Duplicidades são controladas por Terceiro + Médico + Especialidade.
   - A importação foi reestruturada para processamento em lote: os dados
     são lidos uma vez e gravados ao final, evitando lentidão/travamento
     causado por carregar e salvar os JSONs a cada linha.

4. Ordenação
   - Terceiros sempre em ordem alfabética.
   - Médicos sempre em ordem alfabética dentro do Terceiro.
   - Especialidade é usada como terceiro critério para desempate.

5. Arquivo de especialidades suplementadas
   - O arquivo utilizado é:
       data\especialidades_suplementadas.csv

Compatibilidade:
   Python 3.8 x86
   Windows 7 x86
   PyInstaller 5.13.2
