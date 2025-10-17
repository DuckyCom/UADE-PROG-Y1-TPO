import csv
import os
import time
import datetime
import json
from colorama import init, Fore, Style

# --- INICIALIZACIÓN Y CONSTANTES GLOBALES ---
init(autoreset=True)

LOCACIONES_FILE = 'locaciones.csv'
EVENTOS_FILE = 'eventos.csv'
VENTAS_FILE = 'ventas.csv'
COMPRADORES_FILE = 'compradores.csv'

LOCACIONES_HEADERS = ['id', 'nombre', 'precios', 'capacidades', 'tipos_entrada']
EVENTOS_HEADERS = ['id', 'nombre', 'fecha', 'id_locacion', 'entradas_restantes']
# Añadimos 'estado' a las ventas para mantener el historial (activa/reembolsada)
VENTAS_HEADERS = ['id_venta', 'id_evento', 'id_comprador', 'cantidad', 'tipo_entrada_idx', 'estado']
COMPRADORES_HEADERS = ['id', 'nombre', 'dni']

# --- FUNCIONES AUXILIARES Y DE MANEJO DE DATOS ---
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def cargar_datos(nombre_archivo, headers):
    try:
        with open(nombre_archivo, 'r', newline='', encoding='utf-8') as archivo_csv:
            lector = csv.DictReader(archivo_csv)
            datos = []
            for fila in lector:
                fila_procesada = {}
                for clave, valor in fila.items():
                    # Campos que se guardan como listas en la CSV -> intentamos JSON para preservar tipos
                    if clave in ['precios', 'capacidades', 'tipos_entrada', 'entradas_restantes']:
                        if valor and valor not in ['', '[]']:
                            lista = None
                            # Intenta JSON primero
                            try:
                                parsed = json.loads(valor)
                                if isinstance(parsed, list):
                                    lista = parsed
                            except Exception:
                                lista = None

                            if lista is None:
                                # Intentar formato separado por ; o por , (más legible en CSV)
                                txt = valor.strip()
                                sep = None
                                if ';' in txt:
                                    sep = ';'
                                elif ',' in txt:
                                    sep = ','
                                if sep:
                                    lista = [x.strip().strip('"').strip("'") for x in txt.strip('[]').split(sep) if x.strip()]
                                else:
                                    # Un solo elemento
                                    cleaned = txt.strip('[]').strip('"').strip("'")
                                    lista = [cleaned] if cleaned else []

                            # Cast por tipo de campo
                            if clave == 'precios':
                                fila_procesada[clave] = [float(x) for x in lista]
                            elif clave in ['capacidades', 'entradas_restantes']:
                                fila_procesada[clave] = [int(x) for x in lista]
                            else:
                                fila_procesada[clave] = [str(x) for x in lista]
                        else:
                            fila_procesada[clave] = []
                    # Campos numéricos (IDs y cantidades)
                    elif clave.startswith('id') or clave in ['cantidad', 'tipo_entrada_idx']:
                        try:
                            fila_procesada[clave] = int(valor) if valor not in [None, ''] else None
                        except Exception:
                            fila_procesada[clave] = None
                    else:
                        # Texto plano (nombre, fecha, estado, dni...)
                        fila_procesada[clave] = valor
                datos.append(fila_procesada)
            return datos
    except FileNotFoundError:
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo_csv:
            escritor = csv.writer(archivo_csv)
            escritor.writerow(headers)
        return []
    except Exception as e:
        print(f"{Fore.RED}Error al cargar {nombre_archivo}: {e}")
        return []

def guardar_datos(nombre_archivo, datos, headers):
    try:
        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo_csv:
            escritor = csv.DictWriter(archivo_csv, fieldnames=headers)
            escritor.writeheader()
            # Asegurarnos de serializar listas en el mismo formato que cargar_datos espera
            filas_a_escribir = []
            for d in datos:
                fila = {}
                for h in headers:
                    valor = d.get(h, '')
                    if isinstance(valor, list):
                        # Serializamos listas usando JSON para preservar tipos (números y strings)
                        try:
                            fila[h] = json.dumps(valor, ensure_ascii=False)
                        except Exception:
                            fila[h] = str(valor)
                    else:
                        fila[h] = valor
                filas_a_escribir.append(fila)
            escritor.writerows(filas_a_escribir)
    except Exception as e:
        print(f"{Fore.RED}Error al guardar {nombre_archivo}: {e}")

def buscar_por_clave_recursivo(datos, valor_buscado, clave, indice=0):
    if indice >= len(datos):
        return None
    if str(datos[indice][clave]) == str(valor_buscado):
        return datos[indice]
    return buscar_por_clave_recursivo(datos, valor_buscado, clave, indice + 1)


