"""Genera oferta.js a partir del Excel de oferta JE6 con puntajes mínimos de JE4.

Uso:
    python scripts/generar_oferta.py JE6_OfertaTOTAL_ConCupos.xlsx JE6_OFERTA_PuntMinJE4.xlsx oferta.js

El Excel no se versiona (.gitignore). Solo se publican las columnas que usa la
calculadora: programa, institución, nivel, modalidad, jornada, campo de
conocimiento, cupos JE6 y puntaje del último elegible en JE4.
"""
import json
import re
import sys

import pandas as pd

MINUSCULAS = {"de", "del", "la", "las", "los", "el", "y", "e", "en", "para", "a", "con", "o", "u", "al"}
SIGLAS = {"CUN", "UMB", "UDCA", "ECCI", "EAN", "FABA", "UNICA", "TIC", "MD", "SST", "II", "III"}
# Artículos que forman parte del nombre propio de la institución.
ARTICULO_PROPIO = {"el bosque", "la salle", "la sabana", "los andes", "los libertadores", "la gran"}

# En el Excel muchos nombres vienen en mayúsculas sin tilde. Solo se corrigen
# palabras cuya forma con tilde no admite duda.
TILDES = {
    "administracion": "administración", "aeronautica": "aeronáutica", "agronomica": "agronómica",
    "america": "américa", "area": "área", "autonoma": "autónoma", "beltran": "beltrán",
    "bogota": "bogotá", "camara": "cámara", "citohistologia": "citohistología",
    "computacion": "computación", "conservacion": "conservación", "contaduria": "contaduría",
    "corporacion": "corporación", "diagnosticas": "diagnósticas", "economia": "economía",
    "educacion": "educación", "electrica": "eléctrica", "electronica": "electrónica",
    "electronico": "electrónico", "enfermeria": "enfermería", "fundacion": "fundación",
    "gestion": "gestión", "imagenes": "imágenes", "informatica": "informática",
    "ingenieria": "ingeniería", "ingles": "inglés", "institucion": "institución",
    "instrumentacion": "instrumentación", "matematicas": "matemáticas", "mecanica": "mecánica",
    "mecatronica": "mecatrónica", "musica": "música", "politecnico": "politécnico",
    "politica": "política", "publica": "pública", "quirurgica": "quirúrgica",
    "radiologia": "radiología", "restauracion": "restauración", "tecnica": "técnica",
    "tecnico": "técnico", "tecnologia": "tecnología", "tecnologica": "tecnológica",
    "tomas": "tomás", "turistica": "turística", "turisticas": "turísticas",
}


def palabra(p: str, primera: bool) -> str:
    # Trata por separado las partes unidas con guion, como "Superior-CUN-".
    if "-" in p:
        return "-".join(palabra(x, primera and i == 0) for i, x in enumerate(p.split("-")))
    if not p:
        return p
    nucleo = p.strip("(),.")
    if nucleo.upper() in SIGLAS:
        return p.upper()
    bajo = p.lower()
    if not primera and bajo in MINUSCULAS:
        return bajo
    base = bajo.strip("(),.")
    if base in TILDES:
        bajo = bajo.replace(base, TILDES[base])
    return bajo[:1].upper() + bajo[1:]


def titulo(texto: str) -> str:
    texto = re.sub(r"\s+", " ", str(texto)).strip()
    return " ".join(palabra(p, i == 0) for i, p in enumerate(texto.split(" ")))


def institucion(texto: str) -> str:
    sin_ciudad = re.sub(r"\s*\((BOGOT[ÁA], D\.C\.|CH[ÍI]A)\)\s*$", "", str(texto).strip())
    nombre = titulo(sin_ciudad)
    for frase in ARTICULO_PROPIO:
        art, resto = frase.split(" ", 1)
        nombre = re.sub(rf"\b{art} {resto}\b", f"{art.title()} {resto}", nombre, flags=re.I)
        nombre = re.sub(rf"\b{art.title()} {resto}\b", lambda m: m.group(0).title(), nombre)
    return nombre


def main(total: str, historico: str, salida: str) -> None:
    oferta = pd.read_excel(total)
    historia = pd.read_excel(historico)
    for tabla in (oferta, historia):
        if tabla.ID.isna().any() or tabla.ID.duplicated().any():
            raise ValueError("ID ausente o duplicado: el cruce requiere claves únicas")
    hist = historia.set_index("ID").to_dict("index")
    campos = {}
    for _, r in historia.iterrows():
        campos.setdefault(r["CINE_F_2013_AC_CAMPO_DETALLADO"], set()).add(r["CINE_F_2013_AC_CAMPO_AMPLIO"])
    extra = {
        "Construcción e ingeniería civil": "Ingeniería, Industria y Construcción",
        "Mecánica y profesiones afines a la metalistería": "Ingeniería, Industria y Construcción",
        "Biología": "Ciencias Naturales, Matemáticas y Estadística",
        "Física": "Ciencias Naturales, Matemáticas y Estadística",
        "Ciencias de la tierra": "Ciencias Naturales, Matemáticas y Estadística",
        "Programas y certificaciones interdisciplinarios relativos a administración de empresas y derecho": "Administración de Empresas y Derecho",
    }
    nombres = {int(r.CODIGO_SNIES_IES): institucion(r.INSTITUCION) for _,r in historia.iterrows()}
    registros = []
    for _, r in oferta.iterrows():
        h = hist.get(r.ID, {})
        detalle = r["CINE_F_2013_AC_CAMPO_DETALLADO"]
        opciones = campos.get(detalle, {extra.get(detalle)})
        campo = h.get("CINE_F_2013_AC_CAMPO_AMPLIO")
        if not campo:
            if len(opciones) != 1 or None in opciones:
                raise ValueError(f"Campo ambiguo o desconocido: {detalle}")
            campo = next(iter(opciones))
        minimo = h.get("PUNTAJE_ELEGIBLE_MINIMO")
        registros.append({
            "id": int(r.ID),
            "idHistorico": int(h["ID_OFERTA_PROGRAMA"]) if h else None,
            "p": titulo(r.NOMBRE_PROGRAMA_SNIES),
            "i": nombres.get(int(r.COD_IES), institucion(r.NOMBRE_IES)),
            "campo": campo,
            "nivel": str(r["NIVEL_DE_FORMACIÓN"]).strip(),
            "mod": h.get("MODALIDAD", "Virtual" if r.JORNADA_DEL_PROGRAMA == "VIRTUAL" else "Sin dato"),
            "jor": titulo(r.JORNADA_DEL_PROGRAMA),
            "cupos": int(r.TOTAL_CUPOS_ASIGNADOS_Y_REEMPLAZOS),
            "min": int(minimo) if pd.notna(minimo) else None,
        })
    registros.sort(key=lambda x: (x["p"], x["i"], x["id"]))
    with open(salida, "w", encoding="utf-8") as f:
        f.write("// Generado por scripts/generar_oferta.py. No editar a mano.\n")
        f.write("// Toda la oferta JE6; cruce por ID. min=null significa sin referencia JE4.\nwindow.OFERTA = ")
        json.dump(registros, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"{len(registros)} ofertas; {sum(x['min'] is None for x in registros)} sin referencia JE4; {sum(x['cupos'] for x in registros)} cupos")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Uso: generar_oferta.py oferta_total.xlsx historico.xlsx oferta.js")
    main(*sys.argv[1:])
