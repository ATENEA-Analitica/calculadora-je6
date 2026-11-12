"""Conciliación independiente del artefacto publicado contra ambos Excel."""
import json
from pathlib import Path
import pandas as pd
root = Path(__file__).resolve().parents[1]
a = pd.read_excel(root / 'JE6_OfertaTOTAL_ConCupos.xlsx').set_index('ID')
b = pd.read_excel(root / 'JE6_OFERTA_PuntMinJE4.xlsx').set_index('ID')
js = (root / 'oferta.js').read_text(encoding='utf-8')
registros = json.loads(js.split('window.OFERTA = ',1)[1].strip().removesuffix(';'))
assert set(a.index) == {r['id'] for r in registros}
assert len(registros) == len(a)
for r in registros:
    assert r['cupos'] == int(a.loc[r['id'], 'TOTAL_CUPOS_ASIGNADOS_Y_REEMPLAZOS'])
    if r['id'] in b.index:
        assert r['min'] == int(b.loc[r['id'], 'PUNTAJE_ELEGIBLE_MINIMO'])
    else:
        assert r['min'] is None
assert sum(r['cupos'] for r in registros) == a.TOTAL_CUPOS_ASIGNADOS_Y_REEMPLAZOS.sum()
print('OK: todos los ID JE6, cupos por fila y referencias JE4 conciliados por ID.')

# El resultado debe ser independiente del orden de las filas de entrada.
from unittest.mock import patch
from tempfile import TemporaryDirectory
from generar_oferta import main
with TemporaryDirectory() as tmp:
    salida = Path(tmp) / 'oferta.js'
    with patch('generar_oferta.pd.read_excel', side_effect=[a.reset_index().sample(frac=1, random_state=6), b.reset_index().sample(frac=1, random_state=4)]):
        main('total', 'historico', str(salida))
    assert salida.read_text(encoding='utf-8') == js
    duplicada = pd.concat([a.reset_index(), a.reset_index().iloc[:1]], ignore_index=True)
    with patch('generar_oferta.pd.read_excel', side_effect=[duplicada, b.reset_index()]):
        try:
            main('total', 'historico', str(salida))
        except ValueError:
            pass
        else:
            raise AssertionError('No se rechazó un ID duplicado')
print('OK: orden independiente y rechazo de claves duplicadas.')
