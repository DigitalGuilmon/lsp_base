Aquí tienes la documentación limpia, con los caracteres de control de terminal eliminados y el formato corregido para su lectura técnica:

---

# Documentación Técnica: Verificación Formal con JBMC 6.8.0

Esta documentación técnica detalla el procedimiento exacto para realizar la verificación formal de seguridad en el código bancario utilizando **JBMC 6.8.0**, basándose en las opciones disponibles en el sistema.

## 1. Comando de Ejecución Realizado

Para generar el reporte de vulnerabilidad en formato legible por máquinas, se utilizó la siguiente sintaxis en Bash:

```bash
jbmc ProcesadorPagosBancarios \
     --classpath . \
     --function ProcesadorPagosBancarios.verificarIntegridadSaldos \
     --unwind 6 \
     --json-ui
```

### Desglose de Parámetros Utilizados:
* **`ProcesadorPagosBancarios`**: El nombre de la clase compilada (`.class`). Es el argumento principal.
* **`--classpath .`**: Define la ruta de búsqueda de archivos. El punto `.` indica que la clase está en el directorio actual.
* **`--function [nombre]`**: Define el Punto de Entrada. A diferencia de un programa normal que inicia en `main`, JBMC permite elegir cualquier método para analizarlo como si fuera la raíz.
* **`--unwind 6`**: Opción de **BMC (Bounded Model Checking)**. Obliga a JBMC a expandir los ciclos `for` e `if` hasta 6 niveles de profundidad. Esto permitió analizar las 5 transacciones del lote bancario.
* **`--json-ui`**: Cambia la interfaz de salida de texto plano a JSON. Fundamental para la integración con herramientas de seguridad automatizadas.

---

## 2. Posibilidades de Análisis (Según Documentación)

Basado en el comando `jbmc --help`, existen tres categorías principales de ejecución según el objetivo:

### A. Diagnóstico de Propiedades (`--show-properties`)
Antes de correr el análisis pesado, se usa para listar qué es lo que JBMC va a intentar "romper".
* **Uso:** `jbmc Clase --show-properties`
* **Resultado:** Muestra todos los `assert`, revisiones de punteros nulos y límites de arreglos que JBMC ha identificado.

### B. Análisis de Fallos Detallado (`--trace`)
Si prefieres una lectura humana en lugar de JSON, esta es la opción estándar.
* **Uso:** `jbmc Clase --function Metodo --trace`
* **Resultado:** Si la verificación falla, muestra paso a paso los valores de las variables en la consola hasta llegar al error.

### C. Control de Complejidad (`--unwind` y `--depth`)
Indispensable para manejar programas complejos con bucles o recursividad.
* **`--unwind N`**: Límite para ciclos.
* **`--depth N`**: Límite total de pasos de ejecución simbólica. Previene que el verificador consuma toda la RAM en grafos de ejecución infinitos.

---

## 3. Matriz de Formatos de Salida (UI Options)

JBMC ofrece tres formas de reportar resultados, seleccionables al final del comando:

| Opción | Formato | Caso de Uso Ideal |
| :--- | :--- | :--- |
| (Ninguna) | Texto Plano | Revisión rápida por el desarrollador. |
| `--json-ui` | JSON | Integración con CI/CD, Dashboards y Scripts de Python. |
| `--xml-ui` | XML | Sistemas legados o herramientas de reporte basadas en XML. |

---

## 4. Opciones de Seguridad Avanzadas (Bytecode Frontend)

En el menú de ayuda se listan opciones críticas para entornos bancarios que son altamente recomendadas:
* **`--java-assume-inputs-non-null`**: Asume que los parámetros de entrada nunca son nulos. Evita falsos positivos si el framework ya valida nulos.
* **`--throw-assertion-error`**: En lugar de que JBMC marque un "FAILURE" directo, hace que el programa lance una excepción real de Java.
* **`--max-nondet-array-length N`**: Limita el tamaño de los arreglos generados aleatoriamente por JBMC para probar el código (por defecto es 5).

---

## 5. Resumen del Flujo de Trabajo

1.  **Compilación**: Se genera el bytecode con `javac`.
2.  **Configuración**: Se elige el método crítico (ej. el cálculo de saldos).
3.  **Ejecución**: Se corre JBMC con el límite de ciclos (`--unwind`) adecuado.
4.  **Captura**: Se redirige el JSON a un archivo: `jbmc ... --json-ui > reporte.json`.

Esta metodología asegura que ningún desbordamiento aritmético pase a producción, cumpliendo con los estándares de auditoría informática más estrictos (como los requeridos por la CNBV en México).