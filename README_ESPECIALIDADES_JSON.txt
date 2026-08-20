ATUALIZACAO - ESPECIALIDADES SUPLEMENTADAS

As Especialidades Suplementadas agora sao mantidas em dois arquivos sincronizados:

  data\especialidades_suplementadas.json  <- fonte principal
  data\especialidades_suplementadas.csv   <- copia de compatibilidade

O JSON e o CSV sao automaticamente normalizados, sem duplicidades e em ordem alfabetica.
A comparacao das especialidades ignora maiusculas/minusculas.

Se o JSON nao existir (por exemplo, em uma instalacao antiga), o programa migra os dados
existentes do CSV para o JSON e regrava os dois arquivos de forma consistente.
