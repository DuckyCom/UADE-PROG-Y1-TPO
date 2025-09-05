#Funciones 
import os
import time



def existeUsuario(email, usuarios_list): 
    for usuario in usuarios_list:
        if usuario[1] == email:  # email está en índice 1
            return True
    return False

def verificarContraseña(email, contraseña, usuarios_list):
    for usuario in usuarios_list:
        if usuario[1] == email and usuario[2] == contraseña:  # email en índice 1, contraseña en índice 2
            print("Inicio de sesión exitoso.")
            return True
    print("Contraseña incorrecta.")
    return False

def registrarUsuario(nombre, email, contraseña, usuarios_list):
    # Verificar si el usuario ya existe
    if existeUsuario(email, usuarios_list):
        print("El usuario ya existe.")
        return False
    
    # Agregar nuevo usuario: [nombre, email, contraseña, entradaComprada, cantComprada]
    usuarios_list.append([nombre, email, contraseña, -1, 0])
    print("Usuario registrado exitosamente.")
    return True


def cerrandoSesion():
    for i in range(3, 0, -1):
        print(f"Cerrando sesión{'.' * i}{' ' * (3 - i)}", end='\r')
        time.sleep(1.15)
    os.system('cls')  # Limpia la consola
    return






