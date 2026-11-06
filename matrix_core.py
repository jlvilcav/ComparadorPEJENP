"""Reglas de lectura y comparación de la matriz PROCESO ÚNICO.

La lógica funcional es determinista, auditable y no altera el archivo fuente.
"""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import re
import unicodedata
from typing import Any

import pandas as pd

SHEET_NAME = 'PROCESO ÚNICO'
# Letras originales: columna X es código del acto, W es el texto del acto.
FIELDS = {
    'especialidad': 'A',
    'subespecialidad': 'D',
    'nivel_instancia': 'F',
    'organo': 'G',
    'bandeja_origen': 'I',
    'tarea_origen': 'K',
    'motivo': 'M',
    'proceso': 'O',
    'sentido_calificacion': 'Q',
    'sentido_fallo': 'S',
    'fallo': 'U',
    'acto': 'W',
    'tipo_audiencia': 'Y',
    'estado_origen': 'AA',
    'estado_destino': 'AC',
    'bandeja_destino': 'AE',
    'tarea_destino': 'AG',
}
LABELS = {
    'especialidad': 'Especialidad', 'subespecialidad': 'Subespecialidad',
    'nivel_instancia': 'Nivel de instancia', 'organo': 'Órgano jurisdiccional',
    'bandeja_origen': 'Bandeja de origen', 'tarea_origen': 'Tarea de origen',
    'motivo': 'Motivo de ingreso a la instancia', 'proceso': 'Proceso',
    'sentido_calificacion': 'Sentido de la calificación',
    'sentido_fallo': 'Sentido de fallo', 'fallo': 'Fallo',
    'acto': 'Acto procesal', 'tipo_audiencia': 'Tipo de audiencia',
    'estado_origen': 'Estado de origen', 'estado_destino': 'Estado destino',
    'bandeja_destino': 'Bandeja destino', 'tarea_destino': 'Tarea destino',
}
TARGET_FIELDS = ('acto', 'estado_origen', 'estado_destino', 'bandeja_destino', 'tarea_destino')
TRANSITION_FIELDS = ('estado_origen', 'estado_destino', 'bandeja_destino', 'tarea_destino')
CONTEXT_FIELDS = ('especialidad', 'subespecialidad', 'nivel_instancia', 'organo', 'bandeja_origen')
MISSING_VALUES = {'', 'PENDIENTE', 'NO DEFINIDO', 'SIN DEFINIR', '#N/A', '#REF!', '#VALUE!', '#DIV/0!', '#NAME?', '#NUM!', '#NULL!'}


def excel_column_number(label: str) -> int:
    total = 0
    for ch in label:
        total = total * 26 + (ord(ch) - ord('A') + 1)
    return total - 1


def clean(value: Any) -> str:
    if value is None or pd.isna(value):
        return ''
    return re.sub(r'\s+', ' ', str(value).replace('\u00a0', ' ')).strip()


def key(value: Any) -> str:
    """Clave para equiparar variantes de mayúsculas/espacios, sin alterar datos originales."""
    return clean(value).casefold()


def missing(value: Any) -> bool:
    return clean(value).upper() in MISSING_VALUES


def load_matrix(file_obj: Any, sheet_name: str = SHEET_NAME) -> pd.DataFrame:
    """Lee posiciones fijas (columnas reales) y encabezado en fila 2.

    Si se desplazan columnas en una nueva versión, debe revisarse el mapeo.
    """
    try:
        wb = pd.ExcelFile(file_obj, engine='openpyxl')
    except Exception as exc:
        raise ValueError('No se pudo abrir el Excel. Verifica que sea un archivo .xlsx válido.') from exc
    matches = [name for name in wb.sheet_names if key(name) == key(sheet_name)]
    if not matches:
        raise ValueError(f'No se encontró la hoja «{sheet_name}». Hojas disponibles: {", ".join(wb.sheet_names)}')
    name = matches[0]
    raw = pd.read_excel(wb, sheet_name=name, header=None, dtype=object)
    needed = max(excel_column_number(c) for c in FIELDS.values())
    if raw.shape[0] < 3 or raw.shape[1] <= needed:
        raise ValueError('La hoja no tiene la estructura esperada (encabezados en fila 2, datos desde fila 3).')
    expected_headers = {
        'A': 'ESPECIALIDAD', 'G': 'ORGANO JURISDICCIONAL',
        'I': 'BANDEJA DE ORIGEN', 'K': 'TAREA DE ORIGEN',
        'M': 'MOTIVO DE INGRESO A LA INSTANCIA', 'W': 'ACTO PROCESAL',
        'AA': 'ESTADO DE ORIGEN', 'AC': 'ESTADO DESTINO',
        'AE': 'BANDEJA DESTINO', 'AG': 'TAREA DESTINO',
    }
    errors = []
    for col, head in expected_headers.items():
        observed = clean(raw.iat[1, excel_column_number(col)]).upper()
        if observed != head:
            errors.append(f'{col}: esperado {head!r}; recibido {observed!r}')
    if errors:
        raise ValueError('La estructura de columnas cambió. Revisa el mapeo antes de analizar: ' + '; '.join(errors))

    data = raw.iloc[2:].copy()
    result = pd.DataFrame({field: data.iloc[:, excel_column_number(col)].map(clean).to_numpy() for field, col in FIELDS.items()})
    result.insert(0, 'fila_excel', list(range(3, 3 + len(result))))
    meaningful = result[list(FIELDS)].apply(lambda s: s.map(bool)).any(axis=1)
    result = result.loc[meaningful].reset_index(drop=True)
    # Las claves de comparación no sustituyen los textos originales que aparecen en resultados/exportaciones.
    for field in ('tarea_origen', 'motivo', 'acto', *TRANSITION_FIELDS):
        result[f'_key_{field}'] = result[field].map(key)
    return result