# --- MÓDULO DE GESTIÓN DE COMPRADORES --- (NUEVO)
def gestionar_compradores(compradores, ventas, eventos, locaciones):
    """
    Menú para listar y eliminar compradores existentes.
    La creación se maneja durante el proceso de venta.
    """
    while True:
        limpiar_pantalla()
        print(Fore.CYAN + "--- GESTIÓN DE COMPRADORES ---")
        print("1. Listar Compradores y sus Compras")
        print("2. Eliminar un Comprador")
        print("0. Volver al Menú Principal")
        opcion = input(Fore.YELLOW + "Seleccione una opción: ")

        if opcion == '1':
            listar_compradores_y_compras(compradores, ventas, eventos, locaciones)
        elif opcion == '2':
            eliminar_comprador(compradores, ventas)
        elif opcion == '0':
            break
        else:
            print(Fore.RED + "Opción no válida.")
            time.sleep(1)
            
    while True:
        limpiar_pantalla()
        print(Fore.CYAN + "--- GESTIÓN DE COMPRADORES ---")
        print("1. Registrar Nuevo Comprador")
        print("2. Listar Todos los Compradores")
        print("0. Volver al Menú Principal")
        opcion = input(Fore.YELLOW + "Seleccione una opción: ")

        if opcion == '1':
            registrar_comprador(compradores)
            input("\nPresione Enter para continuar...")
        elif opcion == '2':
            listar_compradores(compradores)
            input("\nPresione Enter para continuar...")
        elif opcion == '0':
            break
        else:
            print(Fore.RED + "Opción no válida.")
            time.sleep(1)
            
def listar_compradores_y_compras(compradores, ventas, eventos, locaciones):
    """
    Muestra cada comprador y un detalle de todas las entradas que ha adquirido.
    """
    limpiar_pantalla()
    print(Fore.CYAN + "--- LISTA DE COMPRADORES Y SUS COMPRAS ---")
    if not compradores:
        print(Fore.YELLOW + "No hay compradores registrados.")
    else:
        for comprador in compradores:
            print(Style.BRIGHT + f"\n[ID: {comprador['id']}] Nombre: {comprador['nombre']} | DNI: {comprador['dni']}")
            
            # Buscamos las ventas asociadas a este comprador
            compras_del_usuario = [v for v in ventas if v['id_comprador'] == comprador['id']]
            
            if not compras_del_usuario:
                print(Fore.WHITE + "  - Sin compras registradas.")
            else:
                for compra in compras_del_usuario:
                    evento = buscar_por_clave_recursivo(eventos, compra['id_evento'], 'id')
                    if evento:
                        locacion = buscar_por_clave_recursivo(locaciones, evento['id_locacion'], 'id')
                        if locacion:
                            tipo_entrada = locacion['tipos_entrada'][compra['tipo_entrada_idx']]
                            cantidad = compra['cantidad']
                            # (Requisito: Formateo de Cadenas)
                            print(Fore.GREEN + f"  - Compra ID {compra['id_venta']}: {cantidad}x '{tipo_entrada}' para el evento '{evento['nombre']}'.")
    
    input("\nPresione Enter para continuar...")
            
def eliminar_comprador(compradores, ventas):
    """
    Elimina un comprador si y solo si no tiene compras asociadas.
    """
    limpiar_pantalla()
    print(Fore.CYAN + "--- ELIMINAR COMPRADOR ---")
    if not compradores:
        print(Fore.YELLOW + "No hay compradores para eliminar.")
        input("\nPresione Enter para continuar...")
        return

    # Mostramos una lista simple para que elija a quién borrar
    for c in compradores:
        print(f"ID: {c['id']} | Nombre: {c['nombre']} | DNI: {c['dni']}")

    try:
        id_eliminar = int(input(Fore.YELLOW + "\nIngrese el ID del comprador a eliminar: "))
        comprador_a_eliminar = buscar_por_clave_recursivo(compradores, id_eliminar, 'id')

        if not comprador_a_eliminar:
            print(Fore.RED + "No se encontró un comprador con ese ID.")
        else:
            # Verificación CRÍTICA: ¿Tiene compras asociadas?
            compras_asociadas = [v for v in ventas if v['id_comprador'] == id_eliminar]
            if compras_asociadas:
                print(Fore.RED + f"\nError: No se puede eliminar a '{comprador_a_eliminar['nombre']}' porque tiene compras registradas.")
                print(Fore.RED + "Para eliminarlo, primero se deben reembolsar todas sus entradas.")
            else:
                confirmacion = input(f"¿Está seguro de que desea eliminar a {comprador_a_eliminar['nombre']}? (s/n): ").lower()
                if confirmacion == 's':
                    compradores.remove(comprador_a_eliminar)
                    guardar_datos(COMPRADORES_FILE, compradores, COMPRADORES_HEADERS)
                    print(Fore.GREEN + "\n¡Comprador eliminado con éxito!")
                else:
                    print(Fore.YELLOW + "\nEliminación cancelada.")

    except ValueError:
        print(Fore.RED + "Por favor, ingrese un ID numérico válido.")
        
    input("\nPresione Enter para continuar...")

