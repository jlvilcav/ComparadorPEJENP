"""Interfaz Streamlit — Comparador PEJENP V2.

Ejecutar: python -m streamlit run app.py
"""
from pathlib import Path
import streamlit as st
import pandas as pd

from matrix_core import (
    SHEET_NAME, FIELDS, LABELS, TARGET_FIELDS, TRANSITION_FIELDS,
    load_matrix, options, filter_equal, filter_tasks, compare_acts,
    completeness, summary_by_task, missing, key, export_csv,
)

ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT / 'data' / 'matriz_proceso_unico.xlsx'
st.set_page_config(page_title='Comparador de Reglas Procesales · PEJENP', page_icon='⚖️', layout='wide')

st.markdown('''<style>
.block-container{padding-top:1.5rem;max-width:1500px}
h1,h2,h3{letter-spacing:-.02em}
[data-testid="stMetric"]{padding:12px 14px;border:1px solid rgba(100,116,139,.22);border-radius:10px}
small{color:#64748b}
</style>''', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def cached_excel(contents: bytes) -> pd.DataFrame:
    from io import BytesIO
    return load_matrix(BytesIO(contents))

st.title('⚖️ Comparador de actos y transiciones procesales')
st.caption('PEJENP · Matriz de Reglas Funcionales y Transiciones Procesales · Especialidad Familia / Proceso Único')

with st.sidebar:
    st.header('Origen de datos')
    file = st.file_uploader('Cargar una nueva matriz Excel', type=['xlsx'], help='Se analiza la pestaña PROCESO ÚNICO. No se altera el archivo.')
    if file is None and DEFAULT.exists():
        content = DEFAULT.read_bytes()
        st.success('Matriz de ejemplo del proyecto cargada localmente.')
    elif file is not None:
        content = file.getvalue()
        st.success('Se utilizará el archivo seleccionado.')
    else:
        content = None
        st.info('Adjunta un Excel con la hoja PROCESO ÚNICO para comenzar.')
    st.caption('Los datos se procesan localmente en tu computadora mientras ejecutes el servidor local. No publiques matrices institucionales en repositorios o servidores públicos.')

if content is None:
    st.stop()
try:
    matrix = cached_excel(content)
except Exception as exc:
    st.error(f'No se puede analizar el Excel: {exc}')
    st.stop()
if matrix.empty:
    st.warning('No existen registros válidos en la hoja seleccionada.')
    st.stop()

# El contexto se filtra en cascada, conservando la posibilidad de no aplicar cada filtro.
st.subheader('1. Contexto procesal')
context = matrix
cols = st.columns(3)
filters = [('especialidad', 'Especialidad'), ('subespecialidad','Subespecialidad'),
           ('nivel_instancia','Nivel de instancia'),('organo','Órgano jurisdiccional'),
           ('bandeja_origen','Bandeja de origen')]
for i,(field, label) in enumerate(filters):
    choices=['Todos']+options(context,field)
    # Persistir solo mientras el valor siga siendo compatible con selecciones anteriores.
    session_name=f'filter_{field}'
    if st.session_state.get(session_name,'Todos') not in choices:
        st.session_state[session_name]='Todos'
    with cols[i % 3]:
        value = st.selectbox(label, choices, key=session_name)
    context=filter_equal(context,field,value)

st.subheader('2. Tareas de origen para comparar')
available_tasks=options(context,'tarea_origen')
default_example=['INADMISIBLES','PENDIENTES DE CALIFICACIÓN']
# Si dos tareas ilustrativas existen en contexto, se ofrecen como selección inicial.
if 'selected_tasks' not in st.session_state:
    example={key(x) for x in default_example}
    st.session_state.selected_tasks=[t for t in available_tasks if key(t) in example]
else:
    st.session_state.selected_tasks=[t for t in st.session_state.selected_tasks if t in available_tasks]
selected=st.multiselect('Selecciona dos o más tareas (puedes comparar una sola para explorarla)',available_tasks,key='selected_tasks',help='La comparación de ausencias solo es útil cuando seleccionas al menos dos tareas.')
if not selected:
    st.info('Selecciona al menos una tarea de origen para continuar.')
    st.stop()
filtered_tasks=filter_tasks(context,selected)

st.subheader('3. Motivo de ingreso a la instancia')
motives=options(filtered_tasks,'motivo')
motive_choices=['Todos los motivos']+motives
if st.session_state.get('selected_motive','Todos los motivos') not in motive_choices:
    st.session_state.selected_motive='Todos los motivos'
motive=st.selectbox('Filtra un motivo para comparar los mismos actos procesales en varias tareas',motive_choices,key='selected_motive')
filtered=filter_equal(filtered_tasks,'motivo',None if motive=='Todos los motivos' else motive)

st.divider()
st.subheader('4. Indicadores y completitud')
stat_cols=st.columns(4)
stat_cols[0].metric('Registros', f'{len(filtered):,}')
stat_cols[1].metric('Tareas seleccionadas', str(len(selected)))
stat_cols[2].metric('Motivos distintos', str(len({key(m) for m in filtered['motivo'] if not missing(m)})))
complete_mask=~filtered[list(TARGET_FIELDS)].apply(lambda col:col.map(missing)).any(axis=1)
stat_cols[3].metric('Filas con 5 campos informados', f'{int(complete_mask.sum())}/{len(filtered)}')

left,right=st.columns([1.05,1.35],gap='large')
with left:
    st.markdown('**Completitud por columna**')
    complete_df=completeness(filtered)
    st.dataframe(complete_df, hide_index=True, use_container_width=True)
with right:
    st.markdown('**Completitud por tarea**')
    summary=summary_by_task(filtered,selected)
    st.dataframe(summary, hide_index=True, use_container_width=True)

st.divider()
st.subheader('5. Comparador de actos procesales')
if motive == 'Todos los motivos':
    st.info('Selecciona un **motivo de ingreso específico** para comparar actos y transiciones en condiciones homogéneas. Con “Todos los motivos” se mantiene el resumen de completitud y el detalle filtrado.')
else:
    comparison=compare_acts(filtered,selected)
    total=len(comparison)
    common=int((comparison['tareas_ausentes']==0).sum()) if total else 0
    absent=total-common
    different=int((comparison['resultado']=='Transición diferente').sum()) if total else 0
    four=st.columns(4)
    for widget, title, n in zip(four,['Actos distintos','Comunes a todas','Ausentes en alguna','Transiciones diferentes'],[total,common,absent,different]):
        widget.metric(title,str(n))
    st.caption('La ausencia de un acto en una tarea o una transición diferente NO equivale por sí sola a una observación funcional confirmada.')
    subset_choice=st.radio('Mostrar', ['Todos','Ausentes en alguna tarea','Transición diferente'], horizontal=True)
    display_comp=comparison if subset_choice=='Todos' else comparison.loc[comparison['resultado']==subset_choice]
    if len(selected)>=2 and not comparison.empty:
        table=[]
        for _, comp in display_comp.iterrows():
            base={'Acto procesal':comp['acto'],'Resultado':comp['resultado']}
            for t in selected:
                matches=filtered.loc[filtered['_key_tarea_origen'].eq(key(t)) & filtered['_key_acto'].eq(comp['_key_acto'])]
                base[t] = (' | '.join(
                    f"Fila {r['fila_excel']}: {r['estado_origen'] or 'Sin dato'} → {r['estado_destino'] or 'Sin dato'}; "
                    f"bandeja: {r['bandeja_destino'] or 'Sin dato'}; tarea: {r['tarea_destino'] or 'Sin dato'}"
                    for _, r in matches.iterrows()
                ) if len(matches) else '— No registrado —')
            table.append(base)
        st.dataframe(pd.DataFrame(table), hide_index=True, use_container_width=True)
    elif len(selected)==1:
        st.info('Para identificar actos ausentes en otra tarea, selecciona al menos dos tareas de origen.')
        st.dataframe(display_comp[['acto','resultado','filas_excel']],hide_index=True,use_container_width=True)
    else:
        st.info('No se encontraron actos para estos filtros.')
    st.markdown('**Revisar transiciones de un acto**')
    acts=options(filtered.loc[~filtered['acto'].map(missing)],'acto')
    if acts:
        act=st.selectbox('Acto procesal que deseas inspeccionar', acts)
        by_act=filtered.loc[filtered['_key_acto'].eq(key(act))]
        detail_columns=['fila_excel','tarea_origen','acto',*TRANSITION_FIELDS,'sentido_calificacion','sentido_fallo','fallo','tipo_audiencia']
        st.dataframe(by_act[detail_columns].rename(columns={'fila_excel':'Fila Excel',**LABELS}), hide_index=True, use_container_width=True)
        st.download_button('Descargar transiciones del acto (CSV)',data=export_csv(by_act[detail_columns].rename(columns={'fila_excel':'Fila Excel',**LABELS})),file_name='transiciones_acto.csv',mime='text/csv')

st.divider()
st.subheader('6. Detalle de reglas y pendientes')
only_pending=st.checkbox('Mostrar únicamente filas con alguno de los cinco campos pendientes',False)
search=st.text_input('Buscar texto en motivo, acto, bandeja o tarea','')
details=filtered.copy()
if only_pending:
    details=details.loc[details[list(TARGET_FIELDS)].apply(lambda c:c.map(missing)).any(axis=1)]
if search.strip():
    target=['motivo','acto','tarea_origen','bandeja_origen','estado_destino','bandeja_destino','tarea_destino']
    mask=details[target].apply(lambda col:col.str.contains(search,case=False,regex=False,na=False)).any(axis=1)
    details=details.loc[mask]
view_fields=['fila_excel','organo','bandeja_origen','tarea_origen','motivo','acto',*TRANSITION_FIELDS,'sentido_calificacion','sentido_fallo','fallo','tipo_audiencia']
output=details[view_fields].rename(columns={'fila_excel':'Fila Excel',**LABELS})
st.caption(f'{len(output)} registros visibles. La columna «Fila Excel» permite localizar cada regla en el archivo original.')
st.dataframe(output, hide_index=True, use_container_width=True, height=420)
st.download_button('⬇️ Exportar registros filtrados (CSV)',data=export_csv(output),file_name='reglas_proceso_unico_filtradas.csv',mime='text/csv')

with st.expander('Criterios y límites de interpretación'):
    st.markdown('''
- **Dato pendiente:** celda vacía, `PENDIENTE` o valor de error definido en el catálogo de validación. Un estado como `EN TRAMITE(PENDIENTE)` no se clasifica como campo vacío.
- **Acto coincidente:** se compara ignorando diferencias de mayúsculas y espacios; el texto original permanece visible.
- **Transición diferente:** un acto común presenta dos o más combinaciones distintas de estado de origen, estado destino, bandeja destino y tarea destino.
- **No registrado:** no figura el acto en la tarea seleccionada y el motivo filtrado. No implica necesariamente una omisión.
- **Completitud:** indica presencia de datos en cinco columnas. No determina si las reglas son válidas jurídicamente ni si ciertas columnas son obligatorias para el caso específico.
- **Origen:** se lee la hoja `PROCESO ÚNICO`, encabezados de la fila 2 y registros desde la fila 3. El Excel no se modifica.
    ''')
