#!/usr/bin/env python3
# ej2_historial_usuarios_conectados_exp.py
# Script en Python que llama al Ejercicio 1 (Bash) y agrega orden y conteo

import sys
import subprocess

def mostrar_ayuda():
    print("Uso: ej2_historial_usuarios_conectados_exp.py [-r] [-u USUARIO] "
          "[-o {u,t,h,d | -u,-t,-h,-d}] [-h]")
    print("  -h                 Muestra esta ayuda y termina")
    print("  -r                 Reenvía a Ej.1 para mostrar total")
    print("  -u USUARIO         Reenvía a Ej.1 para filtrar por usuario")
    print("  -o CLAVE           Ordena filas por: u=Usuario, t=Term, h=Host, d=Duración")
    print("                     Con signo menos para descendente (ej.: -d)")

def interpretar_argumentos(argumentos):
    """ Devuelve un diccionario con las opciones que se usaron """
    opciones = {"ayuda": False, "mostrar_total": False, "usuario": None, "orden": None, "descendente": False}
    i = 0
    while i < len(argumentos):
        arg = argumentos[i]
        if arg == "-h":
            opciones["ayuda"] = True
            return opciones
        elif arg == "-r":
            opciones["mostrar_total"] = True
            i += 1
        elif arg == "-u":
            if i + 1 >= len(argumentos):
                sys.stderr.write("Falta el nombre del usuario para -u\n")
                sys.exit(25)
            opciones["usuario"] = argumentos[i+1]
            i += 2
        elif arg == "-o":
            if i + 1 >= len(argumentos):
                sys.stderr.write("Falta la clave para -o\n")
                sys.exit(25)
            clave = argumentos[i+1]
            if clave.startswith("-"):
                opciones["descendente"] = True
                clave = clave[1:]
            if clave not in ["u","t","h","d"]:
                sys.stderr.write("Clave de orden inválida\n")
                sys.exit(25)
            opciones["orden"] = clave
            i += 2
        else:
            sys.stderr.write("Parámetro desconocido: " + arg + "\n")
            sys.exit(25)
    return opciones

def construir_comando(opciones):
    comando = ["./ej1_historial_usuarios_conectados.sh"]
    if opciones["mostrar_total"]:
        comando.append("-r")
    if opciones["usuario"] is not None:
        comando.extend(["-u", opciones["usuario"]])
    return comando

def clave_ordenamiento(fila, clave):
    partes = fila.split()
    if len(partes) < 9:
        return fila
    usuario = partes[0]
    terminal = partes[1]
    host = partes[2]
    duracion = partes[-1]  # último campo (hh:mm)

    if clave == "u":
        return usuario
    if clave == "t":
        return terminal
    if clave == "h":
        return host
    if clave == "d":
        tiempo = duracion.strip("()")
        hh, mm = tiempo.split(":")
        return int(hh) * 60 + int(mm)
    return fila

def main():
    # 1) Leer y validar argumentos
    opciones = interpretar_argumentos(sys.argv[1:])
    if opciones["ayuda"]:
        mostrar_ayuda()
        sys.exit(0)

    # 2) Construir e invocar Ejercicio 1 (Bash)
    comando = construir_comando(opciones)
    proceso = subprocess.run(comando, text=True, capture_output=True)

    # 3) Propagar errores de Ej.1 (mismo stderr y exit code)
    if proceso.returncode != 0:
        if proceso.stderr:
            sys.stderr.write(proceso.stderr)
        sys.exit(proceso.returncode)

    # 4) Normalizar salida: quitar líneas vacías
    lineas = [l for l in proceso.stdout.splitlines() if l.strip() != ""]
    if not lineas:
        # No hubo nada útil que mostrar
        sys.exit(0)

    # 5) Separar encabezado, filas y (si existe) línea de total
    encabezado = lineas[0]
    filas = []
    linea_total = None
    for l in lineas[1:]:
        if l.startswith("El tiempo total de conexión es:"):
            linea_total = l
        else:
            filas.append(l)

    # 6) Si no hay filas válidas, imprimir lo que vino de Ej.1 tal cual
    if not filas:
        print(proceso.stdout)
        sys.exit(0)

    # 7) Ordenar si corresponde (-o u/t/h/d), manteniendo formato de Ej.1
    if opciones["orden"] is not None:
        filas = sorted(
            filas,
            key=lambda f: clave_ordenamiento(f, opciones["orden"]),
            reverse=opciones["descendente"]
        )

    # 8) Imprimir tabla final (encabezado + filas) y total si vino de Ej.1
    print(encabezado)
    for f in filas:
        print(f)
    if linea_total:
        print(linea_total)

    # 9) Agregar conteo final (global o por usuario)
    cantidad = len(filas)
    if opciones["usuario"] is None:
        print(f"Cantidad de conexiones listadas: {cantidad}")
    else:
        print(f"Cantidad de conexiones listadas para el usuario {opciones['usuario']}: {cantidad}")

if __name__ == "__main__":
    main()
