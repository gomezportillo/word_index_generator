import PyPDF2
import re
import sys

PDF_PATH = "libro.pdf"
PALABRAS_PATH = "palabras_limpias.txt"
SALIDA_PATH = "indice_generado.txt"

PALABRAS_A_IGNORAR = {"abbot", "king", "bishop", "child", "saint", "pope", "monastery", "priest", "river", "martyrs", "monk"}

def cargar_palabras(ruta_archivo):
    """
    Carga la lista de palabras a buscar en el doc
    """
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
    return [line.strip() for line in lineas if line.strip()]


def obtener_variantes(frase):
    """
    Obtiene variantes normalizadas de una frase:
    - Detecta inversión de nombres (Apellido, Nombre)
    - Divide por / ( ) ,
    - Si contiene '(s)', genera variante singular y plural
    """
    variantes = set()
    original = frase.strip()

    if ',' in original:
        partes = [p.strip() for p in original.split(',')]
        if len(partes) == 2:
            invertido = f"{partes[1]} {partes[0]}"
            variantes.add(invertido.lower())

    # Separar por / ( ) , pero mantener palabras válidas
    brutos = re.split(r'[\/(),]', original)
    for variante in brutos:
        palabras = re.findall(r'\b\w+\b', variante.strip())
        palabras_lower = [p.lower() for p in palabras]

        # Ignorar variantes de una sola letra (como 's') o que no tengan contenido útil
        if len(palabras_lower) < 1 or all(len(p) <= 1 for p in palabras_lower):
            continue

        if palabras_lower and not all(p in PALABRAS_A_IGNORAR for p in palabras_lower):
            variante_str = ' '.join(palabras_lower)
            variantes.add(variante_str)

            # Añadir plural solo si la original tenía (s)
            if '(s)' in original:
                if len(palabras_lower) >= 1:
                    ultima = palabras_lower[-1]
                    base = palabras_lower[:-1]
                    if ultima.endswith('s'):
                        variantes.add(' '.join(base + [ultima]))  # por si ya es plural
                    else:
                        variantes.add(' '.join(base + [ultima + 's']))

    return sorted(variantes)


def extraer_numero_pagina(texto, pagina):
    """
    Intenta buscar el número de la página en el encabezado
    """
    lineas = texto.strip().split('\n')
    posibles = []
    if lineas:
        posibles.extend([lineas[0], lineas[-1]])
    for linea in posibles:
        numeros = re.findall(r'\b\d{1,4}\b', linea)
        if numeros:
            return int(numeros[-1])

    print(f"Error extrayendo número de página en {pagina}")
    return None


def limpiar_partes_de_linea(texto):
    """
    Revisa si hay palabras partidas y las junta.
    """
    lineas = texto.strip().split('\n')
    texto_limpio = ""

    for i in range(len(lineas)):
        linea_actual = lineas[i].strip()

        if i > 0 and lineas[i - 1].rstrip().endswith('-'):
            # Quitar guion al final de la línea anterior y unir sin espacio
            texto_limpio = texto_limpio.rstrip()[:-1] + linea_actual
        else:
            # Añadir un espacio entre líneas normales
            texto_limpio += ' ' + linea_actual

    return texto_limpio.strip()


def indexar_palabras_en_pdf(pdf_path, palabras_path):
    """
    Busca las palabras objetivo en el PDF
    """
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

            texto_limpio = limpiar_partes_de_linea(texto)
            texto_limpio = re.sub(r'(?<=[a-zA-Z])\d{1,3}(?=\W|\s|$)', '', texto_limpio) # Elimina superindices
            texto_limpio = re.sub(r'(?<=[a-zA-Z])[-–—](?=[a-zA-Z])', ' ', texto_limpio) # Elimina guiones
            texto_lower = texto_limpio.lower()

            num_pagina_real = extraer_numero_pagina(texto, i) or (i + 1)

            for frase, variantes in variantes_por_frase.items():
                sys.stdout.write(f"\rBuscando en página {num_pagina_real} (página real {i}) 🔍")
                sys.stdout.flush()

                for variante in variantes:
                    # palabras = variante.split()
                    pattern = r'\b' + re.escape(variante) + r'\b'

                    if re.search(pattern, texto_lower):
                        if num_pagina_real not in indice[frase][variante]:
                            indice[frase][variante].append(num_pagina_real)

    print("\nBúsqueda completada mi rey 👑\n")
    return indice


def guardar_indice(indice, salida_path='indice.txt'):
    """
    Guarda las palabras y páginas encontradas en disco
    """
    with open(salida_path, 'w', encoding='utf-8') as f:
        for frase in sorted(indice.keys(), key=str.lower):
            f.write(f"{frase}\n")
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
                f.write(f"    {variante_impresa}: {paginas_str}\n")
            f.write("\n")


if __name__ == "__main__":
    indice = indexar_palabras_en_pdf(PDF_PATH, PALABRAS_PATH)
    guardar_indice(indice, SALIDA_PATH)
    print(f"Índice generado en '{SALIDA_PATH}'")