def registrar_comprador(compradores):
    print(Fore.CYAN + "\n--- Registrar Nuevo Comprador ---")
    try:
        nombre = input("Nombre completo del comprador: ")
        dni = input("DNI del comprador: ")
        
        if not nombre or not dni:
            print(Fore.RED + "El nombre y el DNI no pueden estar vacíos.")
            return None

        # Validación: DNI numérico
        if not dni.isdigit():
            print(Fore.RED + "El DNI debe contener solo números.")
            return None

        existente = buscar_por_clave_recursivo(compradores, dni, 'dni')
        if existente:
            print(Fore.YELLOW + "Ya existe un comprador con ese DNI.")
            return existente

        nuevo_id = max([c['id'] for c in compradores] + [0]) + 1
        nuevo_comprador = {'id': nuevo_id, 'nombre': nombre, 'dni': dni}
        compradores.append(nuevo_comprador)
        guardar_datos(COMPRADORES_FILE, compradores, COMPRADORES_HEADERS)
        
        print(Fore.GREEN + f"\n¡Comprador '{nombre}' registrado con éxito con ID {nuevo_id}!")
        return nuevo_comprador

    except Exception as e:
        print(Fore.RED + f"\nHa ocurrido un error inesperado: {e}")
        return None

def listar_compradores(compradores):
    print(Fore.CYAN + "\n--- Lista de Compradores ---")
    if not compradores:
        print(Fore.YELLOW + "No hay compradores registrados.")
    else:
        for c in compradores:
            print(f"ID: {c['id']} | Nombre: {c['nombre']} | DNI: {c['dni']}")

def obtener_o_crear_comprador(compradores):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Paso 1: Identificar al Comprador ---")
    dni_buscado = input("Ingrese el DNI del comprador: ")
    
    comprador = buscar_por_clave_recursivo(compradores, dni_buscado, 'dni')
    
    if comprador:
        print(Fore.GREEN + f"Comprador encontrado: {comprador['nombre']} (ID: {comprador['id']})")
        time.sleep(2)
        return comprador
    else:
        print(Fore.YELLOW + "Comprador no encontrado. Por favor, registre sus datos.")
        return registrar_comprador(compradores)


# --- MÓDULO DE COMPRAS Y REEMBOLSOS --- (ACTUALIZADO)
def gestionar_compras_reembolsos(ventas, eventos, locaciones, compradores):
    while True:
        limpiar_pantalla()
        print(Fore.CYAN + "--- COMPRAS Y REEMBOLSOS ---")
        print("1. Realizar Venta de Entradas")
        print("2. Procesar Reembolso")
        print("0. Volver al Menú Principal")
        opcion = input(Fore.YELLOW + "Seleccione una opción: ")

        if opcion == '1':
            realizar_venta(ventas, eventos, locaciones, compradores) # Pasamos la lista de compradores
        elif opcion == '2':
            procesar_reembolso(ventas, eventos)
        elif opcion == '0':
            break
        else:
            print(Fore.RED + "Opción no válida.")
            time.sleep(1)

