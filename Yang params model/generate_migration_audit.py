from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
MATLAB_DIR = ROOT / "Yang params model"
PYTHON_DIR = ROOT / "dengue_model"
OUTPUT_HTML = ROOT / "Auditoría de Migración Yang Params Model.html"


FILE_METADATA = {
    "ELF": {
        "category": "Ejecucion principal",
        "purpose": "Sirve para correr la simulacion principal del modelo. Prepara las condiciones iniciales, lanza el sistema ODE y devuelve la salida general.",
        "transform": "Se migro de script MATLAB a modulo Python ejecutable por CLI, reemplazando `ode45` por `solve_ivp` y separando la logica en funciones reutilizables.",
    },
    "error_fun_betas": {
        "category": "Calibracion y ajuste",
        "purpose": "Sirve para medir que tan bien se ajusta el modelo a los datos reales de campo. Ejecuta la simulacion, interpola resultados y calcula el error total.",
        "transform": "Se corrigio el bug del tiempo de interpolacion, se estructuro la carga de datos y se unifico el error de ambas especies.",
    },
    "figure_setups": {
        "category": "Visualizacion",
        "purpose": "Sirve para definir el estilo base de las graficas del proyecto. No cambia el modelo, solo la forma en que se visualizan los resultados.",
        "transform": "Paso de defaults globales de MATLAB a una funcion `setup()` con `matplotlib` y estilo reutilizable.",
    },
    "myODE_ELF": {
        "category": "Nucleo matematico",
        "purpose": "Sirve para definir el nucleo matematico del modelo. Aqui estan las ecuaciones diferenciales que describen la dinamica de ambas especies.",
        "transform": "Se adapto a Python con `numpy`, parametros explicitos de competencia y una funcion auxiliar para resolver el sistema con `solve_ivp`.",
    },
    "my_parameters": {
        "category": "Configuracion del modelo",
        "purpose": "Sirve para concentrar los parametros globales y conectar las funciones biologicas del modelo. Es el centro de configuracion del sistema.",
        "transform": "Se reemplazo `global P` por un `SimpleNamespace` y se hicieron explicitas las dependencias entre modulos.",
    },
    "params_b_fits": {
        "category": "Ajustes de literatura",
        "purpose": "Sirve para recalcular curvas y ajustes auxiliares de albopictus usando los CSVs de literatura incluidos como insumos trazables.",
        "transform": "Se eliminaron rutas absolutas, se validan entradas requeridas y se dejaron los insumos como archivos trazables en `data/params_literature`.",
    },
    "temp": {
        "category": "Dinamica termica",
        "purpose": "Sirve para generar la temperatura estacional que alimenta a muchos modulos biologicos del modelo.",
        "transform": "Se preservo la formulacion trigonometrica y se adapto para aceptar escalares y vectores `numpy`.",
    },
    "time_col_date": {
        "category": "Preparacion de datos",
        "purpose": "Sirve para preparar los datos de campo. Limpia el CSV, filtra la localidad LITA, agrega por fecha y genera `full_table_Lita.mat`.",
        "transform": "Se sustituyo `readtable/save` por `pandas` y `savemat`, incorporando limpieza real del CSV del proyecto.",
    },
    "phi_A": {
        "category": "Fecundidad y oviposicion",
        "purpose": "Sirve para calcular una tasa biologica dependiente de temperatura para la especie A dentro del bloque de fecundidad.",
        "transform": "Se migro la evaluacion polinomial a `numpy.polyval` manteniendo correspondencia 1:1.",
    },
    "phi_B": {
        "category": "Fecundidad y oviposicion",
        "purpose": "Sirve para calcular la fecundidad de la especie B combinando la tasa de picadura y la fecundidad dependiente de temperatura.",
        "transform": "Se mantuvo la estructura del producto de polinomios y se adapto a NumPy.",
    },
    "phi_p_a": {
        "category": "Fecundidad y oviposicion",
        "purpose": "Sirve para construir la tasa per capita de oviposicion de la especie A a partir de las funciones biologicas base.",
        "transform": "Se conservo la formula biologica, usando funciones Python y acceso centralizado a parametros.",
    },
    "phi_p_b": {
        "category": "Fecundidad y oviposicion",
        "purpose": "Sirve para construir la tasa per capita de oviposicion de la especie B a partir de las funciones biologicas base.",
        "transform": "Se conservo la formula biologica, usando funciones Python y acceso centralizado a parametros.",
    },
    "psi1_a": {
        "category": "Desarrollo entre etapas",
        "purpose": "Sirve para estimar una transicion temprana entre etapas en aegypti usando temperatura y mortalidad de huevo.",
        "transform": "El `polyfit` se movio fuera del camino critico para evitar recalculo en cada llamada.",
    },
    "psi1_b": {
        "category": "Desarrollo entre etapas",
        "purpose": "Sirve para estimar una tasa de desarrollo dependiente de temperatura para albopictus.",
        "transform": "Se migro la evaluacion directa del polinomio a NumPy.",
    },
    "psi2_a": {
        "category": "Desarrollo entre etapas",
        "purpose": "Sirve para calcular otra tasa de desarrollo dependiente de temperatura para la especie A.",
        "transform": "Se traslado la misma curva polinomial a Python manteniendo coeficientes y dominio operativo.",
    },
    "psi2_b": {
        "category": "Desarrollo entre etapas",
        "purpose": "Sirve para calcular otra tasa de desarrollo dependiente de temperatura para la especie B.",
        "transform": "Se traslado la misma curva polinomial a Python manteniendo coeficientes y dominio operativo.",
    },
    "muE_a": {
        "category": "Mortalidad",
        "purpose": "Sirve para calcular la mortalidad de huevos de aegypti en funcion de la temperatura.",
        "transform": "Se mantuvo la curva polinomial y se adapto a `numpy.polyval` y retorno vectorizable.",
    },
    "muE_b": {
        "category": "Mortalidad",
        "purpose": "Sirve para calcular la mortalidad de huevos de albopictus usando la relacion entre desarrollo y supervivencia.",
        "transform": "Se conservo la formula derivada y se expreso en operaciones `numpy`.",
    },
    "muF_a": {
        "category": "Mortalidad",
        "purpose": "Sirve para calcular la mortalidad de hembras adultas de aegypti.",
        "transform": "Se preservo la curva termodependiente y luego se escala desde `my_parameters`.",
    },
    "muF_b": {
        "category": "Mortalidad",
        "purpose": "Sirve para calcular la mortalidad de hembras adultas de albopictus.",
        "transform": "Se mantuvo el ajuste polinomial y la inversion asociada al lifespan.",
    },
    "muL_a": {
        "category": "Mortalidad",
        "purpose": "Sirve para calcular la mortalidad larvaria de aegypti.",
        "transform": "Se reprodujo el efecto de `fliplr` almacenando los coeficientes en el orden correcto para `numpy.polyval`.",
    },
    "muL_b": {
        "category": "Mortalidad",
        "purpose": "Sirve para calcular la mortalidad larvaria de albopictus combinando desarrollo y supervivencia.",
        "transform": "Se mantuvo la formula compuesta con polinomios de NumPy.",
    },
    "__init__": {
        "category": "Soporte Python",
        "purpose": "Sirve para exponer la API principal del paquete `dengue_model` y facilitar las importaciones desde un solo punto.",
        "transform": "Es un modulo nuevo de Python que no existia en MATLAB y organiza las exportaciones del paquete.",
    },
    "_utils": {
        "category": "Soporte Python",
        "purpose": "Sirve para reunir utilidades numericas compartidas, como divisiones seguras y compatibilidad entre escalares y vectores.",
        "transform": "Es un modulo nuevo creado para evitar repeticion y encapsular operaciones auxiliares.",
    },
    "paths": {
        "category": "Soporte Python",
        "purpose": "Sirve para centralizar las rutas del paquete y de los datos, evitando rutas absolutas dispersas.",
        "transform": "Es un modulo nuevo que reemplaza rutas dispersas y hardcodeadas por resolucion consistente con `pathlib`.",
    },
}

ORDER = [
    "ELF",
    "myODE_ELF",
    "my_parameters",
    "temp",
    "phi_A",
    "phi_B",
    "phi_p_a",
    "phi_p_b",
    "psi1_a",
    "psi1_b",
    "psi2_a",
    "psi2_b",
    "muE_a",
    "muE_b",
    "muF_a",
    "muF_b",
    "muL_a",
    "muL_b",
    "error_fun_betas",
    "time_col_date",
    "params_b_fits",
    "figure_setups",
    "__init__",
    "_utils",
    "paths",
]


