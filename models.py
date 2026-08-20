import csv
import os
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
import json
import sys


@dataclass
class TerceiroRecord:
    nome: str = ""
    contato: str = ""
    email: str = ""
    solic_nf: bool = False
    nf_rec: bool = False
    obs: str = ""
    id: int = field(default=0, init=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'contato': self.contato,
            'email': self.email,
            'solic_nf': self.solic_nf,
            'nf_rec': self.nf_rec,
            'obs': self.obs,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TerceiroRecord':
        record = cls(
            nome=data.get('nome', data.get('terceiro', '')),
            contato=data.get('contato', ''),
            email=data.get('email', ''),
            solic_nf=bool(data.get('solic_nf', False)),
            nf_rec=bool(data.get('nf_rec', False)),
            obs=data.get('obs', '')
        )
        try:
            record.id = int(data.get('id', 0) or 0)
        except (TypeError, ValueError):
            record.id = 0
        return record


def _as_bool(value) -> bool:
    """Converte corretamente SIM/NAO, 1/0, True/False para bool."""
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text in ("sim", "s", "yes", "y", "true", "1", "1.0")


@dataclass
class MedicoRecord:
    terceiro: str = ""
    medico: str = ""
    especialidade: str = ""
    obs: str = ""
    suplementacao: bool = False
    id: int = field(default=0, init=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'terceiro': self.terceiro,
            'medico': self.medico,
            'especialidade': self.especialidade,
            'obs': self.obs,
            'suplementacao': self.suplementacao
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MedicoRecord':
        record = cls(
            terceiro=data.get('terceiro', ''),
            medico=data.get('medico', ''),
            especialidade=data.get('especialidade', ''),
            obs=data.get('obs', ''),
            suplementacao=_as_bool(data.get('suplementacao', False))
        )
        try:
            record.id = int(data.get('id', 0) or 0)
        except (TypeError, ValueError):
            record.id = 0
        return record

    def matches_filter(self, terceiro_filter: str, medico_filter: str, especialidade_filter: str = "") -> bool:
        if terceiro_filter and terceiro_filter.lower() not in self.terceiro.lower():
            return False
        if medico_filter and medico_filter.lower() not in self.medico.lower():
            return False
        if especialidade_filter and especialidade_filter.lower() not in self.especialidade.lower():
            return False
        return True

    def is_duplicate_of(self, other: 'MedicoRecord') -> bool:
        return (
            self.terceiro.strip().lower() == other.terceiro.strip().lower() and
            self.medico.strip().lower() == other.medico.strip().lower() and
            self.especialidade.strip().lower() == other.especialidade.strip().lower()
        )


class DataManager:
    def __init__(self, data_dir: Optional[str] = None):
        # Mantém os dados junto ao executável quando congelado pelo PyInstaller.
        # Em modo fonte, usa a pasta do projeto.
        if data_dir is None:
            if getattr(sys, "frozen", False):
                base_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(base_dir, "data")
        self.data_dir = data_dir
        self.terceiros_file = os.path.join(data_dir, "terceiros.json")
        self.medicos_file = os.path.join(data_dir, "medicos.json")
        self.medicos_csv_file = os.path.join(data_dir, "medicos.csv")
        self.especialidades_file = os.path.join(data_dir, "especialidades_suplementadas.csv")
        self.especialidades_json_file = os.path.join(data_dir, "especialidades_suplementadas.json")
        self.app_config_file = os.path.join(data_dir, "app_config.json")
        self._ensure_data_dir()
        self._ensure_files()
        self._next_id = 1
        self._next_terceiro_id = 1
        self._especialidades_suplementadas: Set[str] = set()
        # Relatório da última importação, usado pela interface.
        self.last_import_duplicates = []
        self._migrate_legacy_data_if_needed()
        self.load_especialidades_suplementadas()

    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _ensure_files(self):
        if not os.path.exists(self.terceiros_file):
            with open(self.terceiros_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        if not os.path.exists(self.medicos_file):
            with open(self.medicos_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
        if not os.path.exists(self.especialidades_file):
            with open(self.especialidades_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['especialidade'])
        if not os.path.exists(self.app_config_file):
            with open(self.app_config_file, 'w', encoding='utf-8') as f:
                json.dump({'suplementacao_cor': '#C00000'}, f, ensure_ascii=False, indent=2)

    def get_app_config(self) -> dict:
        try:
            with open(self.app_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if not isinstance(config, dict):
                config = {}
        except Exception:
            config = {}
        if not config.get('suplementacao_cor'):
            config['suplementacao_cor'] = '#C00000'
        return config

    def get_last_valor_bruto(self) -> str:
        return self.get_app_config().get('last_valor_bruto', '')

    def set_last_valor_bruto(self, value: str):
        config = self.get_app_config()
        config['last_valor_bruto'] = value or ''
        with open(self.app_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def get_suplementacao_cor(self) -> str:
        return self.get_app_config().get('suplementacao_cor', '#C00000')

    def set_suplementacao_cor(self, color: str):
        config = self.get_app_config()
        config['suplementacao_cor'] = color
        with open(self.app_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _migrate_legacy_data_if_needed(self):
        if os.path.exists(self.medicos_csv_file):
            try:
                with open(self.medicos_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                if existing:
                    return
            except Exception:
                pass
            try:
                records = []
                with open(self.medicos_csv_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        record = MedicoRecord.from_dict(row)
                        records.append(record)
                self.save_medicos(records)
                self._next_id = max((record.id for record in records), default=0) + 1
                self._ensure_terceiros_from_medicos(records)
            except Exception:
                pass

    def _ensure_terceiros_from_medicos(self, records: List[MedicoRecord]):
        terceiros = self.load_terceiros()
        seen = {item.nome.strip().lower(): item for item in terceiros}
        for record in records:
            nome = record.terceiro.strip()
            if not nome:
                continue
            key = nome.lower()
            if key not in seen:
                terceiro = TerceiroRecord(nome=nome)
                terceiro.id = max((item.id for item in terceiros), default=0) + 1
                terceiros.append(terceiro)
                seen[key] = terceiro
        self.save_terceiros(terceiros)
        self._next_terceiro_id = max((t.id for t in terceiros), default=0) + 1

    def load_terceiros(self) -> List[TerceiroRecord]:
        try:
            with open(self.terceiros_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            records = [TerceiroRecord.from_dict(item) for item in data]
            records.sort(key=lambda r: (r.nome or "").strip().casefold())
            if records:
                self._next_terceiro_id = max((record.id for record in records), default=0) + 1
            return records
        except Exception:
            return []

    def save_terceiros(self, records: List[TerceiroRecord]):
        records = sorted(records, key=lambda r: (r.nome or "").strip().casefold())
        with open(self.terceiros_file, 'w', encoding='utf-8') as f:
            json.dump([record.to_dict() for record in records], f, ensure_ascii=False, indent=2)

    def get_terceiros(self) -> List[str]:
        terceiros = {record.nome.strip() for record in self.load_terceiros() if record.nome and record.nome.strip()}
        return sorted(terceiros)

    def add_terceiro(self, record: TerceiroRecord) -> int:
        nome = record.nome.strip()
        if not nome:
            return 0
        terceiros = self.load_terceiros()
        for existing in terceiros:
            if existing.nome.strip().lower() == nome.lower():
                record.id = existing.id
                if record.contato and not existing.contato:
                    existing.contato = record.contato
                if record.email and not existing.email:
                    existing.email = record.email
                if record.obs and not existing.obs:
                    existing.obs = record.obs
                self.save_terceiros(terceiros)
                return existing.id
        record.id = self._next_terceiro_id
        self._next_terceiro_id += 1
        terceiros.append(record)
        self.save_terceiros(terceiros)
        return record.id

    def update_terceiro(self, record: TerceiroRecord):
        terceiros = self.load_terceiros()
        for i, item in enumerate(terceiros):
            if item.id == record.id or item.nome.strip().lower() == record.nome.strip().lower():
                terceiros[i] = record
                self.save_terceiros(terceiros)
                return
        terceiros.append(record)
        self.save_terceiros(terceiros)

    def delete_terceiro(self, terceiro_nome: str):
        nome = terceiro_nome.strip()
        if not nome:
            return
        terceiros = self.load_terceiros()
        terceiros = [item for item in terceiros if item.nome.strip().lower() != nome.lower()]
        self.save_terceiros(terceiros)
        medicos = self.load_medicos()
        medicos = [item for item in medicos if item.terceiro.strip().lower() != nome.lower()]
        self.save_medicos(medicos)

    def upsert_terceiro(self, nome: str, contato: str = "", email: str = "", obs: str = "") -> TerceiroRecord:
        nome = nome.strip()
        if not nome:
            return TerceiroRecord()
        terceiros = self.load_terceiros()
        for item in terceiros:
            if item.nome.strip().lower() == nome.lower():
                if contato and not item.contato:
                    item.contato = contato
                if email and not item.email:
                    item.email = email
                if obs and not item.obs:
                    item.obs = obs
                self.save_terceiros(terceiros)
                return item
        record = TerceiroRecord(nome=nome, contato=contato, email=email, obs=obs)
        record.id = self.add_terceiro(record)
        return record

    def load_medicos(self) -> List[MedicoRecord]:
        try:
            with open(self.medicos_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            records = [MedicoRecord.from_dict(item) for item in data]
            records.sort(key=lambda r: ((r.terceiro or "").strip().casefold(), (r.medico or "").strip().casefold(), (r.especialidade or "").strip().casefold()))
            if records:
                self._next_id = max((record.id for record in records), default=0) + 1
            return records
        except Exception:
            pass

        records = []
        try:
            with open(self.medicos_csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    record = MedicoRecord.from_dict(row)
                    records.append(record)
                    if record.id >= self._next_id:
                        self._next_id = record.id + 1
        except Exception:
            pass

        if records:
            self.save_medicos(records)
        return records

    def save_medicos(self, records: List[MedicoRecord]):
        records = sorted(records, key=lambda r: ((r.terceiro or "").strip().casefold(), (r.medico or "").strip().casefold(), (r.especialidade or "").strip().casefold()))
        with open(self.medicos_file, 'w', encoding='utf-8') as f:
            json.dump([record.to_dict() for record in records], f, ensure_ascii=False, indent=2)

    def add_medico(self, record: MedicoRecord) -> int:
        record.terceiro = record.terceiro.strip()
        if record.terceiro:
            self.upsert_terceiro(record.terceiro)

        records = self.load_medicos()
        record.id = self._next_id
        self._next_id += 1
        records.append(record)
        self.save_medicos(records)
        return record.id

    def update_medico(self, record: MedicoRecord):
        records = self.load_medicos()
        for i, r in enumerate(records):
            if r.id == record.id:
                records[i] = record
                break
        self.save_medicos(records)
        if record.terceiro:
            self.upsert_terceiro(record.terceiro)

    def delete_medico(self, record_id: int):
        records = self.load_medicos()
        records = [r for r in records if r.id != record_id]
        self.save_medicos(records)

    def get_terceiros_queryset(self):
        return self.load_terceiros()

    def get_terceiro_by_name(self, nome: str) -> Optional[TerceiroRecord]:
        for item in self.load_terceiros():
            if item.nome.strip().lower() == nome.strip().lower():
                return item
        return None

    def set_terceiro_nf_flags(self, nome: str, solic_nf=None, nf_rec=None):
        """Atualiza as marcacoes de Solic NF e NF Rec de um terceiro."""
        nome_normalizado = nome.strip().lower()
        terceiros = self.load_terceiros()
        for item in terceiros:
            if item.nome.strip().lower() == nome_normalizado:
                if solic_nf is not None:
                    item.solic_nf = bool(solic_nf)
                if nf_rec is not None:
                    item.nf_rec = bool(nf_rec)
                self.save_terceiros(terceiros)
                return

    def set_all_terceiros_nf_flags(self, value: bool):
        """Marca/desmarca as duas colunas para todos os terceiros."""
        terceiros = self.load_terceiros()
        for item in terceiros:
            item.solic_nf = bool(value)
            item.nf_rec = bool(value)
        self.save_terceiros(terceiros)

    @staticmethod
    def _normalize_header(value: object) -> str:
        text = str(value or '').strip().lower()
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'[^a-z0-9]+', '', text)
        return text

    @staticmethod
    def _normalize_text(value: object, max_length: int = 0) -> str:
        text = str(value or '').strip()
        if max_length > 0 and len(text) > max_length:
            text = text[:max_length]
        return text

    @staticmethod
    def _build_field_map(headers):
        normalized = {}
        for idx, header in enumerate(headers):
            normalized[DataManager._normalize_header(header)] = idx

        field_map = {}
        aliases = {
            'terceiro': ('terceiro', 'nomecliente', 'cliente', 'empresa'),
            'medico': ('medico', 'médico', 'nomemedico'),
            'especialidade': ('especialidade', 'especialidades'),
            'contato': ('contato', 'telefone', 'tel', 'telefones', 'fone'),
            'email': ('email', 'e-mail'),
            'obs': ('obs', 'observacao', 'observacoes', 'observações', 'comentario'),
            'suplementacao': ('suplementacao', 'suplementação', 'suplementado')
        }

        for field, names in aliases.items():
            # Normaliza também os aliases para aceitar acentos, espaços,
            # hífens e pequenas variações dos cabeçalhos de origem.
            normalized_aliases = [DataManager._normalize_header(alias) for alias in names]
            for alias in normalized_aliases:
                if alias in normalized:
                    field_map[field] = normalized[alias]
                    break
        return field_map

    def _record_from_row(self, row, field_map):
        defaults = {
            'terceiro': '',
            'medico': '',
            'especialidade': '',
            'contato': '',
            'email': '',
            'obs': '',
            'suplementacao': False
        }

        for field, idx in field_map.items():
            if idx < len(row):
                defaults[field] = DataManager._normalize_text(row[idx], {
                    'terceiro': 150,
                    'medico': 150,
                    'especialidade': 100,
                    'contato': 50,
                    'email': 100,
                    'obs': 250,
                }.get(field, 0))

        # A coluna Supl é derivada exclusivamente da tabela
        # Especialidades Suplementadas. O valor vindo do arquivo de importação
        # não controla o destaque do cadastro.
        sup = self.is_especialidade_suplementada(defaults.get('especialidade', ''))

        return MedicoRecord(
            terceiro=defaults['terceiro'],
            medico=defaults['medico'],
            especialidade=defaults['especialidade'],
            obs=defaults['obs'],
            suplementacao=sup
        )

    def get_especialidades_cadastradas(self) -> List[str]:
        """Retorna todas as especialidades usadas nos cadastros, sem duplicidade."""
        values = set()
        for record in self.load_medicos():
            value = (record.especialidade or "").strip()
            if value:
                values.add(value)
        return sorted(values, key=lambda x: x.lower())

    @staticmethod
    def _especialidade_sort_key(value: str):
        text = (value or "").strip()
        normalized = unicodedata.normalize("NFKD", text)
        normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return normalized.casefold()

    @staticmethod
    def _deduplicate_especialidades(values) -> List[str]:
        """Remove duplicidades ignorando maiusculas/minusculas e preserva a grafia."""
        unique = {}
        for value in values or []:
            text = str(value or "").strip()
            if not text:
                continue
            key = text.casefold()
            if key not in unique:
                unique[key] = text
        return sorted(unique.values(), key=DataManager._especialidade_sort_key)

    def load_especialidades_suplementadas(self) -> Set[str]:
        """Carrega as especialidades do JSON; migra CSV antigo se necessario.

        O JSON passa a ser a fonte principal. O CSV continua sendo mantido como
        copia de compatibilidade, sempre sincronizado e ordenado.
        """
        values = []
        loaded_json = False

        try:
            with open(self.especialidades_json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                values = data
                loaded_json = True
        except Exception:
            loaded_json = False

        if (not loaded_json) or (loaded_json and not values):
            try:
                with open(self.especialidades_file, 'r', newline='', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row:
                            continue
                        value = str(row[0]).strip()
                        if value and self._especialidade_sort_key(value) != 'especialidade':
                            values.append(value)
            except Exception:
                values = []

        canonical = self._deduplicate_especialidades(values)
        self._especialidades_suplementadas = set(canonical)

        # Sempre normaliza e sincroniza os dois arquivos.
        self._save_especialidades_files(canonical)
        return self._especialidades_suplementadas

    def _save_especialidades_files(self, especialidades):
        canonical = self._deduplicate_especialidades(especialidades)
        self._especialidades_suplementadas = set(canonical)

        with open(self.especialidades_json_file, 'w', encoding='utf-8') as f:
            json.dump(canonical, f, ensure_ascii=False, indent=2)

        with open(self.especialidades_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['especialidade'])
            for esp in canonical:
                writer.writerow([esp])

    def save_especialidades_suplementadas(self, especialidades: Set[str]):
        self._save_especialidades_files(especialidades)

    def add_especialidade_suplementada(self, especialidade: str):
        value = str(especialidade or '').strip()
        if not value:
            return
        values = list(self._especialidades_suplementadas)
        values.append(value)
        self._save_especialidades_files(values)

    def remove_especialidade_suplementada(self, especialidade: str):
        target = str(especialidade or '').strip().casefold()
        values = [value for value in self._especialidades_suplementadas if value.casefold() != target]
        self._save_especialidades_files(values)

    def is_especialidade_suplementada(self, especialidade: str) -> bool:
        target = str(especialidade or '').strip().casefold()
        return any(value.casefold() == target for value in self._especialidades_suplementadas)

    def get_especialidades_suplementadas(self) -> List[str]:
        return sorted(self._especialidades_suplementadas, key=self._especialidade_sort_key)

    def export_to_csv(self, filepath: str, records: List[MedicoRecord]):
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['terceiro', 'medico', 'especialidade', 'suplementacao', 'obs']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow({
                    'terceiro': record.terceiro,
                    'medico': record.medico,
                    'especialidade': record.especialidade,
                    'suplementacao': 'SIM' if record.suplementacao else '',
                    'obs': record.obs
                })

    def _import_rows(self, rows) -> Tuple[int, int, List[str]]:
        """Processa linhas de importação em lote, evitando I/O e buscas O(n²)."""
        added = 0
        skipped = 0
        errors = []
        duplicates = []

        rows = list(rows)
        if not rows:
            self.last_import_duplicates = []
            return added, skipped, errors

        field_map = self._build_field_map(list(rows[0]))
        if 'terceiro' not in field_map or 'medico' not in field_map:
            errors.append("Colunas obrigatórias não encontradas. São necessárias: Terceiro e Medico.")
            self.last_import_duplicates = duplicates
            return added, skipped, errors

        # Carrega cada arquivo uma única vez. A versão anterior fazia load/save
        # para praticamente cada linha e podia parecer travada em arquivos grandes.
        existing_records = self.load_medicos()
        existing_keys = {
            (
                (r.terceiro or '').strip().casefold(),
                (r.medico or '').strip().casefold(),
                (r.especialidade or '').strip().casefold(),
            )
            for r in existing_records
        }

        terceiros = self.load_terceiros()
        terceiro_map = {
            (t.nome or '').strip().casefold(): t for t in terceiros if (t.nome or '').strip()
        }

        novos_medicos = []
        for row_idx, row in enumerate(rows[1:], start=2):
            try:
                if not any(value is not None and str(value).strip() for value in row):
                    continue

                record = self._record_from_row(row, field_map)
                if not record.terceiro.strip():
                    errors.append(f"Linha {row_idx}: Terceiro vazio.")
                    continue
                if not record.medico.strip():
                    errors.append(f"Linha {row_idx}: Medico vazio.")
                    continue

                # Cria/atualiza o Terceiro apenas em memória durante a importação.
                terceiro_key = record.terceiro.strip().casefold()
                terceiro = terceiro_map.get(terceiro_key)
                contato = self._normalize_text(row[field_map['contato']], 50) if 'contato' in field_map and field_map['contato'] < len(row) else ''
                email = self._normalize_text(row[field_map['email']], 100) if 'email' in field_map and field_map['email'] < len(row) else ''
                if terceiro is None:
                    terceiro = TerceiroRecord(nome=record.terceiro, contato=contato, email=email)
                    terceiro.id = self._next_terceiro_id
                    self._next_terceiro_id += 1
                    terceiro_map[terceiro_key] = terceiro
                    terceiros.append(terceiro)
                else:
                    if contato and not terceiro.contato:
                        terceiro.contato = contato
                    if email and not terceiro.email:
                        terceiro.email = email

                key = (
                    record.terceiro.strip().casefold(),
                    record.medico.strip().casefold(),
                    record.especialidade.strip().casefold(),
                )
                if key in existing_keys:
                    skipped += 1
                    duplicates.append(
                        f"Linha {row_idx}: {record.terceiro} | {record.medico} | "
                        f"{record.especialidade or '(sem especialidade)'}"
                    )
                    continue

                record.id = self._next_id
                self._next_id += 1
                existing_keys.add(key)
                existing_records.append(record)
                novos_medicos.append(record)
                added += 1
            except Exception as e:
                errors.append(f"Linha {row_idx}: {str(e)}")

        # Uma única gravação por cadastro.
        self.save_medicos(existing_records)
        self.save_terceiros(terceiros)
        self.last_import_duplicates = duplicates
        return added, skipped, errors

    def import_from_xls(self, filepath: str) -> Tuple[int, int, List[str]]:
        """Importa XLS verdadeiro ou XLS textual separado por TAB."""
        errors = []
        try:
            with open(filepath, 'rb') as f:
                signature = f.read(8)
            if signature == b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1':
                import xlrd
                workbook = xlrd.open_workbook(filepath, on_demand=True)
                try:
                    sheet = workbook.sheet_by_index(0)
                    rows = [sheet.row_values(i) for i in range(sheet.nrows)]
                finally:
                    workbook.release_resources()
                return self._import_rows(rows)

            encodings = ('utf-8-sig', 'cp1252', 'latin-1')
            last_error = None
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding, newline='') as f:
                        sample = f.read(8192)
                        if '\t' not in sample:
                            raise ValueError('O arquivo não é um XLS binário e não possui colunas separadas por TAB.')
                        f.seek(0)
                        return self._import_rows(csv.reader(f, delimiter='\t'))
                except UnicodeDecodeError as e:
                    last_error = e
            if last_error:
                errors.append(f"Erro de codificação do XLS textual: {last_error}")
        except ImportError:
            errors.append('Biblioteca xlrd não instalada para XLS verdadeiro. Instale com: pip install xlrd==1.2.0')
        except Exception as e:
            errors.append(f'Erro ao ler arquivo XLS: {e}')
        self.last_import_duplicates = []
        return 0, 0, errors

    def import_from_xlsx(self, filepath: str) -> Tuple[int, int, List[str]]:
        try:
            import openpyxl
            workbook = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            try:
                sheet = workbook.active
                return self._import_rows(sheet.iter_rows(values_only=True))
            finally:
                workbook.close()
        except ImportError:
            return 0, 0, ['Biblioteca openpyxl não instalada. Instale com: pip install openpyxl']
        except Exception as e:
            return 0, 0, [f'Erro ao ler arquivo XLSX: {e}']

    def import_from_csv(self, filepath: str, delimiter: Optional[str] = None):
        errors = []
        last_decode_error = None
        for encoding in ('utf-8-sig', 'cp1252', 'latin-1'):
            try:
                with open(filepath, 'r', newline='', encoding=encoding) as f:
                    sample = f.read(4096)
                    f.seek(0)
                    detected_delimiter = delimiter or self._detect_csv_delimiter(sample, [',', ';', '\t'])
                    return self._import_rows(csv.reader(f, delimiter=detected_delimiter))
            except UnicodeDecodeError as exc:
                last_decode_error = exc
        if last_decode_error:
            errors.append(f'Erro de codificação do CSV: {last_decode_error}')
        else:
            errors.append('Não foi possível ler o arquivo CSV.')
        self.last_import_duplicates = []
        return 0, 0, errors

    @staticmethod
    def _detect_csv_delimiter(sample: str, candidates: List[str]) -> str:
        if not sample:
            return ';'

        best_delimiter = ';'
        best_score = -1

        for delimiter in candidates:
            if not delimiter:
                continue
            score = 0
            for line in sample.splitlines()[:5]:
                if delimiter in line:
                    score += 1
            if score > best_score:
                best_score = score
                best_delimiter = delimiter

        return best_delimiter