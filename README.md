# CadMedicos

Sistema de cadastro de médicos desenvolvido em Python 3.8 com tkinter, compatível com Windows 7 x86.

## Características

1. **Campos do cadastro:**
   - Terceiro (string, 150 chars)
   - Médico (string, 150 chars)
   - Especialidade (string, 100 chars)
   - Contato (string, 50 chars)
   - Email (string, 100 chars)
   - Observações (texto, 250 chars)

2. **Filtros** para Terceiro e Médico
3. **Importação** de arquivos XLS e XLSX
4. **Dados salvos** em arquivos CSV
5. **Exportação** para CSV
6. **Edição** via duplo clique no registro
7. **Cadastro auxiliar** de Especialidades Suplementadas
8. **Destaque visual** (fundo laranja claro) para especialidades suplementadas
9. **Dois painéis sincronizados:**
   - Esquerdo: Terceiro, Contato, Email
   - Direito: Médico, Especialidade (com destaque)
10. **Prevenção de duplicatas** na importação

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Estrutura de Arquivos

```
CadMedicos/
├── main.py                 # Aplicação principal
├── models.py               # Modelos de dados e gerenciamento CSV
├── edit_form.py            # Formulário de edição/adição
├── especialidades_window.py # Janela de especialidades suplementadas
├── requirements.txt        # Dependências
├── data/                   # Pasta de dados (criada automaticamente)
│   ├── medicos.csv         # Cadastro de médicos
│   └── especialidades_suplementadas.csv  # Especialidades suplementadas
```

## Formato de Importação (XLS/XLSX)

A planilha deve conter as colunas na ordem:
1. Terceiro
2. Médico
3. Especialidade
4. Contato
5. Email
6. Observações

A primeira linha deve ser o cabeçalho.

## Compatibilidade

- Python 3.8+
- Windows 7 x86 / x64
- Windows 10/11
- Linux/macOS (com tkinter instalado)

## Atalhos de Teclado

- **Duplo clique** em qualquer linha: Editar registro
- **Filtros**: Digite nos campos de filtro para filtrar em tempo real
- **Navegação**: Use setas ou clique no painel esquerdo para sincronizar o direito

## Licença

Uso livre para fins educacionais e comerciais.