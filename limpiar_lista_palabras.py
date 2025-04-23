import re

# Variables modificables
ENTRADA_PATH = "palabras_en_bruto.txt"
SALIDA_PATH = "palabras_limpias.txt"

# Código
def limpiar_lineas(archivo_entrada, archivo_salida):
    with open(archivo_entrada, 'r', encoding='utf-8') as f_in, open(archivo_salida, 'w', encoding='utf-8') as f_out:
        for linea in f_in:
            # Elimina los números de página y rangos al final (con o sin 'p.' delante)
            linea_limpia = re.sub(r'[\s,:;.-]*(p\.\s*)?\d+([–,-]\d+)?(,\s*(p\.\s*)?\d+([–,-]\d+)?)*\s*$', '', linea.strip())

            # Elimina símbolos finales sobrantes (:,.;- etc.)
            linea_limpia = re.sub(r'[\s:;.,\-–]+$', '', linea_limpia)
            f_out.write(linea_limpia + '\n')

if __name__ == "__main__":
    limpiar_lineas(ENTRADA_PATH, SALIDA_PATH)
