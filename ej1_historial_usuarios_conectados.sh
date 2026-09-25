#!/bin/bash
# Script: ej1_historial_usuarios_conectados.sh
# Descripción: Procesa la salida de 'last' para mostrar historial de conexiones

# --- 1. Funciones Auxiliares ---
usuario_existe() {
	id "$1" &>/dev/null
	return $?
}

tiempo_a_minutos() {
	local tiempo=$1
	if [[ "$tiempo" == "crash" ]]; then
		echo 0
	else
		local limpio=${tiempo//[()]/}
		local horas=${limpio%%:*}
		local minutos=${limpio##*:}
		echo $((10#$horas * 60 + 10#$minutos))
	fi
}

minutos_a_formato_largo() {
	local total_minutos=$1
	local horas=$((total_minutos / 60))
	local minutos=$((total_minutos % 60))
	echo "$horas horas y $minutos minutos"
}

# --- 2. Manejo de Parámetros ---
FILTRAR_USUARIO=""
CALCULAR_TOTAL=0

case $# in
	0) ;;	# Sin parámetros
	1)
		if [[ "$1" == "-r" ]]; then
			CALCULAR_TOTAL=1
		elif [[ "$1" == "-u" ]]; then
			echo "No se ha especificado el usuario para el modificador -u." >&2
			exit 2
		else
			echo "Modificador inválido: $1" >&2
			exit 4
		fi
		;;
	2)
		if [[ "$1" == "-u" ]]; then
			FILTRAR_USUARIO="$2"
		else
			echo "Modificador inválido: $1" >&2
			exit 4
		fi
		;;
	3)
		if [[ "$1" == "-r" && "$2" == "-u" ]]; then
			CALCULAR_TOTAL=1
			FILTRAR_USUARIO="$3"
		else
			echo "Orden inválido. Use: -r -u USUARIO" >&2
			exit 4
		fi
		;;
	*)
		echo "Cantidad de parámetros inválida" >&2
		exit 3
		;;
esac

# --- 3. Validación de Usuario ---
if [[ -n "$FILTRAR_USUARIO" ]]; then
	if ! usuario_existe "$FILTRAR_USUARIO"; then
		echo "No existe el usuario $FILTRAR_USUARIO en el sistema." >&2
		exit 5
	fi
fi

# --- 4. Obtención y Filtrado de Datos ---
DATOS_LAST=$(last | grep -E '\([0-9]{2}:[0-9]{2}\)$')

if [[ -n "$FILTRAR_USUARIO" ]]; then
	DATOS_LAST=$(echo "$DATOS_LAST" | grep -w "^$FILTRAR_USUARIO")
fi

if [[ -z "$DATOS_LAST" ]]; then
	if [[ -n "$FILTRAR_USUARIO" ]]; then
		echo "No hay conexiones válidas para el usuario $FILTRAR_USUARIO."
	else
		echo "No hay conexiones válidas."
	fi
	exit 0
fi

# --- 5. Salida de tabla ---
printf "%-8s %-6s %-15s %-12s %-5s %-5s %s\n" "Usuario" "Term" "Host" "Fecha" "H.Con" "H.Des" "T.Con"

echo "$DATOS_LAST" | awk '
{
	usr=$1; term=$2; tcon=$(NF);
	
	if (NF >= 10) { 
		host=$3; 
		fecha=$4" "$5" "$6; 
		hcon=$(NF-3); 
		hdes=$(NF-1);
	} else { 
		host="-";   # <--- cambio aquí
		fecha=$3" "$4" "$5; 
		hcon=$(NF-3); 
		hdes=$(NF-1);
	}
	printf "%-8s %-6s %-15s %-12s %-5s %-5s %s\n", usr, term, host, fecha, hcon, hdes, tcon
}'

# --- 6. Cálculo del tiempo total (si -r) ---
if [[ $CALCULAR_TOTAL -eq 1 ]]; then
	minutos_totales=0
	while IFS= read -r t; do
		minutos_totales=$((minutos_totales + $(tiempo_a_minutos "$t")))
	done < <(echo "$DATOS_LAST" | awk '{print $NF}')
	
	echo "El tiempo total de conexión es: $(minutos_a_formato_largo "$minutos_totales")"
fi

exit 0
