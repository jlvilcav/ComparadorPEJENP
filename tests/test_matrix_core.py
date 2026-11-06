import sys
from pathlib import Path
from io import BytesIO
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import pytest
from matrix_core import load_matrix, compare_acts, missing, completeness, filter_equal, key

ROOT=Path(__file__).resolve().parents[1]

def test_placeholder_exact():
    assert missing(' PENDIENTE ')
    assert missing('')
    assert missing('#REF!')
    assert not missing('EN TRAMITE(PENDIENTE)')

def test_normalization():
    assert key('TRÁMITE  ') == key('trámite')

def test_custom_difference_not_falsely_error():
    import pandas as pd
    from matrix_core import FIELDS
    rows=[]
    for task, destino in [('T1','X'),('T2','Y')]:
        r={name:'' for name in FIELDS}
        r.update({'fila_excel':4 if task=='T1' else 5,'tarea_origen':task,'motivo':'DEMANDA','acto':'AUTO','estado_origen':'O','estado_destino':destino,'bandeja_destino':'B','tarea_destino':'T'})
        for f in ('tarea_origen','motivo','acto','estado_origen','estado_destino','bandeja_destino','tarea_destino'):
            r[f'_key_{f}']=key(r[f])
        rows.append(r)
    df=pd.DataFrame(rows)
    result=compare_acts(df,['T1','T2'])
    assert len(result)==1
    assert result['resultado'].iloc[0]=='Transición diferente'

def test_import_synthetic_workbook():
    # Prueba sin Excel institucional: filas 1/2 de encabezados, datos desde fila 3.
    from matrix_core import excel_column_number
    from io import BytesIO
    import pandas as pd
    width=excel_column_number('AG')+1
    matrix=[[None]*width for _ in range(4)]
    headers={
        'A':'ESPECIALIDAD','G':'ORGANO JURISDICCIONAL',
        'I':'BANDEJA DE ORIGEN','K':'TAREA DE ORIGEN',
        'M':'MOTIVO DE INGRESO A LA INSTANCIA','W':'ACTO PROCESAL',
        'AA':'ESTADO DE ORIGEN','AC':'ESTADO DESTINO',
        'AE':'BANDEJA DESTINO','AG':'TAREA DESTINO',
    }
    for col,label in headers.items():matrix[1][excel_column_number(col)]=label
    data={
       'A':'FAMILIA','D':'FAMILIA CIVIL','F':'2','G':'SALA SUPERIOR',
       'I':'CALIFICACIÓN','K':'INADMISIBLES','M':'DEMANDA',
       'W':'AUTO DE PRUEBA','AA':'ELEVADO','AC':'PENDIENTE',
       'AE':'TRAMITACIÓN','AG':'TRÁMITE',
    }
    for col,value in data.items():matrix[2][excel_column_number(col)]=value
    buffer=BytesIO()
    with pd.ExcelWriter(buffer,engine='openpyxl') as writer:
        pd.DataFrame(matrix).to_excel(writer,sheet_name='PROCESO ÚNICO',header=False,index=False)
    buffer.seek(0)
    result=load_matrix(buffer)
    assert len(result)==1
    assert result['fila_excel'].tolist()==[3]
    assert result['acto'].iloc[0]=='AUTO DE PRUEBA'
    assert result['estado_destino'].iloc[0]=='PENDIENTE'
    assert completeness(result).loc[completeness(result)['Campo']=='Estado destino','Pendientes'].iloc[0]==1
