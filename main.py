#SISTEMA DE VENTA DE ENTRADAS PARA ESPECTÁCULOS
#Implementar un sistema que gestione las ventas de entradas
#para distintos espectáculos a realizarse en un estadio, utilizando matrices,
#listas y diccionarios para mentener la información, almacenandola en archivos 
# para permitir su posterior recuperación. Aplicar recursividad para realizar las 
# busquedad de una manera agil y flexible.

#matriz con filas por show = [nombre, fecha, cant_Max_Entradas, precio, cant_Entradas_Vendidas]
#mas adelante tiene que leerse un archivo [con los shows] en vez de tenerlos en el programa
#Funciones

# TO DO
# Cambiar en la funcion registrarUsuario: el append por este: listaUsuarios.append([username, email, contraseña, [idShow, cantEntradas]]) 
# Con esto hacemos una lista de tuplas (id_show, cantidad) para las compras.
# Agregar que se lean/escriban los usuarios y shows a archivos .json/.csv
# 

# DONE
# HACER QUE LA SALIDA ESTÉ FORMATEADA, MÁS PROLIJA
# CON LO DE RIGHT O PONER VACIOS O SIMILAR
# PONER EN MIS ENTRADAS FORMATO nombreShow .............. numEntradas
# HICIMOS DE QUE NO APAREZCAN LOS SHOWS CON 0 ENTRADAS DISPONIBLES PERO
# SI SELECCIONA SU NUMERO, APARECE PARA COMPRAR IGUALMENTE, DEBE DE HABER UNA VERIFICACION PARA QUE
# SI ENTRADAS DISPONIBLES = 0, NO DEJE SELECCIONAR ESE SHOW [TIRE OPCION INVALIDA]
 
import os
import time

def cerrandoSesion():
    for i in range(3, 0, -1):
        print(f"Cerrando sesión{'.' * i}{' ' * (3 - i)}", end='\r')
        time.sleep(1.15)
    os.system('cls')  # Limpia la consola
    return

def limpiarconsola():
    os.system('cls')  # Limpia la consola
    return

def existeUsuario(email, listaUsuarios): 
    for usuario in listaUsuarios:
        if usuario[1] == email:  # email está en índice 1
            return True
    return False

def verificarContraseña(email, contraseña, listaUsuarios):
    for usuario in listaUsuarios:
        if usuario[1] == email and usuario[2] == contraseña:
            print("Inicio de sesión exitoso.")
            return True
    
    print("Contraseña incorrecta.")
    return False

def registrarUsuario(username, email, contraseña, listaUsuarios):
    # Verificar si el usuario ya existe
    if existeUsuario(email, listaUsuarios):
        print("El usuario ya existe.")
        return False
    
    # Agregar nuevo usuario: [email, contraseña, nombre, entradaComprada, cantComprada]
    listaUsuarios.append([username, email, contraseña, -1, 0])
    print("Usuario registrado exitosamente.")
    return True

def transfNombreUsuario(mail):
    username = (mail.split('@')[0]).title()
    #print("Este es el username que sale de la funcion: ", username)
    return username

shows = [
    ["Nombre XD", "2026-05-15", 100, 50.0, 0],
    ["Lollapalooza 2026", "2026-03-12", 80, 30.0, 0],
    ["Big Time Rush", "2026-04-24", 150, 75.0, 0],
    ["Espectaculo caro", "2026-06-30", 50, 15000.0, 0],
]

listaUsuarios = []

def logueo():
    validado = False
    while not validado:
        usuario = []
        #print(f"Esto es lo que hay {listaUsuarios}")
        mail = input(("Ingrese su mail: ").ljust(30, '.'))
        if "@" in mail and "." in mail:
            if(existeUsuario(mail, listaUsuarios)):
                #Pedimos contraseña para verificar que sea el usuario correcto
                contr = input("Ingrese su contraseña: ")
                validado = verificarContraseña(mail, contr, listaUsuarios)
            else:
                print("No existe el usuario, proceda a registrarse.")
                # mail = input("Ingrese su mail: ")
                contr = input(("Ingrese su contraseña: ").ljust(30, '.'))
                username = transfNombreUsuario(mail)
                #print(f"Nombre de usuario: {username}")
                validado = registrarUsuario(username, mail, contr, listaUsuarios)
        else:
            print("El mail ingresado no es válido.")
    for usuario in listaUsuarios:
        if usuario[1] == mail:
            return usuario
