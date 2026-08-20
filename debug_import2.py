import os
os.remove('data/medicos.csv')
from models import DataManager
dm = DataManager()

# monkey patch to debug
original_add = dm.add_medico
def debug_add(record):
    print(f'add_medico called: {record.terceiro} | {record.medico} | {record.especialidade}')
    result = original_add(record)
    print(f'  -> returned ID: {result}')
    # check file after
    with open('data/medicos.csv', 'r') as f:
        lines = f.readlines()
    print(f'  File now has {len(lines)-1} records')
    return result
dm.add_medico = debug_add

added, skipped, errors = dm.import_from_csv('Importacao.csv')
print(f'Final: Added={added}, Skipped={skipped}, Errors={errors}')

with open('data/medicos.csv', 'r') as f:
    print('Final file:')
    print(f.read())