DETAILED_FILE_METADATA = {
    "ELF": {
        "overview": "Este archivo es la puerta de entrada del modelo. Orquesta la simulacion completa: arma el tiempo de evaluacion, prepara condiciones iniciales, llama al solucionador y opcionalmente grafica las fracciones de compartimentos.",
        "inputs": [
            "`tfinal`, `num_points` y el vector de competencia entre especies.",
            "Opcionalmente una bandera para activar o no las figuras.",
        ],
        "outputs": [
            "Un diccionario con `t`, `y` y las fracciones por compartimento.",
            "Graficas de salida cuando `plot=True`.",
        ],
        "dependencies": ["`initial_state()`", "`solve_model()`", "`compartment_fractions()`", "`figure_setups.setup()`"],
        "flow": [
            "Construye el vector temporal de simulacion.",
            "Obtiene el estado inicial del sistema desde `my_parameters.py`.",
            "Resuelve el sistema ODE y calcula fracciones de compartimentos.",
            "Si corresponde, dibuja las curvas para inspeccion visual.",
        ],
        "code_explanation": "En el bloque clave se ve la secuencia completa del archivo: preparar entradas, resolver la dinamica y empaquetar la salida utilizable por otros scripts o por linea de comandos.",
    },
    "myODE_ELF": {
        "overview": "Aqui vive el nucleo matematico del modelo. Define las derivadas de los seis compartimentos y la logica temporal para activar la dinamica de albopictus despues del umbral definido.",
        "inputs": [
            "`t`: tiempo de simulacion.",
            "`y`: vector de estado con huevos, larvas y hembras adultas de ambas especies.",
            "`p`: vector de competencia inter-especies.",
        ],
        "outputs": [
            "Vector derivada `dydt` con la variacion instantanea de cada compartimento.",
            "Indirectamente, la solucion completa cuando se usa mediante `solve_model()`.",
        ],
        "dependencies": ["`P` desde `my_parameters.py`", "`solve_ivp`", "tasas biologicas `phi`, `psi` y `mu`"],
        "flow": [
            "Separa el estado en seis variables biologicas.",
            "Calcula nacimientos, desarrollo y mortalidad para aegypti.",
            "Activa o bloquea la dinamica de albopictus segun el tiempo.",
            "Devuelve el vector de derivadas para el integrador numerico.",
        ],
        "code_explanation": "Este snippet muestra la traduccion directa de las ecuaciones del modelo a Python. Cada termino corresponde a fecundidad, desarrollo, competencia o mortalidad.",
    },
    "my_parameters": {
        "overview": "Centraliza los parametros del modelo y conecta todas las funciones biologicas en una estructura comun. En la migracion reemplaza el viejo `global P` de MATLAB por un objeto Python reutilizable.",
        "inputs": [
            "No recibe entradas externas directas al importarse.",
            "Usa las funciones biologicas de otros modulos para construir el objeto `P`.",
        ],
        "outputs": [
            "El objeto `P` con parametros y funciones dependientes del tiempo.",
            "`DEFAULT_COMPETITION`, `equilibrium_a()` e `initial_state()`.",
        ],
        "dependencies": ["modulos `mu*`", "`phi*`", "`psi*`", "`numpy`", "`SimpleNamespace`"],
        "flow": [
            "Define constantes base del modelo.",
            "Importa las funciones biologicas por modulo.",
            "Las conecta dentro del objeto `P` para uso uniforme.",
            "Calcula estados de equilibrio e iniciales para iniciar simulaciones.",
        ],
        "code_explanation": "El bloque seleccionado deja ver como el archivo arma el entorno de parametros compartidos y como deriva un estado inicial consistente para arrancar el modelo.",
    },
    "error_fun_betas": {
        "overview": "Este archivo se usa para calibracion. Corre el modelo con un vector de betas, interpola la salida en los tiempos de muestreo y calcula el error cuadratico frente a los datos observados.",
        "inputs": [
            "Vector `p` con betas a calibrar.",
            "Opcionalmente datos ya cargados y banderas de `plot`, `verbose` o `return_details`.",
        ],
        "outputs": [
            "El error total del ajuste.",
            "Opcionalmente un paquete detallado con series, interpolaciones y errores parciales.",
        ],
        "dependencies": ["`load_field_data()`", "`simulate_segments()`", "`numpy.interp`", "`matplotlib`"],
        "flow": [
            "Carga o recibe los datos de campo.",
            "Simula el modelo por segmentos con los betas propuestos.",
            "Interpola la solucion al calendario de observaciones.",
            "Calcula el error para aegypti y albopictus y los combina.",
        ],
        "code_explanation": "Aqui se ve la logica de calibracion: transformar una corrida del modelo en un numero unico de error que luego puede minimizarse.",
    },
    "time_col_date": {
        "overview": "Prepara los datos observacionales del proyecto. Limpia el CSV bruto, filtra la localidad correcta, agrega por fecha y genera el `.mat` que usa el ajuste del modelo.",
        "inputs": [
            "Ruta al CSV de campo, localidad objetivo y ruta de salida opcionales.",
            "El archivo bruto localizado en la carpeta de datos del proyecto.",
        ],
        "outputs": [
            "Tabla agregada por fecha.",
            "Archivo `full_table_Lita.mat` listo para calibracion.",
        ],
        "dependencies": ["`pandas`", "`savemat`", "`find_field_csv()`", "`ensure_data_dir()`"],
        "flow": [
            "Lee el CSV y elimina filas espurias de encabezado.",
            "Normaliza localidad y columnas numericas.",
            "Agrupa conteos por fecha y calcula `Days_Passed`.",
            "Exporta el resultado como `.mat` para el resto del flujo.",
        ],
        "code_explanation": "El bloque principal ilustra el pipeline de limpieza de datos, que es el puente entre los datos crudos de campo y el formato que espera el modelo.",
    },
    "params_b_fits": {
        "overview": "Recalcula los ajustes auxiliares de literatura para albopictus. Este archivo no ejecuta la simulacion principal; reconstruye curvas polinomiales a partir de CSVs de referencia biologica.",
        "inputs": [
            "Directorio con CSVs de literatura.",
            "Bandera para mostrar o no graficas de verificacion.",
        ],
        "outputs": [
            "Coeficientes ajustados para mortalidad, desarrollo y fecundidad.",
            "Graficas diagnosticas opcionales.",
        ],
        "dependencies": ["`pandas`", "`numpy.polyfit`", "`matplotlib`", "`PARAMS_DATA_DIR`"],
        "flow": [
            "Valida que existan los CSVs requeridos.",
            "Ajusta polinomios a cada tabla de literatura.",
            "Deriva curvas secundarias como `mu_L_b` y `mu_E_b`.",
            "Devuelve todos los coeficientes en un diccionario reusable.",
        ],
        "code_explanation": "El archivo muestra como convertir literatura biologica en coeficientes concretos que luego alimentan las funciones del modelo.",
    },
    "figure_setups": {
        "overview": "Es un utilitario de visualizacion. Define configuracion comun de graficas para que todas las figuras del proyecto tengan un estilo consistente.",
        "inputs": ["Tamano de figura opcional."],
        "outputs": ["Objeto `fig, ax` de matplotlib ya configurado."],
        "dependencies": ["`matplotlib.pyplot`"],
        "flow": [
            "Actualiza `rcParams` globales relevantes.",
            "Crea una figura y eje base.",
            "Activa grilla y devuelve ambos objetos listos para graficar.",
        ],
        "code_explanation": "Aunque es pequeno, este archivo separa la logica de visualizacion del resto del modelo y evita repetir configuraciones de estilo.",
    },
    "temp": {
        "overview": "Genera la temperatura estacional sintetica que alimenta a casi todas las funciones biologicas. Es una pieza transversal del modelo.",
        "inputs": ["`day` como escalar o vector.", "`method` para escoger la parametrizacion termica."],
        "outputs": ["Temperatura periodica en el mismo formato del input."],
        "dependencies": ["`numpy`", "`return_like_input()`"],
        "flow": [
            "Convierte la entrada a arreglo numérico.",
            "Evalua la parametrizacion termica seleccionada.",
            "Devuelve el resultado respetando si el input era escalar o vector.",
        ],
        "code_explanation": "Este snippet enseña la ecuacion periodica que reemplaza a una serie observada y sirve como base para las tasas dependientes de temperatura.",
    },
    "__init__": {
        "overview": "Este archivo organiza la API publica del paquete. Permite importar funciones principales desde `dengue_model` sin exponer toda la estructura interna.",
        "inputs": ["El nombre del simbolo solicitado al paquete."],
        "outputs": ["La funcion o variable exportada correspondiente."],
        "dependencies": ["`__getattr__` perezoso", "modulos `ELF`, `error_fun_betas` y `my_parameters`"],
        "flow": [
            "Declara los nombres exportables del paquete.",
            "Resuelve importaciones de forma perezosa cuando se solicitan.",
            "Evita advertencias y sobrecarga innecesaria al importar el paquete completo.",
        ],
        "code_explanation": "La idea central es que el paquete no importe todo de una vez, sino solo cuando alguien realmente necesita un simbolo.",
    },
    "_utils": {
        "overview": "Agrupa utilidades numericas pequenas pero importantes. Su objetivo es evitar repetir codigo auxiliar en muchos modulos biologicos.",
        "inputs": ["Plantillas de entrada y arreglos numericos."],
        "outputs": ["Resultados numericos con formato consistente y divisiones seguras."],
        "dependencies": ["`numpy`"],
        "flow": [
            "Ajusta salidas para que respeten si la entrada era escalar o vector.",
            "Protege divisiones contra denominadores cero.",
            "Sirve como soporte invisible para modulos `phi`, `psi` y `mu`.",
        ],
        "code_explanation": "Aunque no representa biologia directamente, este archivo cuida la robustez numerica del paquete entero.",
    },
    "paths": {
        "overview": "Centraliza todas las rutas relevantes del proyecto. Evita que los modulos usen rutas absolutas o duplicadas en distintos lugares.",
        "inputs": ["No recibe entradas al importarse; usa la ubicacion del paquete como referencia."],
        "outputs": ["Constantes de ruta y funciones para localizar datos del proyecto."],
        "dependencies": ["`pathlib.Path`"],
        "flow": [
            "Define la estructura de carpetas relativa al paquete.",
            "Expone rutas a datos de campo y literatura.",
            "Incluye funciones auxiliares para localizar archivos esperados.",
        ],
        "code_explanation": "Su funcion principal es convertir la estructura de carpetas en una capa reutilizable para que el resto del codigo sea portable.",
    },
}


@dataclass
class FileEntry:
    stem: str
    kind: str
    matlab_path: Path | None
    python_path: Path | None
    matlab_code: str
    python_code: str
    category: str
    purpose: str
    transform: str
    added_lines: int
    removed_lines: int
    matlab_lines: int
    python_lines: int
    notes: list[str]


def read_text(path: Path | None) -> str:
    if path is None:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def compute_diff_stats(before: str, after: str) -> tuple[int, int]:
    diff = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        fromfile="before",
        tofile="after",
        lineterm="",
    )
    added = 0
    removed = 0
    for line in diff:
        if line.startswith("+++ ") or line.startswith("--- ") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1
    return added, removed


def infer_category(stem: str) -> str:
    if stem in FILE_METADATA:
        return FILE_METADATA[stem]["category"]
    if stem.startswith("mu"):
        return "Mortalidad"
    if stem.startswith("phi"):
        return "Fecundidad y oviposicion"
    if stem.startswith("psi"):
        return "Desarrollo entre etapas"
    return "Migracion"


def infer_purpose(stem: str) -> str:
    if stem in FILE_METADATA:
        return FILE_METADATA[stem]["purpose"]
    return "Modulo migrado desde MATLAB a Python dentro del paquete del modelo."


def infer_transform(stem: str) -> str:
    if stem in FILE_METADATA:
        return FILE_METADATA[stem]["transform"]
    return "Se adapto la implementacion a Python manteniendo la correspondencia funcional con el modulo original."