def options(df: pd.DataFrame, field: str) -> list[str]:
    """No muestra variaciones solamente por mayúsculas como opciones duplicadas."""
    representative: dict[str, str] = {}
    for value in df[field]:
        if value and key(value) not in representative:
            representative[key(value)] = value
    return sorted(representative.values(), key=lambda x: key(x))


def filter_equal(df: pd.DataFrame, field: str, value: str | None) -> pd.DataFrame:
    if not value or value == 'Todos':
        return df
    return df.loc[df[field].map(key).eq(key(value))]


def filter_tasks(df: pd.DataFrame, tasks: list[str]) -> pd.DataFrame:
    return df.loc[df['_key_tarea_origen'].isin({key(t) for t in tasks})] if tasks else df.iloc[:0].copy()


def compare_acts(df: pd.DataFrame, tasks: list[str]) -> pd.DataFrame:
    """Una fila por acto distinto. Duplicidades y transiciones se conservan en detalle.

    Ausencia no es una observación confirmada; diferentes transiciones no
    implican error funcional. La comparación requiere un motivo filtrado.
    """
    tasks = list(dict.fromkeys(key(t) for t in tasks if t))
    if not tasks:
        return pd.DataFrame(columns=['acto', 'tareas_presentes', 'tareas_ausentes', 'transiciones_distintas', 'resultado', 'filas_excel'])
    source = filter_tasks(df, tasks)
    rows = []
    for act_key, group in source.loc[~source['acto'].map(missing)].groupby('_key_acto', sort=False):
        observed = set(group['_key_tarea_origen'])
        present_tasks = [t for t in tasks if t in observed]
        absent_tasks = [t for t in tasks if t not in observed]
        # Solo calificamos transición diferente cuando el acto aparece en todas las tareas.
        route_values = set(tuple(key(r[f]) for f in TRANSITION_FIELDS) for _, r in group.iterrows())
        if absent_tasks:
            status = 'Ausente en alguna tarea'
        elif len(route_values) > 1:
            status = 'Transición diferente'
        else:
            status = 'Misma transición'
        rows.append({
            'acto': group['acto'].iloc[0],
            '_key_acto': act_key,
            'tareas_presentes': len(present_tasks),
            'tareas_ausentes': len(absent_tasks),
            'transiciones_distintas': len(route_values),
            'resultado': status,
            'filas_excel': ', '.join(str(n) for n in group['fila_excel'].tolist()),
        })
    return pd.DataFrame(rows).sort_values('acto', key=lambda s: s.str.casefold()).reset_index(drop=True) if rows else pd.DataFrame(columns=['acto','_key_acto','tareas_presentes','tareas_ausentes','transiciones_distintas','resultado','filas_excel'])


def completeness(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    return pd.DataFrame([
        {'Campo': LABELS[field], 'Informados': int((~df[field].map(missing)).sum()),
         'Pendientes': int(df[field].map(missing).sum()),
         'Completitud %': round(100 * int((~df[field].map(missing)).sum()) / total, 1) if total else 0.0}
        for field in TARGET_FIELDS
    ])


def summary_by_task(df: pd.DataFrame, tasks: list[str]) -> pd.DataFrame:
    summary = []
    for task in tasks:
        subset = filter_equal(df, 'tarea_origen', task)
        required = subset[list(TARGET_FIELDS)].apply(lambda c: c.map(missing))
        complete = int((~required.any(axis=1)).sum())
        summary.append({'Tarea de origen':task, 'Registros':len(subset),
                        'Motivos de ingreso distintos':len({key(x) for x in subset['motivo'] if not missing(x)}),
                        'Registros completos':complete,
                        'Registros con pendientes':len(subset)-complete,
                        'Completitud %':round(100*complete/len(subset),1) if len(subset) else 0.0})
    return pd.DataFrame(summary)


def export_csv(df: pd.DataFrame) -> bytes:
    """Archivo delimitado por ; con BOM UTF-8 para Excel en configuración regional española."""
    return df.to_csv(index=False,sep=';').encode('utf-8-sig')
