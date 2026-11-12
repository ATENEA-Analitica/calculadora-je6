# Oferta publicada

La base es JE6_OfertaTOTAL_ConCupos.xlsx (214 filas). JE6_OFERTA_PuntMinJE4.xlsx aporta referencias históricas para 170 ID. El cruce es izquierdo y uno a uno por la columna ID, no por nombre, SNIES ni ID_OFERTA_PROGRAMA. Este último se conserva como idHistorico para migrar opciones guardadas. Los 44 ID sin coincidencia llevan min: null y nunca se interpretan como cero.

Programa, nivel, jornada y cupos proceden de la oferta total. Los nombres de instituciones se normalizan por código IES para conservar los logos. Campo amplio y modalidad se complementan con el archivo histórico cuando existe coincidencia; los campos detallados adicionales se clasifican mediante el mapa explícito del generador. La modalidad ausente se indica por confirmar; la jornada Virtual permite identificar esa modalidad. No se infiere modalidad presencial por jornada diurna. Se respeta la clasificación CINE de origen.

La vista por defecto incluye toda la oferta en orden alfabético. La comparación de referencias y el filtro por puntaje son opciones explícitas. Sin referencia no significa admisión garantizada ni demuestra por sí solo que el programa sea nuevo.

Regeneración: python scripts/generar_oferta.py JE6_OfertaTOTAL_ConCupos.xlsx JE6_OFERTA_PuntMinJE4.xlsx oferta.js
Verificación con fuentes locales: python scripts/verificar_cruce.py
Verificación del sitio: node scripts/verificar.mjs