def infer_notes(stem: str, matlab_code: str, python_code: str, kind: str) -> list[str]:
    if kind == "python-only":
        return ["Modulo agregado en Python como soporte de paquete o infraestructura reutilizable."]
    if kind == "matlab-only":
        return ["No existe conversion Python asociada; este archivo sigue solo en MATLAB."]

    notes: list[str] = []
    if "ode45" in matlab_code and "solve_ivp" in python_code:
        notes.append("El integrador `ode45` se reemplazo por `scipy.integrate.solve_ivp`.")
    if "global P" in matlab_code and "SimpleNamespace" in python_code:
        notes.append("El estado global MATLAB se encapsulo en un `SimpleNamespace` compartido.")
    if "interp1" in matlab_code and "np.interp" in python_code:
        notes.append("La interpolacion de series se migro a `numpy.interp`.")
    if "readtable" in matlab_code and "pd.read_csv" in python_code:
        notes.append("La lectura tabular se migro de `readtable` a `pandas.read_csv`.")
    if "save(" in matlab_code and "savemat" in python_code:
        notes.append("La exportacion de `.mat` se migro a `scipy.io.savemat`.")
    if "load(" in matlab_code and "loadmat" in python_code:
        notes.append("La carga de `.mat` se migro a `scipy.io.loadmat`.")
    if "polyfit" in matlab_code and "np.polyfit" in python_code:
        notes.append("Los ajustes polinomiales se migraron a NumPy.")
    if "fliplr" in matlab_code and "polyval" in matlab_code and "np.polyval" in python_code:
        notes.append("Se reviso el orden de coeficientes para reproducir el comportamiento de `fliplr`.")
    if stem == "params_b_fits":
        notes.append("El modulo ahora valida de forma explicita que existan los CSVs de literatura requeridos.")
    if stem == "error_fun_betas":
        notes.append("Se corrigio el uso del vector temporal para la interpolacion y se expuso una API reusable.")
    if not notes:
        notes.append("Se mantiene una correspondencia funcional 1:1 con adaptaciones de sintaxis, imports y estructura de paquete.")
    return notes


def detail_profile(stem: str, category: str, purpose: str, kind: str) -> dict:
    if stem in DETAILED_FILE_METADATA:
        return DETAILED_FILE_METADATA[stem]

    if stem.startswith("mu"):
        stage = "mortalidad biologica" if kind != "python-only" else "soporte"
        return {
            "overview": f"Este archivo encapsula una tasa de {stage}. Toma el tiempo, lo traduce a temperatura y devuelve la curva numerica que usa el modelo para esa etapa o especie.",
            "inputs": ["`day` como escalar o vector temporal."],
            "outputs": ["Una tasa numerica de mortalidad lista para usarse dentro del sistema ODE."],
            "dependencies": ["`temp()`", "`numpy.polyval` o relaciones polinomiales equivalentes", "`return_like_input()` cuando aplica"],
            "flow": [
                "Convierte tiempo a temperatura mediante `temp(day, 0)`.",
                "Evalua uno o varios polinomios biologicos.",
                "Devuelve la tasa final en el formato esperado por el resto del modelo.",
            ],
            "code_explanation": "El patron comun de estos archivos es: obtener temperatura, evaluar la curva calibrada y devolver una tasa escalar o vectorial consistente.",
        }
    if stem.startswith("phi"):
        return {
            "overview": "Este archivo participa en el bloque de fecundidad y oviposicion. Su responsabilidad es traducir temperatura o parametros biologicos en una tasa de puesta o fecundidad utilizable por el modelo.",
            "inputs": ["`day` como tiempo de evaluacion."],
            "outputs": ["Una tasa biologica de fecundidad u oviposicion."],
            "dependencies": ["`temp()`", "funciones biologicas relacionadas", "`numpy.polyval`"],
            "flow": [
                "Obtiene temperatura para el instante evaluado.",
                "Evalua la curva biologica correspondiente.",
                "Combina la curva con otros parametros si el archivo representa una tasa compuesta.",
            ],
            "code_explanation": "En esta familia de funciones, la temperatura se convierte en fecundidad o puesta mediante curvas calibradas y combinaciones biologicamente interpretables.",
        }
    if stem.startswith("psi"):
        return {
            "overview": "Este archivo calcula una tasa de desarrollo entre etapas del ciclo de vida. Forma parte del motor biologico que mueve el sistema entre huevo, larva y adulto.",
            "inputs": ["`day` como tiempo o calendario biologico."],
            "outputs": ["Una tasa de desarrollo dependiente de temperatura."],
            "dependencies": ["`temp()`", "`numpy.polyval` o `numpy.polyfit`", "parametros del modelo cuando aplica"],
            "flow": [
                "Convierte tiempo a temperatura.",
                "Evalua una curva de desarrollo ajustada a datos biologicos.",
                "Devuelve la tasa de transicion que usa el sistema ODE.",
            ],
            "code_explanation": "El archivo transforma temperatura en velocidad de cambio entre etapas, de manera que el sistema ODE pueda mover masa entre compartimentos.",
        }

    if kind == "python-only":
        return {
            "overview": f"Este archivo es un modulo de soporte Python. {purpose}",
            "inputs": ["Entradas internas del paquete segun el modulo que lo invoque."],
            "outputs": ["Utilidades, configuraciones o rutas reutilizables."],
            "dependencies": ["Otros modulos del paquete cuando corresponde."],
            "flow": [
                "Encapsula una responsabilidad transversal del paquete.",
                "Evita repetir codigo o configuracion en multiples archivos.",
            ],
            "code_explanation": "Su valor esta en la infraestructura del paquete mas que en la dinamica biologica.",
        }

    return {
        "overview": purpose,
        "inputs": ["Depende del tiempo o de parametros del modelo segun el archivo."],
        "outputs": ["Una salida intermedia o final utilizada por la simulacion."],
        "dependencies": ["Otros modulos del paquete relacionados con su categoria."],
        "flow": [
            "Recibe entradas del flujo de simulacion.",
            "Aplica la logica del modulo.",
            "Devuelve un valor o estructura consumida por el resto del sistema.",
        ],
        "code_explanation": "El snippet representa la seccion principal del archivo y como se integra al resto del modelo.",
    }


def first_function_snippet(code: str, fallback_lines: int = 14) -> str:
    lines = code.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def ") or stripped.startswith("class "):
            return "\n".join(lines[idx : idx + fallback_lines]).strip()
    return "\n".join(lines[:fallback_lines]).strip()


def first_meaningful_matlab_snippet(code: str, fallback_lines: int = 14) -> str:
    lines = code.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("function ") or stripped.startswith("clearvars") or stripped.startswith("global "):
            return "\n".join(lines[idx : idx + fallback_lines]).strip()
    return "\n".join(lines[:fallback_lines]).strip()


def collect_matching_lines(code: str, patterns: list[str], *, max_lines: int = 3) -> list[str]:
    matches: list[str] = []
    for line in code.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("%"):
            continue
        if any(re.search(pattern, line) for pattern in patterns):
            normalized = stripped if len(stripped) <= 180 else stripped[:177] + "..."
            if normalized not in matches:
                matches.append(normalized)
        if len(matches) >= max_lines:
            break
    return matches


def infer_alerts(stem: str, matlab_code: str, python_code: str) -> list[dict]:
    alerts: list[dict] = []

    python_constant_lines = collect_matching_lines(
        python_code,
        [
            r"^\s*(COEFF\w*|COEFFICIENTS\w*|DEFAULT_COMPETITION|TEMP|EP|POLYFIT|development_time_[xy]|egg_l1_[xy]|so|c|k1|k2|u1|u2|v)\s*=",
            r"^\s*[A-Za-z_]\w*\s*=\s*np\.array\(",
        ],
    )
    matlab_constant_lines = collect_matching_lines(
        matlab_code,
        [
            r"^\s*\w+\s*=\s*\[[^\]]*\d",
            r"^\s*coeff\w*\s*=",
            r"^\s*coefficients\w*\s*=",
            r"^\s*(So|c|k1|k2|u1|u2|v)\s*=",
        ],
    )
    if python_constant_lines or matlab_constant_lines:
        alerts.append(
            {
                "level": "warning",
                "title": "Parametros o coeficientes hardcodeados",
                "message": "El archivo contiene constantes numericas incrustadas directamente en el codigo. Si cambia la calibracion o la fuente cientifica, este archivo requerira edicion manual.",
                "evidence": python_constant_lines or matlab_constant_lines,
            }
        )

    embedded_data_lines = collect_matching_lines(
        python_code,
        [
            r"=\s*np\.array\(\s*\[",
            r"=\s*\[[^\]]*,[^\]]*,[^\]]*,",
        ],
    ) + collect_matching_lines(
        matlab_code,
        [
            r"=\s*\[[^\]]*,[^\]]*,[^\]]*,",
            r"polyfit\(",
        ],
    )
    if embedded_data_lines:
        alerts.append(
            {
                "level": "warning",
                "title": "Datos o curvas pegadas en el archivo",
                "message": "Se detectaron tablas, series o puntos de ajuste embebidos en el codigo. Esto reduce trazabilidad cuando ya no se quiera considerar esos datos o se quiera reemplazarlos por una fuente externa.",
                "evidence": embedded_data_lines[:3],
            }
        )

    threshold_lines = collect_matching_lines(
        python_code,
        [
            r"\bif\s+t\s*<\s*\d+",
            r"\b355(?:\.0)?\b",
            r"\b371(?:\.0)?\b",
        ],
    ) + collect_matching_lines(
        matlab_code,
        [
            r"\bif\s+t\s*<\s*\d+",
            r"\b355\b",
            r"\b371\b",
        ],
    )
    if threshold_lines:
        alerts.append(
            {
                "level": "info",
                "title": "Umbral temporal fijo dentro del codigo",
                "message": "El archivo usa un valor temporal fijo para activar una logica del modelo. Si este criterio cambia, no bastara con cambiar datos: habra que modificar codigo.",
                "evidence": threshold_lines[:3],
            }
        )

    if stem == "temp" and python_constant_lines:
        alerts.append(
            {
                "level": "warning",
                "title": "Parametrizacion de temperatura embebida",
                "message": "La funcion de temperatura usa constantes internas para definir la curva estacional. Si en el futuro quieres reemplazar esos supuestos por una fuente dinamica, este archivo es un punto critico.",
                "evidence": python_constant_lines[:3],
            }
        )

    return alerts


def build_detail_payload(
    stem: str,
    category: str,
    purpose: str,
    transform: str,
    kind: str,
    notes: list[str],
    matlab_code: str,
    python_code: str,
) -> dict:
    profile = detail_profile(stem, category, purpose, kind)
    python_snippet = first_function_snippet(python_code) if python_code else ""
    matlab_snippet = first_meaningful_matlab_snippet(matlab_code) if matlab_code else ""
    alerts = infer_alerts(stem, matlab_code, python_code)
    return {
        "overview": profile["overview"],
        "inputs": profile["inputs"],
        "outputs": profile["outputs"],
        "dependencies": profile["dependencies"],
        "flow": profile["flow"],
        "migrationNotes": notes,
        "alerts": alerts,
        "codeExplanation": profile["code_explanation"],
        "pythonSnippet": python_snippet,
        "matlabSnippet": matlab_snippet,
        "transform": transform,
    }


