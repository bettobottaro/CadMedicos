import os
os.remove('data/medicos.csv')
from models import DataManager
dm = DataManager()

# Add first two records manually
r1 = dm.add_medico(type('obj', (object,), {'terceiro': 'Empresa Um', 'medico': 'Doutor Um', 'especialidade': 'Cardiologia', 'contato': '3221.3000 - Bruno', 'email': 'teste1@gmail.com', 'obs': ''})())
print('After first add:')
with open('data/medicos.csv', 'r') as f:
    print(repr(f.read()))

r2 = dm.add_medico(type('obj', (object,), {'terceiro': 'Empresa Um', 'medico': 'Doutor Dois', 'especialidade': 'Urologia', 'contato': '3217.4000 - Carla', 'email': 'my@hotmail.com', 'obs': ''})())
print('After second add:')
with open('data/medicos.csv', 'r') as f:
    content = f.read()
    print(repr(content))
    print('---')
    print(content)