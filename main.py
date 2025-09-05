#SISTEMA DE VENTA DE ENTRADAS PARA ESPECTÁCULOS
#Implementar un sistema que gestione las ventas de entradas
#para distintos espectáculos a realizarse en un estadio, utilizando matrices,
#listas y diccionarios para mentener la información, almacenandola en archivos 
# para permitir su posterior recuperación. Aplicar recursividad para realizar las 
# busquedad de una manera agil y flexible.

#matriz con filas por show = [nombre, fecha, cant_Max_Entradas, precio, cant_Entradas_Vendidas]
#mas adelante tiene que leerse un archivo [con los shows] en vez de tenerlos en el programa
#Funciones 

def existeUsuario(email, usuarios_list): 
    for usuario in usuarios_list:
        if usuario[0] == email:  # email está en índice 1
            return True
    return False

def verificarContraseña(email, contraseña, usuarios_list):
    for usuario in usuarios_list:
        if usuario[0] == email and usuario[1] == contraseña:
            print("Inicio de sesión exitoso.")
            return True
    
    print("Contraseña incorrecta.")
    return False

def registrarUsuario(nombre, email, contraseña, usuarios_list):
    # Verificar si el usuario ya existe
    if existeUsuario(email, usuarios_list):
        print("El usuario ya existe.")
        return False
    
    # Agregar nuevo usuario: [email, contraseña, nombre, entradaComprada, cantComprada]
    usuarios_list.append([email, contraseña, nombre, -1, 0])
    print("Usuario registrado exitosamente.")
    return True

shows = [
    ["Nombre XD", "2026-05-15", 100, 50.0, 0],
    ["Lollapalooza 2026", "2026-03-12", 80, 30.0, 0],
    ["Big Time Rush", "2026-04-24", 150, 75.0, 0],
    ["Espectaculo caro", "2026-06-30", 50, 15000.0, 0],
]
#diccionario para almacenar los usuarios
#nombre, mail, contraseña, entradaComprada (id de show, no nombre), cantComprada

#se registra o inicia sesion
#aparece menu con acciones posibles: 1. comprar entradas 2. ver mis entradas -1. salir (cerrar sesión)
#si el usuario ya tiene entradas compradas, no puede comprar a otros shows que no sea del que ya tiene
#si el usuario no tiene entradas, puede comprar en cualquier show


#esto es una mantriz pero tiene que hacerse diccionarios cuando lo veamos OJO
usuarios = []

#MAIN
#Aca verificamos al usuario




validado = False
mail = input("Ingrese su mail: ")
if(existeUsuario(mail, usuarios)):
    #Pedimos contraseña para verificar que sea el usuario correcto
    contr = input("Ingrese su contraseña: ")
    validado = verificarContraseña(mail, contr, usuarios)
        
else:
    print("No existe el usuario, proceda a registrarse.")
    # mail = input("Ingrese su mail: ")
    contr = input("Ingrese su contraseña: ")
    nombre = input("Ingrese su nombre: ")
    validado = registrarUsuario(nombre, mail, contr, usuarios)

if(validado):
    print(f"Bienvenido")
    #Mostrar menu de inicio
    while True:
        print("1. Comprar entradas")
        print("2. Ver mis entradas")
        print("-1. Salir")
        opcion = int(input("Ingrese una opción: "))
        if(opcion == 1):
            #Espectaculos disponibles e información de cada uno
            print("Espectáculos disponibles:")
            showElegido = -1
            for i,show in enumerate(shows):
                print(f"{i+1}. {shows.index(show)} - {show[0]} - {show[1]} - Entradas disponibles: {show[2] - show[4]} - Precio: ${show[3]}")
            showElegido = int(input("Ingrese el número del espectáculo al que desea asistir: "))
            if showElegido > 0 and showElegido <= len(shows):
                showElegido -= 1
                #Comprar entradas
                print(f"Has seleccionado: {shows[showElegido][0]} el {shows[showElegido][1]}")
                cantEntradas = int(input(f"Cuantas entradas desea comprar? (Disponibles: {shows[showElegido][2] - shows[showElegido][4]})\n"))
                if cantEntradas > 0 and cantEntradas <= (shows[showElegido][2] - shows[showElegido][4]):
                    #Verificar si el usuario ya tiene entradas compradas
                    for usuario in usuarios:
                        if usuario[0] == mail:
                            if usuario[3] == -1 or usuario[3] == showElegido:
                                #Actualizar la cantidad de entradas vendidas en el show
                                shows[showElegido][4] += cantEntradas
                                #Actualizar la información del usuario
                                usuario[3] = showElegido
                                usuario[4] += cantEntradas
                                print(f"Has comprado {cantEntradas} entradas para {shows[showElegido][0]}.")
                            else:
                                print("Ya tienes entradas compradas para otro espectáculo. No puedes comprar en este.")
                            
            else:
                print("Opción inválida.")
                
        elif(opcion == 2):
            print("Estas son tus entradas")
            for usuario in usuarios:
                if usuario[0] == mail:
                    if usuario[3] == -1:
                        print("No tienes entradas compradas.")
                    else:
                        idShow = usuario[3]
                        cant = usuario[4]
                        showComprado = shows[idShow]
                        print(f"Espectáculo: {showComprado[0]} - Fecha: {showComprado[1]} - Cantidad de entradas: {cant} - Precio total: ${cant * showComprado[3]}")
                    break
        else:
            print("Cerrando sesión...")
            break

        