def rel_href(path: Path | None) -> str | None:
    if path is None:
        return None
    return path.relative_to(ROOT).as_posix()


def stem_sort_key(stem: str) -> tuple[int, str]:
    if stem in ORDER:
        return (ORDER.index(stem), stem)
    return (len(ORDER) + 1, stem.lower())


def collect_files() -> tuple[dict[str, Path], dict[str, Path]]:
    matlab_files = {path.stem: path for path in MATLAB_DIR.glob("*.m")}
    python_files = {path.stem: path for path in PYTHON_DIR.glob("*.py")}
    return matlab_files, python_files


def build_entries() -> list[FileEntry]:
    matlab_files, python_files = collect_files()
    stems = sorted(set(matlab_files) | set(python_files), key=stem_sort_key)
    entries: list[FileEntry] = []

    for stem in stems:
        matlab_path = matlab_files.get(stem)
        python_path = python_files.get(stem)
        if matlab_path and python_path:
            kind = "paired"
        elif python_path:
            kind = "python-only"
        else:
            kind = "matlab-only"

        matlab_code = read_text(matlab_path)
        python_code = read_text(python_path)
        added, removed = compute_diff_stats(matlab_code, python_code)
        entries.append(
            FileEntry(
                stem=stem,
                kind=kind,
                matlab_path=matlab_path,
                python_path=python_path,
                matlab_code=matlab_code,
                python_code=python_code,
                category=infer_category(stem),
                purpose=infer_purpose(stem),
                transform=infer_transform(stem),
                added_lines=added,
                removed_lines=removed,
                matlab_lines=len(matlab_code.splitlines()),
                python_lines=len(python_code.splitlines()),
                notes=infer_notes(stem, matlab_code, python_code, kind),
            )
        )

    return entries


def build_summary(entries: Iterable[FileEntry]) -> dict:
    entries = list(entries)
    matlab_count = sum(1 for entry in entries if entry.matlab_path is not None)
    python_count = sum(1 for entry in entries if entry.python_path is not None)
    paired_count = sum(1 for entry in entries if entry.kind == "paired")
    python_only_count = sum(1 for entry in entries if entry.kind == "python-only")
    matlab_only_count = sum(1 for entry in entries if entry.kind == "matlab-only")
    coverage = round((paired_count / matlab_count) * 100, 1) if matlab_count else 0.0

    total_added = sum(entry.added_lines for entry in entries)
    total_removed = sum(entry.removed_lines for entry in entries)
    most_changed = max(entries, key=lambda entry: entry.added_lines + entry.removed_lines, default=None)

    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "matlabCount": matlab_count,
        "pythonCount": python_count,
        "pairedCount": paired_count,
        "pythonOnlyCount": python_only_count,
        "matlabOnlyCount": matlab_only_count,
        "coveragePercent": coverage,
        "totalAddedLines": total_added,
        "totalRemovedLines": total_removed,
        "mostChangedStem": most_changed.stem if most_changed else None,
        "methodology": (
            f"Se inspeccionaron {matlab_count} archivos MATLAB canonicos y {python_count} modulos Python actuales. "
            f"De ellos, {paired_count} conservan correspondencia directa 1:1 y {python_only_count} son modulos "
            "de soporte agregados en Python para empaquetado, rutas y utilidades compartidas."
        ),
        "regenerateCommand": "python generate_migration_audit.py",
    }


