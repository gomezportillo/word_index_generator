# Genenador de índices de palabras

Este proyecto pretende ayudar a automatizar la tediosa tarea de encontrar en qué páginas de un PDF aparecen una lista de palabras y conceptos.

### Limpiar palabras

El primer script `limpiar_lista_palabras.py` limpia la lista de palabras de entrada de posibles números de páginas y otros signos de puntuación para que la búsqueda sea más precisa. Genera un archivo `palabras_limpias.txt` idéntico al original pero sin caracteres que solo empeorarían la búsqueda

Esto solo es necesario hacerlo una vez, para limpiar de ruido.

### Generar índice

Y el segundo script `generar_indice.py` busca las palabras y conceptos que hay `palabras_limpias.txt` en el PDF indicado. Recorre página a página buscando cualquier palabra en la lista y la almacena. Cuando ha terminado todas las páginas del PDF guarda las ocurrencias encontradas en el archivo `indice_generado.txt`.

Ahora mismo si un concepto con varias palabras aparece dividido entre páginas no lo detecta. Si fuera importante se puede cambiar.

---

## Instalación

1. Descargar e instalar Python de [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Instalar el módulo `PyPDF2` con `pip`

```sh
pip install PyPDF2
```

3. Descargar este proyecto y pegar dentro la lista de palabras y el PDF. Debería quedar así:

```
📁 word_index_generator/
│
├── limpiar_lista_palabras.py   ← Script para limpiar la lista de palabas de entrada
├── generar_indice.py           ← Script para generar el índice de palabras
├── palabras_en_bruto.txt       ← Lista de palabras o frases a buscar
├── libro.pdf                   ← El libro en PDF en el que queremos buscar palabras
└── README.md                   ← Este archivo
```

---

## Uso

Ambos scripts tienen variables modificables al principio. Sin cambiar nada, una ejecución normal sería

```sh
python limpiar_lista_palabras.py
```

Tras lo que se crea el archivo `palabras_limpias.txt`. Ahora, ya podemos generar el índice de palabras:

```sh
python generar_indice.py
```