#diccionario para almacenar los usuarios
#user, mail, contraseña, entradaComprada (id de show, no nombre), cantComprada

#se registra o inicia sesion
#aparece menu con acciones posibles: 1. comprar entradas 2. ver mis entradas -1. salir (cerrar sesión)
#si el usuario ya tiene entradas compradas, no puede comprar a otros shows que no sea del que ya tiene
#si el usuario no tiene entradas, puede comprar en cualquier show

#MAIN
usuarioLogueado = []
usuarioLogueado = logueo()
logueoPrimero = True
while(usuarioLogueado != []):
    #Mostrar menu de inicio
    while True:
        # print("vuelve al primer while")
        if logueoPrimero:
            print((f"Bienvenido {usuarioLogueado[0]}!").center(50,'-'))
            logueoPrimero = False
        print(f"\n1. Comprar entradas")
        print("2. Ver mis entradas")
        print("-1. Salir")
        opcion = int(input("Ingrese una opción: "))
        if(opcion == 1):
            #Espectaculos disponibles e información de cada uno
            limpiarconsola()
            print("Espectáculos disponibles:")
            showElegido = -1
            for i,show in enumerate(shows):
                if(show[2] - show[4]) > 0:
                    print(f"{i+1}. {show[0]} - {show[1]} - Entradas disponibles: {show[2] - show[4]} - Precio: ${show[3]}")
            showElegido = int(input("Ingrese el número del espectáculo al que desea asistir: "))
            #aca verifica que el show elegido sea válido y que haya entradas disponibles
            if showElegido > 0 and showElegido <= len(shows) and (shows[showElegido-1][2] - shows[showElegido-1][4]) > 0:
                showElegido -= 1
                #Comprar entradas
                limpiarconsola()
                print(f"Has seleccionado: {shows[showElegido][0]} el {shows[showElegido][1]}")
                cantEntradas = int(input(f"Cuantas entradas desea comprar? (Disponibles: {shows[showElegido][2] - shows[showElegido][4]})\n"))
                if cantEntradas > 0 and cantEntradas <= (shows[showElegido][2] - shows[showElegido][4]):
                    #Verificar si el usuario ya tiene entradas compradas
                        if usuarioLogueado[3] == -1 or usuarioLogueado[3] == showElegido:
                            #Verificar el precio a pagar
                            confirmacion = input(f"Está por pagar ${cantEntradas * shows[showElegido][3]}. Confirma la compra? (Si/No)\n")
                            if(confirmacion.lower() == "si"):
                                    #Actualizar la cantidad de entradas vendidas en el show
                                shows[showElegido][4] += cantEntradas
                                #Actualizar la información del usuario
                                usuarioLogueado[3] = showElegido
                                usuarioLogueado[4] += cantEntradas
                                limpiarconsola()
                                print((f"Has comprado {cantEntradas} entradas para {shows[showElegido][0]}.").center(50,'-'))
                            else:
                                limpiarconsola()
                                print("Compra cancelada.")
                        else:
                            limpiarconsola()
                            print("Ya tienes entradas compradas para otro espectáculo. No puedes comprar en este.")
                else:
                    limpiarconsola()
                    print("Se está tratanto de comprar una cantidad inválida de entradas.")            
            else:
                limpiarconsola()
                print("Opción inválida.")    
                
        elif(opcion == 2):
            if usuarioLogueado[3] == -1:
                limpiarconsola()
                print(("No tienes entradas compradas.").center(50,'-'))
            else:
                limpiarconsola()
                print(("Estas son tus entradas: ").center(50,'-')) # PONER EN CENTRO
                idShow = usuarioLogueado[3]
                cant = usuarioLogueado[4]
                showComprado = shows[idShow]
                print(f"{showComprado[0]} - {showComprado[1]} - {cant} entradas - ${cant * showComprado[3]}\n") #HACER LO DE BARRA Y FLECHAS QUE DIJO BENJA
            break
        elif(opcion == -1):
            cerrandoSesion()
            usuarioLogueado = logueo()
            logueoPrimero = True
            break
        else:
            print("Opción inválida.")