def realizar_venta(ventas, eventos, locaciones, compradores):
    # Paso 1: Identificar al comprador
    comprador_actual = obtener_o_crear_comprador(compradores)
    if not comprador_actual:
        input("\nNo se pudo identificar al comprador. Venta cancelada. Presione Enter para continuar...")
        return
        
    # Paso 2: Seleccionar evento y entradas
    limpiar_pantalla()
    print(Fore.CYAN + f"--- Paso 2: Venta para {comprador_actual['nombre']} ---")
    listar_eventos(eventos, locaciones)
    if not eventos:
        input("\nPresione Enter para continuar...")
        return
        
    try:
        id_evento = int(input("\nIngrese el ID del evento para la venta: "))
        evento = buscar_por_clave_recursivo(eventos, id_evento, 'id')
        
        if not evento:
            print(Fore.RED + "ID de evento no válido.")
            input("\nPresione Enter para continuar...")
            return

        locacion = buscar_por_clave_recursivo(locaciones, evento['id_locacion'], 'id')
        
        print("\nTipos de entrada disponibles:")
        for i in range(len(locacion['tipos_entrada'])):
            disponibles = evento['entradas_restantes'][i] if i < len(evento.get('entradas_restantes', [])) else 0
            precio = locacion['precios'][i] if i < len(locacion.get('precios', [])) else 0
            print(f"  {i}. Tipo: {locacion['tipos_entrada'][i]:<15} | Disponibles: {disponibles:<7} | Precio: ${precio:,.2f}")

        tipo_idx = int(input("Seleccione el número del tipo de entrada: "))
        cantidad = int(input("Ingrese la cantidad de entradas a comprar: "))

        if not (0 <= tipo_idx < len(locacion['tipos_entrada'])) or cantidad <= 0 or evento['entradas_restantes'][tipo_idx] < cantidad:
            print(Fore.RED + "Datos de venta inválidos (tipo, cantidad o disponibilidad).")
        else:
            # restamos en entero
            evento['entradas_restantes'][tipo_idx] = evento['entradas_restantes'][tipo_idx] - cantidad
            nuevo_id_venta = max([v['id_venta'] for v in ventas] + [0]) + 1
            
            nueva_venta = {
                'id_venta': nuevo_id_venta,
                'id_evento': id_evento,
                'id_comprador': comprador_actual['id'], # <-- ID DEL COMPRADOR CORRECTO
                'cantidad': cantidad,
                'tipo_entrada_idx': tipo_idx,
                'estado': 'activa'
            }
            
            ventas.append(nueva_venta)
            guardar_datos(VENTAS_FILE, ventas, VENTAS_HEADERS)
            guardar_datos(EVENTOS_FILE, eventos, EVENTOS_HEADERS)
            
            precio_total = float(locacion['precios'][tipo_idx]) * cantidad
            print(Fore.GREEN + f"\n¡Venta realizada con éxito! ID de Venta: {nuevo_id_venta}")
            print(f"Comprador: {comprador_actual['nombre']}. Total a pagar: ${precio_total}")

    except ValueError:
        print(Fore.RED + "\nError: Ingrese números válidos.")
    except Exception as e:
        print(Fore.RED + f"\nHa ocurrido un error inesperado: {e}")
        
    input("\nPresione Enter para continuar...")


# ------------------- GESTIÓN DE LOCACIONES -------------------
def listar_locaciones(locaciones):
    print(Fore.CYAN + "\n--- Lista de Locaciones ---")
    if not locaciones:
        print(Fore.YELLOW + "No hay locaciones registradas.")
    else:
        for l in locaciones:
            print(f"ID: {l['id']} | Nombre: {l['nombre']} | Tipos: {l['tipos_entrada']} | Precios: {l['precios']} | Capacidades: {l['capacidades']}")


def crear_locacion(locaciones):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Crear Nueva Locación ---")
    nombre = input("Nombre de la locación: ").strip()
    if not nombre:
        print(Fore.RED + "El nombre no puede estar vacío.")
        return

    # Evitar duplicados por nombre
    if buscar_por_clave_recursivo(locaciones, nombre, 'nombre'):
        print(Fore.YELLOW + "Ya existe una locación con ese nombre.")
        return

    precios_raw = input("Ingrese los precios separados por coma (ej: 15000.0,35000.0): ")
    capacidades_raw = input("Ingrese las capacidades separadas por coma (ej: 50000,25000): ")
    tipos_raw = input("Ingrese los tipos de entrada separados por coma (ej: Popular,Platea): ")

    precios = [p.strip() for p in precios_raw.split(',')] if precios_raw else []
    capacidades = [c.strip() for c in capacidades_raw.split(',')] if capacidades_raw else []
    tipos = [t.strip() for t in tipos_raw.split(',')] if tipos_raw else []

    # Convertir tipos a numéricos donde corresponda
    try:
        precios = [float(p) for p in precios]
        capacidades = [int(c) for c in capacidades]
    except Exception:
        print(Fore.RED + "Error: precios y capacidades deben ser números válidos.")
        return

    if not (len(precios) == len(capacidades) == len(tipos)):
        print(Fore.RED + "Los arrays de precios, capacidades y tipos deben tener la misma longitud.")
        return

    nuevo_id = max([l['id'] for l in locaciones] + [0]) + 1
    nueva = {'id': nuevo_id, 'nombre': nombre, 'precios': precios, 'capacidades': capacidades, 'tipos_entrada': tipos}
    locaciones.append(nueva)
    guardar_datos(LOCACIONES_FILE, locaciones, LOCACIONES_HEADERS)
    print(Fore.GREEN + f"Locación '{nombre}' creada con ID {nuevo_id}.")