def serialize(entries: list[FileEntry], summary: dict) -> dict:
    payload = {
        "summary": summary,
        "entries": [
            {
                "id": entry.stem,
                "kind": entry.kind,
                "statusLabel": (
                    "Migrado 1:1"
                    if entry.kind == "paired"
                    else "Nuevo en Python"
                    if entry.kind == "python-only"
                    else "Solo MATLAB"
                ),
                "matlabName": entry.matlab_path.name if entry.matlab_path else "No existe",
                "pythonName": entry.python_path.name if entry.python_path else "No existe",
                "matlabRelPath": rel_href(entry.matlab_path),
                "pythonRelPath": rel_href(entry.python_path),
                "category": entry.category,
                "purpose": entry.purpose,
                "transform": entry.transform,
                "notes": entry.notes,
                "detail": build_detail_payload(
                    stem=entry.stem,
                    category=entry.category,
                    purpose=entry.purpose,
                    transform=entry.transform,
                    kind=entry.kind,
                    notes=entry.notes,
                    matlab_code=entry.matlab_code,
                    python_code=entry.python_code,
                ),
                "matlabLines": entry.matlab_lines,
                "pythonLines": entry.python_lines,
                "addedLines": entry.added_lines,
                "removedLines": entry.removed_lines,
                "matlabCode": entry.matlab_code,
                "pythonCode": entry.python_code,
            }
            for entry in entries
        ],
    }
    return payload


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoría de Migración: Yang Params Model</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/5.2.0/diff.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        :root {
            color-scheme: light;
            --page-bg: #f6f8fc;
            --page-bg-soft: #eef4fb;
            --page-bg-elevated: #ffffff;
            --panel-bg: rgba(255, 255, 255, 0.92);
            --panel-strong: #ffffff;
            --panel-muted: #f6f8fb;
            --border: #d8e0ea;
            --border-strong: #c7d2e1;
            --text: #0f172a;
            --text-muted: #475569;
            --text-soft: #64748b;
            --accent: #58a6ff;
            --accent-strong: #1f6feb;
            --success-bg: rgba(46, 160, 67, 0.15);
            --success-border: #2ea043;
            --success-text: #1f7a39;
            --danger-bg: rgba(248, 81, 73, 0.16);
            --danger-border: #f85149;
            --danger-text: #b42318;
            --warning-bg: rgba(210, 153, 34, 0.16);
            --warning-border: #d29922;
            --warning-text: #9a6700;
            --info-bg: rgba(56, 139, 253, 0.16);
            --info-border: #388bfd;
            --info-text: #0b5cab;
            --diff-bg: #0f1720;
            --diff-bg-alt: #111926;
            --diff-header: #0b1220;
            --diff-text: #e5edf5;
            --diff-muted: #94a3b8;
            --shadow-lg: 0 24px 60px rgba(15, 23, 42, 0.12);
        }
        body {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top, rgba(56, 139, 253, 0.18), transparent 24%),
                linear-gradient(180deg, #f8fbff 0%, #eef3f8 100%);
        }
        .panel-scroll::-webkit-scrollbar { width: 10px; height: 10px; }
        .panel-scroll::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 999px; }
        .panel-scroll::-webkit-scrollbar-track { background: var(--panel-muted); }
        .tab-active { border-bottom: 2px solid var(--accent); color: var(--accent); font-weight: 700; }
        .tab-inactive { color: var(--text-muted); font-weight: 600; }
        .tab-inactive:hover { color: var(--text); }
        .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
        .glass-panel {
            background: var(--panel-bg);
            border-color: var(--border) !important;
            box-shadow: var(--shadow-lg);
            backdrop-filter: blur(18px);
        }
        .summary-card { position: relative; overflow: hidden; }
        .summary-card::after { content: ""; position: absolute; inset: auto -20% -45% auto; width: 120px; height: 120px; border-radius: 999px; background: rgba(88, 166, 255, 0.12); pointer-events: none; }
        .review-input {
            background: var(--panel-muted);
            border: 1px solid var(--border);
            color: var(--text);
        }
        .review-input::placeholder { color: var(--text-soft); }
        .review-input:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 1px var(--accent);
        }
        .nav-button {
            background: var(--panel-muted);
            border: 1px solid var(--border);
            color: var(--text-muted);
        }
        .nav-button:hover { background: #151b23; color: var(--text); }
        .nav-button-disabled {
            background: rgba(48, 54, 61, 0.45);
            border: 1px solid var(--border);
            color: var(--text-soft);
            cursor: not-allowed;
        }
        .pill-badge, .pill-neutral {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            border-radius: 999px;
            border: 1px solid var(--border);
            padding: 0.2rem 0.65rem;
            font-size: 11px;
            font-weight: 700;
            line-height: 1.3;
        }
        .pill-neutral {
            background: var(--panel-muted);
            color: var(--text-muted);
        }
        .kind-paired {
            background: var(--success-bg);
            border-color: var(--success-border);
            color: var(--success-text);
        }
        .kind-python-only {
            background: var(--info-bg);
            border-color: var(--info-border);
            color: var(--info-text);
        }
        .kind-matlab-only {
            background: var(--warning-bg);
            border-color: var(--warning-border);
            color: var(--warning-text);
        }
        .filter-active {
            background: var(--accent-strong);
            color: #ffffff;
            border-color: var(--accent-strong);
        }
        .filter-idle {
            background: var(--panel-muted);
            color: var(--text-muted);
            border-color: var(--border);
        }
        .filter-idle:hover {
            background: #151b23;
            color: var(--text);
        }
        .meta-card {
            border: 1px solid var(--border);
            background: var(--panel-muted);
        }
        .mini-stat {
            border: 1px solid var(--border);
            background: #ffffff;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-size: 12px;
            color: var(--text-muted);
            white-space: nowrap;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
        }
        .mini-stat strong {
            color: #0b1220;
            font-size: 14px;
            margin-left: 0.3rem;
        }
        .compact-summary {
            border: 1px solid var(--border);
            background: var(--panel-muted);
            border-radius: 16px;
            padding: 0.8rem 1rem;
        }
        .compact-summary summary {
            cursor: pointer;
            color: var(--text);
            font-size: 13px;
            font-weight: 700;
            list-style: none;
        }
        .compact-summary summary::-webkit-details-marker { display: none; }
        .compact-summary[open] summary { margin-bottom: 0.85rem; }
        .diff-table { width: 100%; border-collapse: collapse; table-layout: fixed; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; }
        .diff-table th {
            position: sticky;
            top: 0;
            z-index: 5;
            background: var(--diff-header);
            color: var(--diff-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-size: 11px;
            border-bottom: 1px solid var(--border);
        }
        .diff-table td, .diff-table th { border-bottom: 1px solid var(--border); vertical-align: top; }
        .diff-num { width: 56px; color: var(--diff-muted); text-align: right; padding: 0.45rem 0.5rem; user-select: none; }
        .diff-code-cell { padding: 0; }
        .diff-code { margin: 0; padding: 0.45rem 0.75rem; white-space: pre-wrap; word-break: break-word; line-height: 1.5; color: var(--diff-text); background: transparent; }
        .diff-row-context { background: var(--diff-bg); }
        .diff-row-added { background: var(--success-bg); }
        .diff-row-removed { background: var(--danger-bg); }
        .diff-row-empty { background: var(--diff-bg-alt); }
        .diff-separator td { background: var(--diff-header); color: var(--diff-muted); font-size: 11px; padding: 0.4rem 0.75rem; border-bottom: 1px solid var(--border); }
        .diff-split-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 0; min-width: 1200px; }
        .diff-pane { min-width: 0; border-right: 1px solid var(--border); }
        .diff-pane:last-child { border-right: 0; }
        .diff-empty-note { color: var(--diff-muted); }
        .summary-table th {
            background: #f8fafc;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-size: 11px;
            border-bottom: 1px solid var(--border);
        }
        .summary-table td, .summary-table th {
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }
        .summary-scroll {
            overflow-x: auto;
            overflow-y: hidden;
            scrollbar-gutter: stable both-edges;
            scrollbar-color: var(--border-strong) #eef2f7;
            scrollbar-width: auto;
        }
        .summary-scroll::-webkit-scrollbar {
            height: 14px;
        }
        .summary-scroll::-webkit-scrollbar-track {
            background: #eef2f7;
            border-radius: 999px;
        }
        .summary-scroll::-webkit-scrollbar-thumb {
            background: var(--border-strong);
            border-radius: 999px;
            border: 3px solid #eef2f7;
        }
        .modal-backdrop {
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(8px);
        }
        .modal-shell {
            max-height: min(86vh, 980px);
        }
        .modal-code {
            background: #0f1720;
            color: #e5edf5;
            border: 1px solid #233044;
            border-radius: 16px;
            padding: 1rem;
            overflow-x: auto;
            font-size: 12px;
            line-height: 1.55;
        }
        .section-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            padding: 0.25rem 0.65rem;
            font-size: 11px;
            font-weight: 700;
        }
        .alert-chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            border-radius: 999px;
            background: #fff7ed;
            color: #c2410c;
            border: 1px solid #fdba74;
            padding: 0.3rem 0.7rem;
            font-size: 11px;
            font-weight: 700;
        }
        .alert-card {
            border: 1px solid #fed7aa;
            background: linear-gradient(180deg, #fffaf4 0%, #fff7ed 100%);
            border-radius: 18px;
            padding: 1rem 1rem 0.95rem;
        }
        .alert-card-info {
            border-color: #bfdbfe;
            background: linear-gradient(180deg, #f8fbff 0%, #eff6ff 100%);
        }
        .alert-evidence {
            background: #111827;
            color: #e5edf5;
            border-radius: 14px;
            padding: 0.85rem 0.95rem;
            font-size: 12px;
            line-height: 1.55;
            overflow-x: auto;
        }
    </style>
</head>
<body class="min-h-screen">
    <header class="bg-white/90 text-slate-900 border-b border-slate-200 backdrop-blur">
        <div class="max-w-[1600px] mx-auto px-6 py-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
                <div class="flex items-center gap-3">
                    <i data-lucide="files" class="w-6 h-6 text-blue-600"></i>
                    <h1 class="text-xl font-bold">Auditoría de Migración: Yang Params Model</h1>
                </div>
                <p class="text-sm text-slate-600 mt-2">
                    Reporte generado desde los archivos reales de <span class="mono">Yang params model/</span> y <span class="mono">dengue_model/</span>.
                </p>
            </div>
            <div class="text-sm text-slate-600 space-y-1">
                <div>Generado: <span class="text-slate-900 font-medium" id="generated-at"></span></div>
                <div>Regenerar: <span class="mono text-blue-700" id="regen-command"></span></div>
                <div>Elaborado: <span class="font-medium text-slate-900">Econ. Alexis Núñez</span></div>
            </div>
        </div>
        <div class="max-w-[1600px] mx-auto px-6 flex gap-6">
            <button id="tab-resumen" class="tab-active py-3 flex items-center gap-2" onclick="switchTab('resumen')">
                <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
                Modulo 1: Transformacion y estructura
            </button>
            <button id="tab-diff" class="tab-inactive py-3 flex items-center gap-2" onclick="switchTab('diff')">
                <i data-lucide="git-compare-arrows" class="w-4 h-4"></i>
                Modulo 2: Diff archivo por archivo
            </button>
        </div>
    </header>

    <main class="max-w-[1600px] mx-auto px-6 py-6">
        <section id="view-resumen" class="space-y-6">
            <section class="rounded-[28px] bg-gradient-to-br from-white to-slate-100 border border-slate-200 text-slate-900 shadow-xl overflow-hidden">
                <div class="grid grid-cols-1 xl:grid-cols-[1.25fr_0.75fr] gap-0">
                    <article class="p-7 lg:p-8">
                        <div class="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                            <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
                            Lectura ejecutiva de la migracion
                        </div>
                        <h2 class="mt-4 text-2xl lg:text-3xl font-bold leading-tight">La auditoría ahora se centra en comprender la transformación y luego inspeccionarla como revisión de código.</h2>
                        <p class="mt-4 text-sm lg:text-base text-slate-600 leading-7" id="methodology-text"></p>
                        <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div class="rounded-2xl border border-slate-200 bg-white p-4">
                                <div class="font-semibold text-slate-900">Correspondencia verificable</div>
                                <div class="text-slate-600 mt-1">Cada par MATLAB/Python puede abrirse directamente en el inspector para revisar cambios reales.</div>
                            </div>
                            <div class="rounded-2xl border border-slate-200 bg-white p-4">
                                <div class="font-semibold text-slate-900">Infraestructura visible</div>
                                <div class="text-slate-600 mt-1">Los módulos nuevos de Python quedan separados para distinguir soporte del núcleo migrado.</div>
                            </div>
                            <div class="rounded-2xl border border-slate-200 bg-white p-4">
                                <div class="font-semibold text-slate-900">Reporte regenerable</div>
                                <div class="text-slate-600 mt-1">El HTML sigue anclado a los archivos del proyecto y se reconstruye desde el estado actual del disco.</div>
                            </div>
                        </div>
                    </article>
                    <aside class="p-7 lg:p-8 bg-slate-50 border-t xl:border-t-0 xl:border-l border-slate-200">
                        <div class="flex items-center gap-2 text-blue-700">
                            <i data-lucide="scan-search" class="w-5 h-5"></i>
                            <h3 class="font-semibold">Señales rápidas</h3>
                        </div>
                        <ul class="mt-4 space-y-3 text-sm text-slate-700" id="quick-facts"></ul>
                    </aside>
                </div>
            </section>

            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4" id="summary-cards"></div>

            <section class="glass-panel border border-white/70 rounded-[28px] shadow-xl overflow-hidden">
                <div class="px-5 py-4 border-b border-slate-200/80 bg-white/70 flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                        <h2 class="font-bold text-slate-900 text-lg">Tabla de transformacion archivo por archivo</h2>
                        <p class="text-sm text-slate-600">Vista tabular compacta del original MATLAB, su version Python, para que sirve y el cambio principal realizado.</p>
                    </div>
                    <div class="text-xs text-slate-500 mono">Desliza horizontalmente si necesitas ver todas las columnas</div>
                </div>
                <div class="summary-scroll relative">
                    <table class="summary-table min-w-[1240px] w-full text-sm">
                        <thead>
                            <tr>
                                <th class="px-3 py-2.5 text-left">MATLAB</th>
                                <th class="px-3 py-2.5 text-left">Python</th>
                                <th class="px-3 py-2.5 text-left">Estado</th>
                                <th class="px-3 py-2.5 text-left">Categoria</th>
                                <th class="px-3 py-2.5 text-left">Para que sirve</th>
                                <th class="px-3 py-2.5 text-left">Cambio principal</th>
                                <th class="px-3 py-2.5 text-left min-w-[220px] w-[220px]">Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="transformation-table"></tbody>
                    </table>
                </div>
            </section>
        </section>

        <section id="view-diff" class="hidden space-y-4">
            <section class="glass-panel border border-white/70 rounded-[24px] shadow-xl overflow-hidden">
                <div class="px-4 py-4 border-b border-slate-200/80 bg-slate-50/80">
                    <div class="flex flex-col 2xl:flex-row gap-3 2xl:items-center">
                        <div class="shrink-0 flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-[0.18em]">
                            <i data-lucide="search-code" class="w-4 h-4 text-blue-400"></i>
                            Inspector
                        </div>
                        <div class="flex-1 grid grid-cols-1 xl:grid-cols-[220px_minmax(0,1fr)_auto_auto] gap-2">
                            <input id="search-input" type="text" placeholder="Buscar archivo..." class="review-input w-full rounded-xl px-3 py-2.5 text-sm">
                            <select id="entry-select" class="review-input w-full rounded-xl px-3 py-2.5 text-sm"></select>
                            <span id="search-result-count" class="pill-neutral justify-center px-3 py-2">0 archivos</span>
                            <div class="flex items-center gap-2">
                                <button id="prev-entry" type="button" class="nav-button rounded-xl px-3 py-2.5">
                                    <i data-lucide="chevron-left" class="w-4 h-4"></i>
                                </button>
                                <button id="next-entry" type="button" class="nav-button rounded-xl px-3 py-2.5">
                                    <i data-lucide="chevron-right" class="w-4 h-4"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="mt-3 flex flex-col gap-2 xl:flex-row xl:items-center xl:justify-between">
                        <div class="flex flex-wrap gap-2" id="kind-filters"></div>
                        <span id="picker-position" class="text-xs text-slate-500">Archivo 0 de 0</span>
                    </div>
                </div>
            </section>

            <section class="glass-panel border border-white/70 rounded-[24px] shadow-xl overflow-hidden">
                    <div class="px-4 py-4 border-b border-slate-200/80 bg-slate-50/80 space-y-3">
                        <div class="flex flex-col 2xl:flex-row 2xl:items-center 2xl:justify-between gap-3">
                            <div class="min-w-0">
                                <div class="flex items-center gap-2 flex-wrap">
                                    <span id="selected-status" class="pill-badge"></span>
                                    <span id="selected-category" class="pill-neutral"></span>
                                </div>
                                <div class="mt-2 flex flex-col gap-1 xl:flex-row xl:items-center xl:gap-3">
                                    <h2 class="text-lg xl:text-xl font-bold text-slate-900 leading-tight" id="selected-title">Archivo</h2>
                                    <span id="selected-stats" class="flex flex-wrap gap-2"></span>
                                </div>
                                <p class="text-sm text-slate-600 mt-1 leading-6" id="selected-purpose"></p>
                            </div>
                            <div class="flex items-center gap-3">
                                <span id="picker-position-inline" class="hidden xl:inline text-xs text-slate-500"></span>
                                <label class="text-xs text-slate-500 font-medium uppercase tracking-[0.16em]">Vista</label>
                                <select id="diff-view-mode" class="review-input rounded-xl px-3 py-2 text-sm">
                                    <option value="line-by-line">Unificada</option>
                                    <option value="side-by-side">Lado a lado</option>
                                </select>
                            </div>
                        </div>
                        <details class="compact-summary">
                            <summary>Contexto del archivo</summary>
                            <div class="grid grid-cols-1 xl:grid-cols-2 gap-3">
                                <div class="meta-card rounded-xl p-3">
                                    <div class="text-[11px] uppercase tracking-[0.16em] text-slate-500">Origen MATLAB</div>
                                    <div class="mt-2 text-sm font-medium mono text-rose-700" id="selected-matlab-name"></div>
                                    <a id="selected-matlab-link" class="mt-1 inline-flex text-xs text-rose-600 hover:underline" target="_blank" rel="noopener noreferrer"></a>
                                </div>
                                <div class="meta-card rounded-xl p-3">
                                    <div class="text-[11px] uppercase tracking-[0.16em] text-slate-500">Destino Python</div>
                                    <div class="mt-2 text-sm font-medium mono text-emerald-700" id="selected-python-name"></div>
                                    <a id="selected-python-link" class="mt-1 inline-flex text-xs text-emerald-600 hover:underline" target="_blank" rel="noopener noreferrer"></a>
                                </div>
                            </div>
                            <div class="meta-card rounded-xl p-3 mt-3">
                                <div class="text-[11px] uppercase tracking-[0.16em] text-slate-500">Lectura de la conversión</div>
                                <p class="mt-2 text-sm text-slate-700 leading-6" id="selected-transform"></p>
                            </div>
                            <div class="meta-card rounded-xl p-3 mt-3">
                                <div class="text-[11px] uppercase tracking-[0.16em] text-slate-500">Notas clave de revisión</div>
                                <ul class="mt-2 space-y-2 text-sm text-slate-700 list-disc list-inside" id="selected-notes"></ul>
                            </div>
                        </details>
                    </div>
                    <div id="diff-output" class="p-3 md:p-4 overflow-x-auto" style="background: var(--diff-bg);"></div>
            </section>
        </section>
    </main>

    <div id="file-detail-modal" class="hidden fixed inset-0 z-50">
        <div class="modal-backdrop absolute inset-0" onclick="closeDetailModal()"></div>
        <div class="relative z-10 min-h-full flex items-center justify-center p-4 lg:p-8">
            <section class="modal-shell glass-panel w-full max-w-6xl rounded-[28px] overflow-hidden flex flex-col">
                <div class="px-6 py-5 border-b border-slate-200 bg-white flex items-start justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2 flex-wrap">
                            <span id="modal-status" class="pill-badge"></span>
                            <span id="modal-category" class="pill-neutral"></span>
                            <span class="section-badge">
                                <i data-lucide="book-open-text" class="w-3.5 h-3.5"></i>
                                Lectura tecnica del archivo
                            </span>
                        </div>
                        <h2 id="modal-title" class="mt-3 text-2xl font-bold text-slate-900"></h2>
                        <p id="modal-overview" class="mt-2 text-sm text-slate-600 leading-7 max-w-4xl"></p>
                    </div>
                    <button type="button" onclick="closeDetailModal()" class="rounded-xl border border-slate-200 bg-white px-3 py-2 text-slate-600 hover:bg-slate-50">
                        <i data-lucide="x" class="w-4 h-4"></i>
                    </button>
                </div>
                <div class="overflow-y-auto p-6 space-y-6">
                    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
                        <article class="rounded-2xl border border-slate-200 bg-white p-5">
                            <h3 class="font-semibold text-slate-900">Entradas</h3>
                            <ul id="modal-inputs" class="mt-3 space-y-2 text-sm text-slate-700 list-disc list-inside"></ul>
                        </article>
                        <article class="rounded-2xl border border-slate-200 bg-white p-5">
                            <h3 class="font-semibold text-slate-900">Salidas</h3>
                            <ul id="modal-outputs" class="mt-3 space-y-2 text-sm text-slate-700 list-disc list-inside"></ul>
                        </article>
                    </div>
                    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
                        <article class="rounded-2xl border border-slate-200 bg-white p-5">
                            <h3 class="font-semibold text-slate-900">Dependencias principales</h3>
                            <ul id="modal-dependencies" class="mt-3 space-y-2 text-sm text-slate-700 list-disc list-inside"></ul>
                        </article>
                        <article class="rounded-2xl border border-slate-200 bg-white p-5">
                            <h3 class="font-semibold text-slate-900">Como trabaja internamente</h3>
                            <ul id="modal-flow" class="mt-3 space-y-2 text-sm text-slate-700 list-disc list-inside"></ul>
                        </article>
                    </div>
                    <article class="rounded-2xl border border-slate-200 bg-white p-5">
                        <h3 class="font-semibold text-slate-900">Notas de migracion</h3>
                        <ul id="modal-migration-notes" class="mt-3 space-y-2 text-sm text-slate-700 list-disc list-inside"></ul>
                    </article>
                    <article class="rounded-2xl border border-slate-200 bg-white p-5">
                        <div class="flex items-center justify-between gap-3 flex-wrap">
                            <h3 class="font-semibold text-slate-900">Alertas de mantenimiento</h3>
                            <span class="text-xs text-slate-500">Busca parametros, curvas o umbrales pegados en el codigo</span>
                        </div>
                        <div id="modal-alerts" class="mt-4 space-y-3"></div>
                    </article>
                    <article class="rounded-2xl border border-slate-200 bg-white p-5">
                        <h3 class="font-semibold text-slate-900">Que significan los bloques principales del codigo</h3>
                        <p id="modal-code-explanation" class="mt-3 text-sm text-slate-700 leading-7"></p>
                    </article>
                    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
                        <article class="rounded-2xl border border-slate-200 bg-white p-5">
                            <div class="flex items-center justify-between gap-3">
                                <h3 class="font-semibold text-slate-900">Bloque clave en Python</h3>
                                <span class="text-xs text-slate-500 mono" id="modal-python-label"></span>
                            </div>
                            <pre id="modal-python-code" class="modal-code mt-3 mono"></pre>
                        </article>
                        <article class="rounded-2xl border border-slate-200 bg-white p-5">
                            <div class="flex items-center justify-between gap-3">
                                <h3 class="font-semibold text-slate-900">Referencia del archivo original</h3>
                                <span class="text-xs text-slate-500 mono" id="modal-matlab-label"></span>
                            </div>
                            <pre id="modal-matlab-code" class="modal-code mt-3 mono"></pre>
                        </article>
                    </div>
                </div>
            </section>
        </div>
    </div>

    <script id="audit-data" type="application/json">__AUDIT_DATA__</script>
    <script>
        const rawAuditData = document.getElementById("audit-data").textContent;
        const audit = JSON.parse(rawAuditData);
        const summary = audit.summary;
        const allEntries = audit.entries;
        let activeTab = "resumen";
        let currentEntryId = allEntries[0]?.id || null;
        let currentFilter = "all";
        let currentSearch = "";

        function switchTab(tab) {
            activeTab = tab;
            document.getElementById("view-resumen").classList.toggle("hidden", tab !== "resumen");
            document.getElementById("view-diff").classList.toggle("hidden", tab !== "diff");
            document.getElementById("tab-resumen").className = tab === "resumen"
                ? "tab-active py-3 flex items-center gap-2"
                : "tab-inactive py-3 flex items-center gap-2";
            document.getElementById("tab-diff").className = tab === "diff"
                ? "tab-active py-3 flex items-center gap-2"
                : "tab-inactive py-3 flex items-center gap-2";
            if (tab === "diff") {
                renderDiff(currentEntryId);
            }
        }

        function initHeader() {
            document.getElementById("generated-at").textContent = summary.generatedAt;
            document.getElementById("regen-command").textContent = summary.regenerateCommand;
        }

        function renderSummary() {
            const cards = [
                ["Archivos MATLAB", summary.matlabCount, "file-code-2", "text-red-600 bg-red-50"],
                ["Modulos Python", summary.pythonCount, "file-json-2", "text-blue-600 bg-blue-50"],
                ["Pares 1:1", summary.pairedCount, "git-branch-plus", "text-emerald-600 bg-emerald-50"],
                ["Modulos nuevos Python", summary.pythonOnlyCount, "package-plus", "text-amber-600 bg-amber-50"],
                ["Cobertura", summary.coveragePercent + "%", "badge-check", "text-teal-700 bg-teal-50"],
            ];

            document.getElementById("summary-cards").innerHTML = cards.map(([label, value, icon, styles]) => `
                <article class="summary-card glass-panel border border-white/80 rounded-[24px] p-5 shadow-lg">
                    <div class="flex items-start justify-between gap-4">
                        <div>
                            <div class="text-xs uppercase tracking-[0.18em] text-slate-500">${label}</div>
                            <div class="text-3xl font-bold text-slate-900 mt-3">${value}</div>
                            <div class="text-sm text-slate-500 mt-2">Estado actual leido desde los archivos conectados al reporte.</div>
                        </div>
                        <div class="w-12 h-12 rounded-2xl flex items-center justify-center ${styles}">
                            <i data-lucide="${icon}" class="w-6 h-6"></i>
                        </div>
                    </div>
                </article>
            `).join("");

            document.getElementById("methodology-text").textContent = summary.methodology;
            document.getElementById("quick-facts").innerHTML = [
                `El reporte compara ${summary.pairedCount} pares reales MATLAB/Python usando el contenido actual del disco.`,
                `Hay ${summary.pythonOnlyCount} modulos nuevos de soporte en Python que no existian como archivo MATLAB.`,
                `El total agregado por la migracion auditada es de ${summary.totalAddedLines} lineas y el total removido es de ${summary.totalRemovedLines}.`,
                summary.mostChangedStem ? `El archivo con mayor volumen de cambios es ${summary.mostChangedStem}.` : "No se detectaron cambios significativos."
            ].map(text => `
                <li class="rounded-2xl border border-slate-200 bg-white px-4 py-3 leading-6 shadow-sm">
                    ${escapeHtml(text)}
                </li>
            `).join("");
        }

        function kindBadge(kind) {
            if (kind === "paired") return "kind-paired";
            if (kind === "python-only") return "kind-python-only";
            return "kind-matlab-only";
        }

        function renderTransformationTable() {
            const tbody = document.getElementById("transformation-table");
            tbody.innerHTML = allEntries.map(entry => `
                <tr class="hover:bg-slate-50/70">
                    <td class="px-3 py-3">
                        <div class="mono text-sm text-rose-700 font-medium">${escapeHtml(entry.matlabName)}</div>
                        <div class="text-xs text-slate-500 mt-1">${escapeHtml(entry.matlabRelPath || "Sin archivo MATLAB asociado")}</div>
                    </td>
                    <td class="px-3 py-3">
                        <div class="mono text-sm text-emerald-700 font-medium">${escapeHtml(entry.pythonName)}</div>
                        <div class="text-xs text-slate-500 mt-1">${escapeHtml(entry.pythonRelPath || "Sin archivo Python asociado")}</div>
                    </td>
                    <td class="px-3 py-3">
                        <span class="inline-flex px-2.5 py-1 rounded-full border text-[11px] font-semibold whitespace-nowrap ${kindBadge(entry.kind)}">
                            ${escapeHtml(entry.statusLabel)}
                        </span>
                    </td>
                    <td class="px-3 py-3 text-slate-700 min-w-[130px]">${escapeHtml(entry.category)}</td>
                    <td class="px-3 py-3 text-slate-700 leading-6 min-w-[250px] max-w-[320px]">${escapeHtml(entry.purpose)}</td>
                    <td class="px-3 py-3 text-slate-600 leading-6 min-w-[250px] max-w-[320px]">${escapeHtml(entry.transform)}</td>
                    <td class="px-3 py-3 min-w-[220px] w-[220px]">
                        <div class="flex flex-col gap-2">
                            ${entry.detail.alerts.length ? `
                                <div class="alert-chip w-full">
                                    <i data-lucide="triangle-alert" class="w-3.5 h-3.5"></i>
                                    ${entry.detail.alerts.length} alerta${entry.detail.alerts.length === 1 ? "" : "s"}
                                </div>
                            ` : ""}
                            <button class="inline-flex items-center justify-center gap-2 text-sm px-3 py-1.5 rounded-xl bg-blue-600 text-white hover:bg-blue-500 whitespace-nowrap w-full" onclick="openInspector('${entry.id}')">
                                <i data-lucide="arrow-up-right" class="w-4 h-4"></i>
                                Abrir diff
                            </button>
                            <button class="inline-flex items-center justify-center gap-2 text-sm px-3 py-1.5 rounded-xl border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 whitespace-nowrap w-full" onclick="openDetailModal('${entry.id}')">
                                <i data-lucide="book-open-text" class="w-4 h-4"></i>
                                Conocer más
                            </button>
                        </div>
                    </td>
                </tr>
            `).join("");
            lucide.createIcons();
        }

        function renderList(items, elementId) {
            document.getElementById(elementId).innerHTML = items
                .map(item => `<li>${escapeHtml(item)}</li>`)
                .join("");
        }

        function renderAlerts(alerts, elementId) {
            const container = document.getElementById(elementId);
            if (!alerts.length) {
                container.innerHTML = `
                    <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                        No se detectaron parametros pegados, curvas embebidas ni umbrales fijos con las reglas actuales de la auditoria.
                    </div>
                `;
                return;
            }
            container.innerHTML = alerts.map(alert => `
                <article class="alert-card ${alert.level === "info" ? "alert-card-info" : ""}">
                    <div class="flex items-center gap-2">
                        <span class="alert-chip">
                            <i data-lucide="${alert.level === "info" ? "info" : "triangle-alert"}" class="w-3.5 h-3.5"></i>
                            ${alert.level === "info" ? "Revision" : "Alerta"}
                        </span>
                        <h4 class="text-sm font-semibold text-slate-900">${escapeHtml(alert.title)}</h4>
                    </div>
                    <p class="mt-3 text-sm text-slate-700 leading-6">${escapeHtml(alert.message)}</p>
                    ${alert.evidence.length ? `
                        <div class="mt-3">
                            <div class="text-[11px] uppercase tracking-[0.16em] text-slate-500 mb-2">Evidencia encontrada</div>
                            <pre class="alert-evidence mono">${escapeHtml(alert.evidence.join("\\n"))}</pre>
                        </div>
                    ` : ""}
                </article>
            `).join("");
        }

        function openDetailModal(id) {
            const entry = allEntries.find(item => item.id === id);
            if (!entry) return;

            document.getElementById("modal-status").textContent = entry.statusLabel;
            document.getElementById("modal-status").className = `pill-badge ${kindBadge(entry.kind)}`;
            document.getElementById("modal-category").textContent = entry.category;
            document.getElementById("modal-title").textContent = `${entry.matlabName} → ${entry.pythonName}`;
            document.getElementById("modal-overview").textContent = entry.detail.overview;
            renderList(entry.detail.inputs, "modal-inputs");
            renderList(entry.detail.outputs, "modal-outputs");
            renderList(entry.detail.dependencies, "modal-dependencies");
            renderList(entry.detail.flow, "modal-flow");
            renderList(entry.detail.migrationNotes, "modal-migration-notes");
            renderAlerts(entry.detail.alerts || [], "modal-alerts");
            document.getElementById("modal-code-explanation").textContent = entry.detail.codeExplanation;
            document.getElementById("modal-python-label").textContent = entry.pythonRelPath || "Sin archivo Python";
            document.getElementById("modal-matlab-label").textContent = entry.matlabRelPath || "Sin archivo MATLAB";
            document.getElementById("modal-python-code").textContent = entry.detail.pythonSnippet || "Sin snippet Python disponible.";
            document.getElementById("modal-matlab-code").textContent = entry.detail.matlabSnippet || "Sin snippet MATLAB disponible.";
            document.getElementById("file-detail-modal").classList.remove("hidden");
            document.body.classList.add("overflow-hidden");
            lucide.createIcons();
        }

        function closeDetailModal() {
            document.getElementById("file-detail-modal").classList.add("hidden");
            document.body.classList.remove("overflow-hidden");
        }

        function buildFilters() {
            const filters = [
                ["all", "Todos"],
                ["paired", "Migrados 1:1"],
                ["python-only", "Nuevos en Python"],
                ["matlab-only", "Solo MATLAB"],
            ];
            document.getElementById("kind-filters").innerHTML = filters.map(([value, label]) => `
                <button onclick="setFilter('${value}')" class="px-3 py-1.5 rounded-full border text-xs font-semibold ${currentFilter === value ? "filter-active" : "filter-idle"}">
                    ${label}
                </button>
            `).join("");
        }

        function filteredEntries() {
            return allEntries.filter(entry => {
                const matchesKind = currentFilter === "all" ? true : entry.kind === currentFilter;
                const haystack = `${entry.id} ${entry.matlabName} ${entry.pythonName} ${entry.category} ${entry.purpose}`.toLowerCase();
                const matchesSearch = haystack.includes(currentSearch.toLowerCase());
                return matchesKind && matchesSearch;
            });
        }

        function navButtonClass(disabled) {
            return disabled
                ? "nav-button-disabled rounded-xl px-3 py-2.5"
                : "nav-button rounded-xl px-3 py-2.5";
        }

        function renderInspectorPicker() {
            const entries = filteredEntries();
            if (!entries.some(entry => entry.id === currentEntryId) && entries.length) {
                currentEntryId = entries[0].id;
            }

            const entrySelect = document.getElementById("entry-select");
            const resultCount = document.getElementById("search-result-count");
            const pickerPosition = document.getElementById("picker-position");
            const pickerPositionInline = document.getElementById("picker-position-inline");
            const prevButton = document.getElementById("prev-entry");
            const nextButton = document.getElementById("next-entry");

            resultCount.textContent = `${entries.length} archivo${entries.length === 1 ? "" : "s"}`;

            if (!entries.length) {
                currentEntryId = null;
                entrySelect.innerHTML = '<option value="">Sin coincidencias</option>';
                pickerPosition.textContent = "Archivo 0 de 0";
                pickerPositionInline.textContent = "Archivo 0 de 0";
                prevButton.disabled = true;
                nextButton.disabled = true;
                prevButton.className = navButtonClass(true);
                nextButton.className = navButtonClass(true);
                document.getElementById("diff-output").innerHTML = '<div class="p-6 text-sm text-slate-500">Ajusta la búsqueda o el filtro para volver a cargar un diff.</div>';
                return;
            }

            entrySelect.innerHTML = entries.map(entry => `
                <option value="${escapeHtml(entry.id)}">${escapeHtml(entry.pythonName)} · ${escapeHtml(entry.category)} · ${escapeHtml(entry.statusLabel)}</option>
            `).join("");
            entrySelect.value = currentEntryId;

            const currentIndex = Math.max(entries.findIndex(entry => entry.id === currentEntryId), 0);
            pickerPosition.textContent = `Archivo ${currentIndex + 1} de ${entries.length}`;
            pickerPositionInline.textContent = `Archivo ${currentIndex + 1} de ${entries.length}`;

            prevButton.disabled = currentIndex <= 0;
            nextButton.disabled = currentIndex >= entries.length - 1;
            prevButton.className = navButtonClass(prevButton.disabled);
            nextButton.className = navButtonClass(nextButton.disabled);
            lucide.createIcons();
            renderDiff(currentEntryId);
        }

        function setFilter(value) {
            currentFilter = value;
            buildFilters();
            renderInspectorPicker();
        }

        function openInspector(id) {
            currentEntryId = id;
            switchTab("diff");
            buildFilters();
            renderInspectorPicker();
        }

        function selectEntry(id) {
            currentEntryId = id;
            renderInspectorPicker();
        }

        function moveEntry(step) {
            const entries = filteredEntries();
            const index = entries.findIndex(entry => entry.id === currentEntryId);
            if (index === -1) return;
            const nextEntry = entries[index + step];
            if (!nextEntry) return;
            currentEntryId = nextEntry.id;
            renderInspectorPicker();
        }

        function statCard(label, value) {
            return `
                <span class="mini-stat">${label}<strong>${value}</strong></span>
            `;
        }

        function formatCode(code) {
            if (!code) {
                return '<span class="diff-empty-note">(sin contenido)</span>';
            }
            return escapeHtml(code);
        }

        function buildStructuredPatch(entry) {
            const beforeName = entry.matlabRelPath || "Sin archivo MATLAB";
            const afterName = entry.pythonRelPath || "Sin archivo Python";
            return Diff.structuredPatch(
                beforeName,
                afterName,
                entry.matlabCode || "",
                entry.pythonCode || "",
                "Original MATLAB",
                "Estado Python",
                { context: 100000 }
            );
        }

        function buildUnifiedRows(entry) {
            const patch = buildStructuredPatch(entry);
            let oldLine = 1;
            let newLine = 1;
            let rows = "";

            if (!patch.hunks.length) {
                return `<div class="p-6 text-sm text-slate-500">No hay diferencias detectadas entre los archivos seleccionados.</div>`;
            }

            patch.hunks.forEach((hunk) => {
                rows += `<tr class="diff-separator"><td colspan="3">${escapeHtml(hunk.oldStart + "," + hunk.oldLines + " -> " + hunk.newStart + "," + hunk.newLines)}</td></tr>`;
                hunk.lines.forEach((line) => {
                    const marker = line[0];
                    const content = line.slice(1);
                    if (marker === "\\\\") {
                        return;
                    }

                    if (marker === " ") {
                        rows += `
                            <tr class="diff-row-context">
                                <td class="diff-num">${oldLine}</td>
                                <td class="diff-num">${newLine}</td>
                                <td class="diff-code-cell"><pre class="diff-code">${formatCode(content)}</pre></td>
                            </tr>
                        `;
                        oldLine += 1;
                        newLine += 1;
                    } else if (marker === "-") {
                        rows += `
                            <tr class="diff-row-removed">
                                <td class="diff-num">${oldLine}</td>
                                <td class="diff-num"></td>
                                <td class="diff-code-cell"><pre class="diff-code">${formatCode(content)}</pre></td>
                            </tr>
                        `;
                        oldLine += 1;
                    } else if (marker === "+") {
                        rows += `
                            <tr class="diff-row-added">
                                <td class="diff-num"></td>
                                <td class="diff-num">${newLine}</td>
                                <td class="diff-code-cell"><pre class="diff-code">${formatCode(content)}</pre></td>
                            </tr>
                        `;
                        newLine += 1;
                    }
                });
            });

            return `
                <table class="diff-table">
                    <thead>
                        <tr>
                            <th class="diff-num">MATLAB</th>
                            <th class="diff-num">Python</th>
                            <th class="text-left px-3 py-2">Codigo</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            `;
        }

        function renderSideBySideHunk(hunk, state) {
            let rows = "";
            let index = 0;
            while (index < hunk.lines.length) {
                const line = hunk.lines[index];
                const marker = line[0];
                if (marker === "\\\\") {
                    index += 1;
                    continue;
                }

                if (marker === " ") {
                    const content = line.slice(1);
                    rows += `
                        <tr>
                            <td class="diff-num">${state.oldLine}</td>
                            <td class="diff-code-cell diff-row-context"><pre class="diff-code">${formatCode(content)}</pre></td>
                            <td class="diff-num">${state.newLine}</td>
                            <td class="diff-code-cell diff-row-context"><pre class="diff-code">${formatCode(content)}</pre></td>
                        </tr>
                    `;
                    state.oldLine += 1;
                    state.newLine += 1;
                    index += 1;
                    continue;
                }

                if (marker === "-") {
                    const removed = [];
                    while (index < hunk.lines.length && hunk.lines[index][0] === "-") {
                        removed.push(hunk.lines[index].slice(1));
                        index += 1;
                    }
                    const added = [];
                    while (index < hunk.lines.length && hunk.lines[index][0] === "+") {
                        added.push(hunk.lines[index].slice(1));
                        index += 1;
                    }
                    const total = Math.max(removed.length, added.length);
                    for (let offset = 0; offset < total; offset += 1) {
                        const left = removed[offset];
                        const right = added[offset];
                        const leftNumber = left !== undefined ? state.oldLine++ : "";
                        const rightNumber = right !== undefined ? state.newLine++ : "";
                        rows += `
                            <tr>
                                <td class="diff-num">${leftNumber}</td>
                                <td class="diff-code-cell ${left !== undefined ? "diff-row-removed" : "diff-row-empty"}"><pre class="diff-code">${formatCode(left || "")}</pre></td>
                                <td class="diff-num">${rightNumber}</td>
                                <td class="diff-code-cell ${right !== undefined ? "diff-row-added" : "diff-row-empty"}"><pre class="diff-code">${formatCode(right || "")}</pre></td>
                            </tr>
                        `;
                    }
                    continue;
                }

                if (marker === "+") {
                    const added = [];
                    while (index < hunk.lines.length && hunk.lines[index][0] === "+") {
                        added.push(hunk.lines[index].slice(1));
                        index += 1;
                    }
                    added.forEach((content) => {
                        rows += `
                            <tr>
                                <td class="diff-num"></td>
                                <td class="diff-code-cell diff-row-empty"><pre class="diff-code">${formatCode("")}</pre></td>
                                <td class="diff-num">${state.newLine++}</td>
                                <td class="diff-code-cell diff-row-added"><pre class="diff-code">${formatCode(content)}</pre></td>
                            </tr>
                        `;
                    });
                }
            }

            return rows;
        }

        function buildSideBySideRows(entry) {
            const patch = buildStructuredPatch(entry);
            if (!patch.hunks.length) {
                return `<div class="p-6 text-sm text-slate-500">No hay diferencias detectadas entre los archivos seleccionados.</div>`;
            }

            const state = { oldLine: 1, newLine: 1 };
            let rows = "";
            patch.hunks.forEach((hunk) => {
                rows += `<tr class="diff-separator"><td colspan="4">${escapeHtml(hunk.oldStart + "," + hunk.oldLines + " -> " + hunk.newStart + "," + hunk.newLines)}</td></tr>`;
                rows += renderSideBySideHunk(hunk, state);
            });

            return `
                <div class="diff-split-grid">
                    <div class="diff-pane">
                        <table class="diff-table">
                            <thead>
                                <tr>
                                    <th class="diff-num">MATLAB</th>
                                    <th class="text-left px-3 py-2">${escapeHtml(entry.matlabName)}</th>
                                </tr>
                            </thead>
                        </table>
                    </div>
                    <div class="diff-pane">
                        <table class="diff-table">
                            <thead>
                                <tr>
                                    <th class="diff-num">Python</th>
                                    <th class="text-left px-3 py-2">${escapeHtml(entry.pythonName)}</th>
                                </tr>
                            </thead>
                        </table>
                    </div>
                </div>
                <table class="diff-table">
                    <colgroup>
                        <col style="width: 56px">
                        <col style="width: calc(50% - 56px)">
                        <col style="width: 56px">
                        <col style="width: calc(50% - 56px)">
                    </colgroup>
                    <tbody>${rows}</tbody>
                </table>
            `;
        }

        function renderDiff(id) {
            const entry = allEntries.find(item => item.id === id);
            if (!entry) return;

            document.getElementById("selected-status").textContent = entry.statusLabel;
            document.getElementById("selected-status").className = `pill-badge ${kindBadge(entry.kind)}`;
            document.getElementById("selected-category").textContent = entry.category;
            document.getElementById("selected-title").textContent = `${entry.matlabName} → ${entry.pythonName}`;
            document.getElementById("selected-purpose").textContent = entry.purpose;
            document.getElementById("selected-transform").textContent = entry.transform;
            document.getElementById("selected-notes").innerHTML = (entry.notes.length ? entry.notes : ["Sin notas adicionales para este archivo."]).map(note => `<li>${escapeHtml(note)}</li>`).join("");
            document.getElementById("selected-matlab-name").textContent = entry.matlabName;
            document.getElementById("selected-python-name").textContent = entry.pythonName;

            const matlabLink = document.getElementById("selected-matlab-link");
            if (entry.matlabRelPath) {
                matlabLink.textContent = entry.matlabRelPath;
                matlabLink.href = encodeURI(entry.matlabRelPath);
                matlabLink.classList.remove("hidden");
            } else {
                matlabLink.textContent = "Sin archivo MATLAB asociado";
                matlabLink.removeAttribute("href");
            }

            const pythonLink = document.getElementById("selected-python-link");
            if (entry.pythonRelPath) {
                pythonLink.textContent = entry.pythonRelPath;
                pythonLink.href = encodeURI(entry.pythonRelPath);
                pythonLink.classList.remove("hidden");
            } else {
                pythonLink.textContent = "Sin archivo Python asociado";
                pythonLink.removeAttribute("href");
            }

            document.getElementById("selected-stats").innerHTML = [
                statCard("Lineas MATLAB", entry.matlabLines),
                statCard("Lineas Python", entry.pythonLines),
                statCard("Lineas agregadas", entry.addedLines),
                statCard("Lineas removidas", entry.removedLines),
            ].join("");
            const format = document.getElementById("diff-view-mode").value;
            document.getElementById("diff-output").innerHTML =
                format === "side-by-side" ? buildSideBySideRows(entry) : buildUnifiedRows(entry);
        }

        function escapeHtml(value) {
            return String(value)
                .replaceAll("&", "&amp;")
                .replaceAll("<", "&lt;")
                .replaceAll(">", "&gt;");
        }

        function init() {
            initHeader();
            renderSummary();
            renderTransformationTable();
            buildFilters();
            renderInspectorPicker();
            document.getElementById("search-input").addEventListener("input", (event) => {
                currentSearch = event.target.value;
                renderInspectorPicker();
            });
            document.getElementById("entry-select").addEventListener("change", (event) => {
                currentEntryId = event.target.value;
                renderInspectorPicker();
            });
            document.getElementById("prev-entry").addEventListener("click", () => moveEntry(-1));
            document.getElementById("next-entry").addEventListener("click", () => moveEntry(1));
            document.getElementById("diff-view-mode").addEventListener("change", () => renderDiff(currentEntryId));
            window.addEventListener("keydown", (event) => {
                if (event.key === "Escape") {
                    closeDetailModal();
                }
            });
            lucide.createIcons();
        }

        window.onload = init;
    </script>
</body>
</html>
"""


def render_html(payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return HTML_TEMPLATE.replace("__AUDIT_DATA__", data)


def main() -> None:
    entries = build_entries()
    summary = build_summary(entries)
    payload = serialize(entries, summary)
    html = render_html(payload)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Reporte generado en: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
