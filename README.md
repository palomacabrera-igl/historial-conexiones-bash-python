# Historial de conexiones (Bash + Python)

Dos scripts que procesan el historial de sesiones de un sistema Linux a partir del comando `last`:

- **`ej1_historial_usuarios_conectados.sh` (Bash):** filtra las sesiones finalizadas y las muestra en una tabla de columnas fijas. Puede filtrar por usuario y calcular el tiempo total de conexión.
- **`ej2_historial_usuarios_conectados_exp.py` (Python):** invoca al script de Bash, captura su salida y le agrega ordenamiento por columna (ascendente o descendente), un conteo final de filas y ayuda. Propaga los mensajes y códigos de error del script de Bash.

Proyecto académico **individual** de la unidad curricular *Administración de Infraestructuras* (Tecnólogo en Informática, UTEC), 2025.

## Tecnologías

- Bash (`case`, expansión de parámetros, aritmética, `grep -E`, `awk`, `printf`)
- Python 3 (solo biblioteca estándar: `subprocess`, `sys`)
- Comando `last` de Linux (fuente única de datos)

## Requisitos

- Linux (o WSL) con `bash`, `python3` y `last` disponibles.
- Los dos scripts tienen que estar en la misma carpeta: el de Python ejecuta `./ej1_historial_usuarios_conectados.sh`.

## Uso

```bash
chmod +x ej1_historial_usuarios_conectados.sh ej2_historial_usuarios_conectados_exp.py
```

### Ejercicio 1: Bash

```text
./ej1_historial_usuarios_conectados.sh [-r] [-u USUARIO]
```

| Opción | Descripción |
|---|---|
| `-u USUARIO` | Muestra solo las conexiones de ese usuario. |
| `-r` | Al final, imprime el tiempo total acumulado (puede superar las 24 horas). |

Si se usan ambas opciones, van en este orden: `-r -u USUARIO`.

Solo se listan las sesiones cuya duración tiene el formato exacto `(hh:mm)`. Se descartan las sesiones abiertas (`still logged in`) y las duraciones de más de un día (`1+22:54`). Las filas respetan el orden original de `last`.

Ejemplo de salida (datos ficticios):

```text
$ ./ej1_historial_usuarios_conectados.sh -r -u alumno
Usuario  Term   Host            Fecha        H.Con H.Des T.Con
alumno   pts/0  192.168.1.10    Mon Sep 8    14:24 14:25 (00:01)
alumno   pts/1  -               Mon Sep 8    13:46 14:24 (00:38)
alumno   tty1   -               Fri Sep 5    09:10 11:02 (01:52)
El tiempo total de conexión es: 2 horas y 31 minutos
```

### Ejercicio 2: Python

```text
./ej2_historial_usuarios_conectados_exp.py [-r] [-u USUARIO] [-o {u,t,h,d | -u,-t,-h,-d}] [-h]
```

| Opción | Descripción |
|---|---|
| `-h` | Muestra la ayuda y termina, sin ejecutar el script de Bash. |
| `-r` / `-u USUARIO` | Se reenvían al script de Bash. |
| `-o CLAVE` | Ordena las filas por `u` = usuario, `t` = terminal, `h` = host, `d` = duración. Con un `-` delante (`-o -d`), el orden es descendente. |

Las opciones se aceptan en cualquier orden. Para ordenar por duración, cada `(hh:mm)` se convierte a minutos, así el orden es numérico y no alfabético. Al final se agrega una línea con la cantidad de conexiones listadas (general o por usuario).

```bash
./ej2_historial_usuarios_conectados_exp.py -r -u alumno -o -d   # usuario, total y orden por duración descendente
./ej2_historial_usuarios_conectados_exp.py -o u                 # todas las conexiones ordenadas por usuario
```

## Códigos de salida

| Caso | Script | Código |
|---|---|---|
| Ejecución correcta (incluye "no hay conexiones válidas") | ambos | 0 |
| `-u` sin nombre de usuario | Bash | 2 |
| Cantidad de parámetros inválida | Bash | 3 |
| Modificador inválido u orden incorrecto de `-r -u` | Bash | 4 |
| El usuario no existe en el sistema | Bash (y Python lo propaga) | 5 |
| Error de argumentos propio (`-o x`, parámetro desconocido, falta un valor) | Python | 25 |

Los mensajes de error se escriben en `stderr`. El script de Python reenvía el mismo mensaje y el mismo código que recibe del script de Bash.

## Estructura y diseño

```text
ej1_historial_usuarios_conectados.sh
  usuario_existe()            valida el usuario con `id`
  tiempo_a_minutos()          convierte (hh:mm) a minutos (usa 10# para evitar errores con 08 y 09)
  minutos_a_formato_largo()   convierte minutos a "X horas y Y minutos"
  case $#                     valida la cantidad y el orden de los parámetros
  last | grep -E '\([0-9]{2}:[0-9]{2}\)$'   se queda solo con las sesiones finalizadas
  awk + printf                tabla de 7 columnas; si falta el host, muestra "-"

ej2_historial_usuarios_conectados_exp.py
  interpretar_argumentos()    parser propio, acepta cualquier orden y sale con código 25 ante errores
  construir_comando()         arma la llamada al script de Bash, solo con -r y/o -u
  clave_ordenamiento()        devuelve la clave de orden de cada fila (duración en minutos)
  main()                      ejecuta el script de Bash con subprocess, separa encabezado,
                              filas y total, ordena, imprime y cuenta
```

Decisiones principales:

- **Bash obtiene los datos y Python los procesa.** Python no vuelve a leer `last`: reutiliza el script de Bash, así el filtrado y el formato están en un solo lugar.
- **Un código de salida distinto para cada tipo de error.** Eso permite usar los scripts desde otros procesos automatizados.