def modificar_locacion(locaciones):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Modificar Locación ---")
    listar_locaciones(locaciones)
    try:
        id_mod = int(input("Ingrese el ID de la locación a modificar: "))
    except ValueError:
        print(Fore.RED + "ID inválido.")
        return

    loc = buscar_por_clave_recursivo(locaciones, id_mod, 'id')
    if not loc:
        print(Fore.RED + "Locación no encontrada.")
        return

    print(Fore.WHITE + f"Valores actuales (Enter para mantenerlos): nombre={loc['nombre']}, precios={loc['precios']}, capacidades={loc['capacidades']}, tipos={loc['tipos_entrada']}")
    nuevo_nombre = input("Nuevo nombre: ").strip()
    precios_raw = input("Nuevos precios (coma separada): ")
    capacidades_raw = input("Nuevas capacidades (coma separada): ")
    tipos_raw = input("Nuevos tipos (coma separada): ")

    if nuevo_nombre:
        # Evitar duplicado por nombre
        existente = buscar_por_clave_recursivo(locaciones, nuevo_nombre, 'nombre')
        if existente and existente['id'] != loc['id']:
            print(Fore.RED + "Ya existe otra locación con ese nombre. Operación cancelada.")
            return
        loc['nombre'] = nuevo_nombre
    if precios_raw:
        try:
            loc['precios'] = [float(p.strip()) for p in precios_raw.split(',')]
        except Exception:
            print(Fore.RED + "Precios inválidos. No se actualizó ese campo.")
    if capacidades_raw:
        try:
            loc['capacidades'] = [int(c.strip()) for c in capacidades_raw.split(',')]
        except Exception:
            print(Fore.RED + "Capacidades inválidas. No se actualizó ese campo.")
    if tipos_raw:
        loc['tipos_entrada'] = [t.strip() for t in tipos_raw.split(',')]

    guardar_datos(LOCACIONES_FILE, locaciones, LOCACIONES_HEADERS)
    print(Fore.GREEN + "Locación actualizada correctamente.")


def eliminar_locacion(locaciones, eventos):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Eliminar Locación ---")
    listar_locaciones(locaciones)
    try:
        id_del = int(input("Ingrese el ID de la locación a eliminar: "))
    except ValueError:
        print(Fore.RED + "ID inválido.")
        return

    loc = buscar_por_clave_recursivo(locaciones, id_del, 'id')
    if not loc:
        print(Fore.RED + "Locación no encontrada.")
        return

    # Verificar eventos asociados
    eventos_asociados = [e for e in eventos if e['id_locacion'] == id_del]
    if eventos_asociados:
        print(Fore.RED + "No se puede eliminar la locación porque tiene eventos asociados.")
        return

    confirm = input(f"¿Está seguro que desea eliminar '{loc['nombre']}'? (s/n): ")
    if confirm.lower() == 's':
        locaciones.remove(loc)
        guardar_datos(LOCACIONES_FILE, locaciones, LOCACIONES_HEADERS)
        print(Fore.GREEN + "Locación eliminada.")
    else:
        print(Fore.YELLOW + "Eliminación cancelada.")


def gestionar_locaciones(locaciones, eventos):
    while True:
        limpiar_pantalla()
        print(Fore.CYAN + "--- GESTIONAR LOCACIONES ---")
        print("1. Listar Locaciones")
        print("2. Crear Locacion")
        print("3. Modificar Locacion")
        print("4. Eliminar Locacion")
        print("0. Volver")
        op = input(Fore.YELLOW + "Seleccione una opción: ")
        if op == '1':
            listar_locaciones(locaciones)
            input("\nPresione Enter para continuar...")
        elif op == '2':
            crear_locacion(locaciones)
            input("\nPresione Enter para continuar...")
        elif op == '3':
            modificar_locacion(locaciones)
            input("\nPresione Enter para continuar...")
        elif op == '4':
            eliminar_locacion(locaciones, eventos)
            input("\nPresione Enter para continuar...")
        elif op == '0':
            break
        else:
            print(Fore.RED + "Opción no válida.")
            time.sleep(1)


