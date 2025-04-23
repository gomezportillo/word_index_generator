import PyPDF2
import re
import sys

# Variables modificables
PDF_PATH = "libro.pdf"
PALABRAS_PATH = "palabras_limpias.txt"
SALIDA_PATH = "indice_generado.txt"

PALABRAS_A_IGNORAR = {"abbot", "king", "bishop", "child", "saint", "pope", "monastery", "priest", "river", "martyrs", "monk"}

# Código
def cargar_palabras(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    return [line.strip() for line in lineas if line.strip()]

def obtener_variantes(frase):
    variantes = set()
    original = frase.strip()

    # Detectar si es "Apellido, Nombre"
    if ',' in original:
        partes = [p.strip() for p in original.split(',')]
        if len(partes) == 2:
            invertido = f"{partes[1]} {partes[0]}"
            variantes.add(invertido.lower())

    # Separar por / ( ) , pero mantener frase completa para reconstrucción
    brutos = re.split(r'[\/(),]', original)
    for variante in brutos:
        palabras = re.findall(r'\b\w+\b', variante.strip())
        palabras_lower = [p.lower() for p in palabras]
        if palabras_lower and not all(p in PALABRAS_A_IGNORAR for p in palabras_lower):
            variante_str = ' '.join(palabras_lower)
            variantes.add(variante_str)

    return sorted(variantes)


def extraer_numero_pagina(texto):
    lineas = texto.strip().split('\n')
    posibles = []
    if lineas:
        posibles.extend([lineas[0], lineas[-1]])
    for linea in posibles:
        numeros = re.findall(r'\b\d{1,4}\b', linea)
        if numeros:
            return int(numeros[-1])
    return None

def indexar_palabras_en_pdf(pdf_path, palabras_path):
    frases = cargar_palabras(palabras_path)
    variantes_por_frase = {frase: obtener_variantes(frase) for frase in frases}
    frase_original_por_variante = {}
    for frase, variantes in variantes_por_frase.items():
        for variante in variantes:
            if variante not in frase_original_por_variante:
                frase_original_por_variante[variante] = []
            frase_original_por_variante[variante].append(frase)

    indice = {frase: {variante: [] for variante in variantes} for frase, variantes in variantes_por_frase.items()}

    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_paginas = len(reader.pages)

        for i, page in enumerate(reader.pages):
            texto = page.extract_text()
            if not texto:
                continue

            texto_lower = texto.lower()
            num_pagina_real = extraer_numero_pagina(texto) or (i + 1)

            for frase, variantes in variantes_por_frase.items():
                sys.stdout.write(f"\rBuscando en página {num_pagina_real}  🔍")
                sys.stdout.flush()

                for variante in variantes:
                    palabras = variante.split()
                    if all(palabra in texto_lower for palabra in palabras):
                        if num_pagina_real not in indice[frase][variante]:
                            indice[frase][variante].append(num_pagina_real)

    print("\nBúsqueda completada mi rey 👑\n")
    return indice

def guardar_indice(indice, salida_path='indice.txt'):
    with open(salida_path, 'w', encoding='utf-8') as archivo_indice:
        for frase in sorted(indice.keys(), key=str.lower):
            archivo_indice.write(f"{frase}\n")
            for variante, paginas in sorted(indice[frase].items(), key=lambda x: x[0].lower()):
                paginas_str = ', '.join(map(str, paginas)) if paginas else 'No encontrada'

                partes_frase = re.findall(r'\b\w+\b', frase)
                partes_frase_lower = [p.lower() for p in partes_frase]
                variante_words = variante.split()
                try:
                    variante_impresa = ' '.join(
                        partes_frase[partes_frase_lower.index(p)] if p in partes_frase_lower else p.capitalize()
                        for p in variante_words
                    )
                except ValueError:
                    variante_impresa = ' '.join([p.capitalize() for p in variante_words])
                archivo_indice.write(f"    {variante_impresa}: {paginas_str}\n")
            archivo_indice.write("\n")

    print(f"Índice generado en '{SALIDA_PATH}' 💾")

if __name__ == "__main__":
    indice = indexar_palabras_en_pdf(PDF_PATH, PALABRAS_PATH)
    guardar_indice(indice, SALIDA_PATH)
