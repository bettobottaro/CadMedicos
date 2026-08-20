import csv
from models import DataManager, MedicoRecord

dm = DataManager()
import os
os.remove('data/medicos.csv')
dm._ensure_files()

existing_records = dm.load_medicos()

with open('Importacao.csv', 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row_idx, row in enumerate(reader, start=2):
        print(f'Row {row_idx}:')
        print(f'  Terceiro: "{row.get("Terceiro", "")}"')
        print(f'  Medico: "{row.get("Medico", "")}"')
        print(f'  Especialidade: "{row.get("Especialidade", "")}"')
        print(f'  Contato: "{row.get("Contato", "")}"')
        print(f'  Email: "{row.get("Email", "")}"')
        
        record = MedicoRecord(
            terceiro=str(row.get('Terceiro', '')).strip()[:150],
            medico=str(row.get('Medico', '')).strip()[:150],
            especialidade=str(row.get('Especialidade', '')).strip()[:100],
            contato=str(row.get('Contato', '')).strip()[:50],
            email=str(row.get('Email', '')).strip()[:100],
            obs=''
        )
        print(f'  Record: {record.terceiro} | {record.medico} | {record.especialidade}')
        
        is_duplicate = any(record.is_duplicate_of(existing) for existing in existing_records)
        print(f'  Duplicate: {is_duplicate}')
        
        if not is_duplicate:
            dm.add_medico(record)
            existing_records.append(record)
            print(f'  Added ID: {record.id}')
        else:
            print(f'  Skipped')