# ------------------- GESTIÓN DE EVENTOS -------------------
def listar_eventos(eventos, locaciones):
    print(Fore.CYAN + "\n--- Lista de Eventos ---")
    if not eventos:
        print(Fore.YELLOW + "No hay eventos registrados.")
    else:
        for e in eventos:
            loc = buscar_por_clave_recursivo(locaciones, e['id_locacion'], 'id')
            nombre_loc = loc['nombre'] if loc else 'Desconocida'
            tipos = loc['tipos_entrada'] if loc else []
            precios = loc['precios'] if loc else []
            entradas = e.get('entradas_restantes', [])

            # Cabecera del evento
            print(Style.BRIGHT + Fore.MAGENTA + f"\nEvento ID {e['id']} - {e['nombre']} ({e['fecha']})")
            print(Fore.WHITE + f"Locación: {nombre_loc}")
            # Tabla de tipos
            print(Fore.CYAN + f"{'Idx':>3} | {'Tipo':<15} | {'Precio':>12} | {'Disponibles':>12}")
            print(Fore.CYAN + '-' * 55)
            for i in range(max(len(tipos), len(entradas))):
                tipo = tipos[i] if i < len(tipos) else 'N/A'
                precio = f"${precios[i]:,.2f}" if i < len(precios) else 'N/A'
                disponible = entradas[i] if i < len(entradas) else 'N/A'
                print(Fore.CYAN + f"{i:>3} | {tipo:<15} | {precio:>12} | {disponible:>12}")


def crear_evento(eventos, locaciones):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Crear Nuevo Evento ---")
    nombre = input("Nombre del evento: ").strip()
    fecha = input("Fecha (YYYY-MM-DD): ").strip()
    if not nombre or not fecha:
        print(Fore.RED + "Nombre y fecha obligatorios.")
        return

    # Validar fecha
    try:
        fecha_dt = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
        if fecha_dt < datetime.date.today():
            print(Fore.RED + "La fecha no puede ser anterior a hoy.")
            return
    except ValueError:
        print(Fore.RED + "Formato de fecha inválido. Use YYYY-MM-DD.")
        return

    listar_locaciones(locaciones)
    try:
        id_loc = int(input("Ingrese el ID de la locación donde se realizará el evento: "))
    except ValueError:
        print(Fore.RED + "ID inválido.")
        return

    loc = buscar_por_clave_recursivo(locaciones, id_loc, 'id')
    if not loc:
        print(Fore.RED + "Locación no encontrada.")
        return

    # entradas_restantes inicia como las capacidades de la locacion
    entradas_restantes = list(loc['capacidades'])

    nuevo_id = max([e['id'] for e in eventos] + [0]) + 1
    nuevo = {'id': nuevo_id, 'nombre': nombre, 'fecha': fecha, 'id_locacion': id_loc, 'entradas_restantes': entradas_restantes}
    eventos.append(nuevo)
    guardar_datos(EVENTOS_FILE, eventos, EVENTOS_HEADERS)
    print(Fore.GREEN + f"Evento '{nombre}' creado con ID {nuevo_id}.")


def modificar_evento(eventos, locaciones):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Modificar Evento ---")
    listar_eventos(eventos, locaciones)
    try:
        id_mod = int(input("Ingrese el ID del evento a modificar: "))
    except ValueError:
        print(Fore.RED + "ID inválido.")
        return

    evento = buscar_por_clave_recursivo(eventos, id_mod, 'id')
    if not evento:
        print(Fore.RED + "Evento no encontrado.")
        return

    print(Fore.WHITE + f"Valores actuales (Enter para mantenerlos): nombre={evento['nombre']}, fecha={evento['fecha']}, id_locacion={evento['id_locacion']}, entradas_restantes={evento['entradas_restantes']}")
    nuevo_nombre = input("Nuevo nombre: ").strip()
    nueva_fecha = input("Nueva fecha (YYYY-MM-DD): ").strip()
    nuevo_id_loc = input("Nuevo ID de locación: ").strip()

    if nuevo_nombre:
        evento['nombre'] = nuevo_nombre
    if nueva_fecha:
        try:
            fecha_dt = datetime.datetime.strptime(nueva_fecha, '%Y-%m-%d').date()
            if fecha_dt < datetime.date.today():
                print(Fore.RED + "La fecha no puede ser anterior a hoy. Cambio ignorado.")
            else:
                evento['fecha'] = nueva_fecha
        except ValueError:
            print(Fore.RED + "Formato de fecha inválido. Cambio ignorado.")
    if nuevo_id_loc:
        try:
            id_loc_n = int(nuevo_id_loc)
            if buscar_por_clave_recursivo(locaciones, id_loc_n, 'id'):
                evento['id_locacion'] = id_loc_n
            else:
                print(Fore.RED + "Locación nueva no encontrada. Cambio ignorado.")
        except ValueError:
            print(Fore.RED + "ID de locación inválido. Cambio ignorado.")

    guardar_datos(EVENTOS_FILE, eventos, EVENTOS_HEADERS)
    print(Fore.GREEN + "Evento actualizado correctamente.")


