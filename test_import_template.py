import os
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

import openpyxl

from main import CadMedicosApp
from models import DataManager, MedicoRecord


class TestImportTemplate(unittest.TestCase):
    def test_import_xlsx_with_code_columns_preserves_contact_and_email(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append([
                'Terceiro', 'Cod Terceiro', 'Medico', 'Cod Medico', 'Especialidade', 'Contato', 'Email'
            ])
            sheet.append([
                'Empresa Um', '001', 'Doutor Um', '10', 'Cardiologia', '3221.3000 - Bruno', 'teste1@gmail.com'
            ])
            sheet.append([
                'Empresa Um', '001', 'Doutor Dois', '15', 'Urologia', '3217.4000 - Carla', 'my@hotmail.com'
            ])

            file_path = os.path.join(temp_dir, 'Importacao.xlsx')
            workbook.save(file_path)

            data_dir = os.path.join(temp_dir, 'data')
            os.mkdir(data_dir)
            manager = DataManager(data_dir=data_dir)

            added, skipped, errors = manager.import_from_xlsx(file_path)

            self.assertEqual(added, 2)
            self.assertEqual(skipped, 0)
            self.assertEqual(errors, [])

            records = manager.load_medicos()
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0].terceiro, 'Empresa Um')
            self.assertEqual(records[0].medico, 'Doutor Um')
            self.assertEqual(records[0].especialidade, 'Cardiologia')
            self.assertEqual(records[0].contato, '3221.3000 - Bruno')
            self.assertEqual(records[0].email, 'teste1@gmail.com')
            self.assertEqual(records[1].contato, '3217.4000 - Carla')
            self.assertEqual(records[1].email, 'my@hotmail.com')

    def test_import_xlsx_does_not_duplicate_existing_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append([
                'Terceiro', 'Cod Terceiro', 'Medico', 'Cod Medico', 'Especialidade', 'Contato', 'Email'
            ])
            sheet.append([
                'Empresa Um', '001', 'Doutor Um', '10', 'Cardiologia', '3221.3000 - Bruno', 'teste1@gmail.com'
            ])

            file_path = os.path.join(temp_dir, 'Importacao.xlsx')
            workbook.save(file_path)
            workbook.close()

            data_dir = os.path.join(temp_dir, 'data')
            os.mkdir(data_dir)
            manager = DataManager(data_dir=data_dir)
            manager.add_medico(MedicoRecord(
                terceiro='Empresa Um',
                medico='Doutor Um',
                especialidade='Cardiologia',
                contato='3221.3000 - Bruno',
                email='teste1@gmail.com',
                obs=''
            ))

            added, skipped, errors = manager.import_from_xlsx(file_path)

            self.assertEqual(added, 0)
            self.assertEqual(skipped, 1)
            self.assertEqual(errors, [])

    def test_import_csv_with_common_variations_in_headers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, 'data')
            os.mkdir(data_dir)
            manager = DataManager(data_dir=data_dir)

            csv_path = os.path.join(temp_dir, 'Importacao.csv')
            with open(csv_path, 'w', newline='', encoding='utf-8') as file:
                file.write(
                    'terceiro;cod terceiro;medico;cod medico;especialidade;contato;email;obs\n'
                    'Empresa Um;001;Doutor Um;10;Cardiologia;3221.3000 - Bruno;teste1@gmail.com;teste\n'
                    'Empresa Um;001;Doutor Dois;15;Urologia;3217.4000 - Carla;my@hotmail.com;\n'
                )

            added, skipped, errors = manager.import_from_csv(csv_path, delimiter=';')

            self.assertEqual(added, 2)
            self.assertEqual(skipped, 0)
            self.assertEqual(errors, [])

            records = manager.load_medicos()
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0].terceiro, 'Empresa Um')
            self.assertEqual(records[0].medico, 'Doutor Um')
            self.assertEqual(records[0].especialidade, 'Cardiologia')
            self.assertEqual(records[0].contato, '3221.3000 - Bruno')
            self.assertEqual(records[0].email, 'teste1@gmail.com')
            self.assertEqual(records[0].obs, 'teste')

    def test_delete_selected_record_removes_record_from_data_manager(self):
        root = tk.Tk()
        root.withdraw()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                data_dir = os.path.join(temp_dir, 'data')
                os.mkdir(data_dir)

                manager = DataManager(data_dir=data_dir)
                manager.add_medico(MedicoRecord(
                    terceiro='Empresa Um',
                    medico='Doutor Um',
                    especialidade='Cardiologia',
                    contato='3221.3000 - Bruno',
                    email='teste1@gmail.com',
                    obs=''
                ))

                app = CadMedicosApp.__new__(CadMedicosApp)
                app.root = root
                app.data_manager = manager
                app.records = manager.load_medicos()
                app.filtered_records = list(app.records)
                app.selected_index = 0
                app.selected_terceiro = 'Empresa Um'
                app.status_var = tk.StringVar(value='Pronto')
                app.terceiro_filter = tk.Entry(root)
                app.medico_filter = tk.Entry(root)
                app.left_tree = tk.ttk.Treeview(root)
                app.right_tree = tk.ttk.Treeview(root)

                with patch('main.messagebox.askyesno', return_value=True):
                    app._on_delete_selected_record()

                self.assertEqual(len(manager.load_medicos()), 0)
        finally:
            root.destroy()

    def test_right_panel_shows_suplementacao_column_and_sim_when_specialty_is_supplemented(self):
        root = tk.Tk()
        root.withdraw()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                data_dir = os.path.join(temp_dir, 'data')
                os.mkdir(data_dir)

                manager = DataManager(data_dir=data_dir)
                manager.add_especialidade_suplementada('Cardiologia')
                manager.add_medico(MedicoRecord(terceiro='Empresa Um', medico='Doutor Um', especialidade='Cardiologia'))
                manager.add_medico(MedicoRecord(terceiro='Empresa Um', medico='Doutor Dois', especialidade='Urologia'))

                app = CadMedicosApp.__new__(CadMedicosApp)
                app.root = root
                app.data_manager = manager
                app.records = manager.load_medicos()
                app.filtered_records = list(app.records)
                app.selected_index = 0
                app.selected_terceiro = 'Empresa Um'
                app.status_var = tk.StringVar(value='Pronto')
                app.left_tree = tk.ttk.Treeview(root)
                app.right_tree = tk.ttk.Treeview(root, columns=('medico', 'especialidade', 'suplementacao'), show='headings')
                app.right_tree.heading('medico', text='Médico')
                app.right_tree.heading('especialidade', text='Especialidade')
                app.right_tree.heading('suplementacao', text='Suplementação')
                app.left_tree.insert('', tk.END, iid='0', values=('Empresa Um', '', ''))
                app.left_tree.selection_set('0')

                app._refresh_right_tree()

                self.assertEqual(app.right_tree['columns'], ('medico', 'especialidade', 'suplementacao'))
                first_row_values = app.right_tree.item(app.right_tree.get_children()[0], 'values')
                self.assertEqual(first_row_values[0], 'Doutor Um')
                self.assertEqual(first_row_values[2], 'SIM')
                second_row_values = app.right_tree.item(app.right_tree.get_children()[1], 'values')
                self.assertEqual(second_row_values[2], '')
        finally:
            root.destroy()

    def test_right_panel_shows_only_medics_from_selected_third(self):
        root = tk.Tk()
        root.withdraw()

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                data_dir = os.path.join(temp_dir, 'data')
                os.mkdir(data_dir)

                manager = DataManager(data_dir=data_dir)
                manager.add_medico(MedicoRecord(terceiro='Empresa Um', medico='Doutor Um', especialidade='Cardiologia'))
                manager.add_medico(MedicoRecord(terceiro='Empresa Um', medico='Doutor Dois', especialidade='Urologia'))
                manager.add_medico(MedicoRecord(terceiro='Empresa Dois', medico='Doutor Tres', especialidade='Dermatologia'))

                app = CadMedicosApp.__new__(CadMedicosApp)
                app.root = root
                app.data_manager = manager
                app.records = manager.load_medicos()
                app.filtered_records = list(app.records)
                app.selected_index = 0
                app.selected_terceiro = 'Empresa Um'
                app.status_var = tk.StringVar(value='Pronto')
                app.left_tree = tk.ttk.Treeview(root)
                app.right_tree = tk.ttk.Treeview(root, columns=('medico', 'especialidade', 'suplementacao'), show='headings')
                app.right_tree.heading('medico', text='Médico')
                app.right_tree.heading('especialidade', text='Especialidade')
                app.right_tree.heading('suplementacao', text='Suplementação')
                app.left_tree.insert('', tk.END, iid='0', values=('Empresa Um', '', ''))
                app.left_tree.selection_set('0')

                app._refresh_right_tree()

                self.assertEqual(len(app.right_tree.get_children()), 2)
                right_values = [app.right_tree.item(child, 'values')[0] for child in app.right_tree.get_children()]
                self.assertEqual(right_values, ['Doutor Um', 'Doutor Dois'])

                left_entries = [app.left_tree.item(child, 'values')[0] for child in app.left_tree.get_children()]
                self.assertEqual(left_entries.count('Empresa Um'), 1)
        finally:
            root.destroy()

    def test_json_persistence_keeps_third_parties_and_medicos_separate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, 'data')
            os.mkdir(data_dir)

            manager = DataManager(data_dir=data_dir)
            manager.add_medico(MedicoRecord(terceiro='Empresa Um', medico='Doutor Um', especialidade='Cardiologia', contato='1111', email='doc1@ex.com'))
            manager.add_medico(MedicoRecord(terceiro='Empresa Um', medico='Doutor Dois', especialidade='Urologia', contato='2222', email='doc2@ex.com'))

            third_file = os.path.join(data_dir, 'terceiros.json')
            doctors_file = os.path.join(data_dir, 'medicos.json')

            self.assertTrue(os.path.exists(third_file))
            self.assertTrue(os.path.exists(doctors_file))
            self.assertEqual(len(manager.load_terceiros()), 1)
            self.assertEqual(len(manager.load_medicos()), 2)
            self.assertEqual(manager.load_terceiros()[0].nome, 'Empresa Um')


if __name__ == '__main__':
    unittest.main()
