"""Genera oferta.js a partir del Excel de oferta JE6 con puntajes mínimos de JE4.

Uso:
    python scripts/generar_oferta.py JE6_OFERTA_PuntMinJE4.xlsx oferta.js

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


def main(entrada: str, salida: str) -> None:
    df = pd.read_excel(entrada)
    df.columns = [c.strip() for c in df.columns]
    col = {c.upper(): c for c in df.columns}

    def c(nombre: str) -> str:
        return col[nombre]

    registros = []
    for _, r in df.iterrows():
        registros.append({
            "id": int(r[c("ID_OFERTA_PROGRAMA")]),
            "p": titulo(r[c("PROGRAMA")]),
            "i": institucion(r[c("INSTITUCION")]),
            "campo": str(r[c("CINE_F_2013_AC_CAMPO_AMPLIO")]).strip(),
            "nivel": str(r[c("NIVEL_DE_FORMACIÓN")]).strip(),
            "mod": str(r[c("MODALIDAD")]).strip(),
            "jor": titulo(r[c("JORNADA")]),
            "cupos": int(r[c("TOTAL_CUPOS_ASIGNADOS_Y_REEMPLAZOS")]),
            "min": int(r[c("PUNTAJE_ELEGIBLE_MINIMO")]),
        })
    registros.sort(key=lambda x: (x["p"], x["i"]))

    with open(salida, "w", encoding="utf-8") as f:
        f.write("// Generado por scripts/generar_oferta.py. No editar a mano.\n")
        f.write("// Oferta JE6 (cupos) con puntaje del último elegible en JE4 (min).\n")
        f.write("window.OFERTA = ")
        json.dump(registros, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"{len(registros)} programas escritos en {salida}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