def eliminar_evento(eventos):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Eliminar Evento ---")
    if not eventos:
        print(Fore.YELLOW + "No hay eventos para eliminar.")
        return
    for e in eventos:
        print(f"ID: {e['id']} | Nombre: {e['nombre']} | Fecha: {e['fecha']}")
    try:
        id_del = int(input("Ingrese el ID del evento a eliminar: "))
    except ValueError:
        print(Fore.RED + "ID inválido.")
        return

    evento = buscar_por_clave_recursivo(eventos, id_del, 'id')
    if not evento:
        print(Fore.RED + "Evento no encontrado.")
        return

    confirm = input(f"¿Está seguro que desea eliminar el evento '{evento['nombre']}'? (s/n): ")
    if confirm.lower() == 's':
        eventos.remove(evento)
        guardar_datos(EVENTOS_FILE, eventos, EVENTOS_HEADERS)
        print(Fore.GREEN + "Evento eliminado.")
    else:
        print(Fore.YELLOW + "Eliminación cancelada.")


def gestionar_eventos(eventos, locaciones):
    while True:
        limpiar_pantalla()
        print(Fore.CYAN + "--- GESTIONAR EVENTOS ---")
        print("1. Listar Eventos")
        print("2. Crear Evento")
        print("3. Modificar Evento")
        print("4. Eliminar Evento")
        print("0. Volver")
        op = input(Fore.YELLOW + "Seleccione una opción: ")
        if op == '1':
            listar_eventos(eventos, locaciones)
            input("\nPresione Enter para continuar...")
        elif op == '2':
            crear_evento(eventos, locaciones)
            input("\nPresione Enter para continuar...")
        elif op == '3':
            modificar_evento(eventos, locaciones)
            input("\nPresione Enter para continuar...")
        elif op == '4':
            eliminar_evento(eventos)
            input("\nPresione Enter para continuar...")
        elif op == '0':
            break
        else:
            print(Fore.RED + "Opción no válida.")
            time.sleep(1)


# ------------------- REEMBOLSOS -------------------
def procesar_reembolso(ventas, eventos):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Procesar Reembolso ---")
    # Listar ventas activas
    ventas_activas = [v for v in ventas if v.get('estado', 'activa') == 'activa']
    if not ventas_activas:
        print(Fore.YELLOW + "No hay ventas activas para reembolsar.")
        input("\nPresione Enter para continuar...")
        return

    for v in ventas_activas:
        print(f"ID Venta: {v['id_venta']} | Evento: {v['id_evento']} | Comprador ID: {v['id_comprador']} | Cantidad: {v['cantidad']} | Tipo idx: {v['tipo_entrada_idx']}")

    try:
        id_v = int(input("Ingrese el ID de la venta a reembolsar: "))
    except ValueError:
        print(Fore.RED + "ID inválido.")
        return

    venta = buscar_por_clave_recursivo(ventas, id_v, 'id_venta')
    if not venta:
        print(Fore.RED + "Venta no encontrada.")
        return
    if venta.get('estado', 'activa') != 'activa':
        print(Fore.YELLOW + "La venta ya fue reembolsada o no está activa.")
        return

    # Devolver stock al evento
    evento = buscar_por_clave_recursivo(eventos, venta['id_evento'], 'id')
    if not evento:
        print(Fore.RED + "Evento vinculado no encontrado. No se puede procesar el reembolso automáticamente.")
        return

    idx = venta['tipo_entrada_idx']
    # entradas_restantes es lista de ints, sumar directamente
    evento['entradas_restantes'][idx] = evento['entradas_restantes'][idx] + int(venta['cantidad'])
    venta['estado'] = 'reembolsada'

    guardar_datos(VENTAS_FILE, ventas, VENTAS_HEADERS)
    guardar_datos(EVENTOS_FILE, eventos, EVENTOS_HEADERS)
    print(Fore.GREEN + "Reembolso procesado correctamente. La venta se marcó como 'reembolsada'.")
    input("\nPresione Enter para continuar...")


# ------------------- REPORTES -------------------
def reporte_ventas_por_evento(eventos, ventas, locaciones):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Reporte: Ventas por Evento ---")
    listar_eventos(eventos, locaciones)
    try:
        id_e = int(input("Ingrese el ID del evento a reportar: "))
    except ValueError:
        print(Fore.RED + "ID inválido.")
        input("\nPresione Enter para continuar...")
        return

    evento = buscar_por_clave_recursivo(eventos, id_e, 'id')
    if not evento:
        print(Fore.RED + "Evento no encontrado.")
        input("\nPresione Enter para continuar...")
        return

    loc = buscar_por_clave_recursivo(locaciones, evento['id_locacion'], 'id')
    tipos = loc['tipos_entrada'] if loc else []
    vendidos_por_tipo = [0] * len(tipos)
    recaudacion_total = 0.0

    for v in ventas:
        if v['id_evento'] == id_e and v.get('estado', 'activa') == 'activa':
            idx = v['tipo_entrada_idx']
            vendidos_por_tipo[idx] += int(v['cantidad'])
            precio = float(loc['precios'][idx]) if loc else 0.0
            recaudacion_total += precio * int(v['cantidad'])

    print(Fore.GREEN + f"Resumen para evento '{evento['nombre']}' (ID {evento['id']}):")
    for i, t in enumerate(tipos):
        print(f"  - {t}: {vendidos_por_tipo[i]} vendidos")
    print(Fore.GREEN + f"Recaudación estimada (ventas activas): ${recaudacion_total}")
    input("\nPresione Enter para continuar...")


