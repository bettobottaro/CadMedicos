import os
os.remove('data/medicos.csv')
from models import DataManager
dm = DataManager()

# monkey patch load_medicos to debug
original_load = dm.load_medicos
def debug_load():
    records = original_load()
    print(f'load_medicos returned {len(records)} records:')
    for r in records:
        print(f'  {r.id}: {r.terceiro} | {r.medico} | {r.especialidade}')
    return records
dm.load_medicos = debug_load

# monkey patch save_medicos to debug
original_save = dm.save_medicos
def debug_save(records):
    print(f'save_medicos called with {len(records)} records:')
    for r in records:
        print(f'  {r.id}: {r.terceiro} | {r.medico} | {r.especialidade}')
    original_save(records)
dm.save_medicos = debug_save

added, skipped, errors = dm.import_from_csv('Importacao.csv')
print(f'Final: Added={added}, Skipped={skipped}, Errors={errors}')