def reporte_disponibilidad(eventos, locaciones):
    limpiar_pantalla()
    print(Fore.CYAN + "--- Reporte: Disponibilidad de Eventos ---")
    if not eventos:
        print(Fore.YELLOW + "No hay eventos.")
        input("\nPresione Enter para continuar...")
        return

    for e in eventos:
        loc = buscar_por_clave_recursivo(locaciones, e['id_locacion'], 'id')
        capacidades = loc['capacidades'] if loc else []
        porcentajes = []
        for i in range(len(capacidades)):
            cap = capacidades[i]
            restante = e['entradas_restantes'][i]
            porcentaje = (restante / cap * 100) if cap > 0 else 0
            porcentajes.append(f"{porcentaje:.1f}%")
        print(f"Evento ID {e['id']} - {e['nombre']} | Disponibilidad por tipo: {porcentajes}")

    input("\nPresione Enter para continuar...")


def gestionar_reportes(eventos, ventas, locaciones):
    while True:
        limpiar_pantalla()
        print(Fore.CYAN + "--- GENERAR REPORTES ---")
        print("1. Reporte de Ventas por Evento")
        print("2. Reporte de Disponibilidad")
        print("0. Volver")
        op = input(Fore.YELLOW + "Seleccione una opción: ")
        if op == '1':
            reporte_ventas_por_evento(eventos, ventas, locaciones)
        elif op == '2':
            reporte_disponibilidad(eventos, locaciones)
        elif op == '0':
            break
        else:
            print(Fore.RED + "Opción no válida.")
            time.sleep(1)

# --- MÓDULO PRINCIPAL --- 
def main():
    locaciones = cargar_datos(LOCACIONES_FILE, LOCACIONES_HEADERS)
    eventos = cargar_datos(EVENTOS_FILE, EVENTOS_HEADERS)
    ventas = cargar_datos(VENTAS_FILE, VENTAS_HEADERS)
    compradores = cargar_datos(COMPRADORES_FILE, COMPRADORES_HEADERS)

    while True:
        limpiar_pantalla()
        print(Fore.MAGENTA + Style.BRIGHT + "=========================================")
        print(Fore.MAGENTA + Style.BRIGHT + "==  SISTEMA DE VENTA DE ENTRADAS   ==")
        print(Fore.MAGENTA + Style.BRIGHT + "=========================================")
        print("Usuario actual: Vendedor")
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Gestionar Eventos")
        print("2. Gestionar Locaciones")
        print("3. Gestionar Compradores")
        print("4. Compras / Reembolsos")
        print("0. Salir")

        opcion = input(Fore.YELLOW + "\nSeleccione una opción: ")

        if opcion == '1':
            gestionar_eventos(eventos, locaciones)
        elif opcion == '2':
            gestionar_locaciones(locaciones)
        elif opcion == '3':
            # Ahora pasamos todas las listas necesarias para mostrar las compras
            gestionar_compradores(compradores, ventas, eventos, locaciones) 
        elif opcion == '4':
            gestionar_compras_reembolsos(ventas, eventos, locaciones, compradores)
        elif opcion == '0':
            print(Fore.CYAN + "¡Gracias por usar el sistema! Saliendo...")
            time.sleep(1)
            break
        else:
            print(Fore.RED + "Opción no válida. Por favor, intente de nuevo.")
            time.sleep(1)

# El resto del código (gestión de locaciones, eventos, etc.) permanece igual que en la versión anterior.
# Se omiten por brevedad, solo se incluyen las funciones modificadas o nuevas.
# Para que funcione, debes copiar y pegar este código completo sobre el anterior.
# Las funciones no mostradas aquí (como listar_eventos, etc.) deben estar presentes.

# --- PUNTO DE ENTRADA DEL SCRIPT ---
if __name__ == "__main__":
    # Asegúrate de tener todas las funciones definidas antes de llamar a main
    # (El código completo ya está arriba)

    main()