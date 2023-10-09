import yaml
import requests
from prettytable import PrettyTable

class Alumno:
    def __init__(self, nombre, codigo, mac):
        self.nombre= nombre
        self.codigo = codigo
        self.mac = mac

class Curso:
    def __init__(self, codigo, estado, nombre, alumnos, servidores):
        self.codigo = codigo
        self.nombre= nombre
        self.estado= estado
        self.alumnos= alumnos
        self.servidores= servidores

class Servidor:
    def __init__(self, nombre, ip, servicios):
        self.nombre= nombre
        self.ip= ip
        self.servicios= servicios

def get_attachment_point(mac_address):
    controller_ip = '10.20.12.132'  
    target_api = '/wm/topology/links/json'
    url = f'http://{controller_ip}:8080{target_api}'
    
    params = {"dst-mac": mac_address}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            link = data[0]
            return link["src-switch"], link["src-port"]
        else:
            return None
    else:
        raise Exception("Error al obtener los puntos de conexión.")

def get_route(dpid_origen, puerto_origen, dpid_destino, puerto_destino):
    controller_ip = '10.20.12.132'  
    target_api = '/wm/topology/route/'
    url = f'http://{controller_ip}:8080{target_api}{dpid_origen}/{puerto_origen}/{dpid_destino}/{puerto_destino}/json'
    
    headers = {'Content-type': 'application/json','Accept': 'application/json'}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        table = PrettyTable(data[0].keys())
        for row in data:
            table.add_row(row.values())
        print(table)
    else:
        raise Exception("Error al obtener la ruta.")


def build_route():
    print("Build route ...")

def menu():
    print("\n#####################################################")
    print("Network Policy manager de la UPSM")
    print("#####################################################")
    print("\nSeleccione una opción:")
    print('\n1) Importar \n2) Exportar \n3) Cursos \n4) Alumnos \n5) Servidores \n6) Políticas \n7) Conexiones \n8) Salir \n')
    opcion_seleccionada = input('>>> ')
    return opcion_seleccionada

def importar(archivo):
    try:
        with open(archivo, 'r') as file:
            datos = yaml.safe_load(file)
        return datos
    except FileNotFoundError:
        print(f"Error: el archivo '{archivo}' no se encontró.")
        return None

def seccion_cursos(datos):
    while True:    
        print("\nSeleccione una opción:")
        opcion_curso = input("\t1) Listar cursos \n\t2) Agregar alumno a curso \n\t3) Eliminar curso\n\t4) Volver al menú principal\n>>> ")
        
        if opcion_curso == '1':
            listar_cursos(datos)
        elif opcion_curso == '2':
            agregar_alumno_a_curso(datos)
        elif opcion_curso == '3':
            curso_a_borrar = input('Ingrese el código del curso que desea eliminar (en mayúsculas):\n>>> ')
            if borrar_curso(curso_a_borrar, datos):
                print(f"Curso con código {curso_a_borrar} eliminado con éxito.")
            else:
                print(f"No se pudo eliminar el curso con código {curso_a_borrar}.")
        elif opcion_curso == '4':
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida del menú.")
        
def listar_cursos(datos):
    lista_servidores = datos['servidores']
    if not lista_servidores:
        print("No hay servidores en la base de datos.")
        return
    while True:
        print("\nSeleccione la manera de listar cursos:")
        print("\t1) Listar cursos por servidor")
        print("\t2) Listar cursos por servicio")
        print("\t3) Listar todos los cursos")
        print("\t4) Volver")
        filtro_cursos = input(">>> ")
        if (filtro_cursos=='1'):
            cursos_list = []
            print("\nSeleccione uno de los siguiente servidores:")
            i=1
            for servidor in lista_servidores:
                print(f"\t{i}) {servidor['nombre']}")
                i=i+1
            opcion_elegida = input(">>>")
            servidor_elegido = lista_servidores[int(opcion_elegida)-1]
            print("Cursos del",servidor_elegido['nombre'],":")
            for curso in datos['cursos']:
                for serv in curso['servidores']:
                    if serv['nombre'] == servidor_elegido['nombre']:
                        nombre_curso = curso['nombre']
                        estado_curso = curso['estado']
                        cursos_list.append(curso)
                        print("\n\t- Nombre del curso:", nombre_curso, "\n\t  Estado:", estado_curso)
            while True:
                print("\nSeleccione una opción:")
                print("\t1) Mostrar más detalles de los cursos")
                print("\t2) Volver")
                opcion_elegida_2 = input(">>> ")
                if (opcion_elegida_2=='1'):
                    mostrar_detalles_curso(cursos_list)
                    break
                if (opcion_elegida_2=='2'):    
                    break
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida del menú.")

        elif (filtro_cursos=='2'):
            print("\nSeleccione uno de los siguientes servicios:")
            i = 1
            cursos_list = []
            servicios_disponibles = []
            for servidor in lista_servidores:
                for servicio in servidor['servicios']:
                    nombre_servicio = servicio['nombre']
                    servicios_disponibles.append(nombre_servicio)
                    print(f"\t{i}) {nombre_servicio}")
                    i=i+1
            opcion_elegida = input(">>> ")
            servicio_elegido = servicios_disponibles[int(opcion_elegida)-1]
            print("Cursos que cuentan con el servicio",servicio_elegido,":")
            for curso in datos['cursos']:
                for serv in curso['servidores']:
                    for service in serv['servicios_permitidos']:
                        if service == servicio_elegido:
                            nombre_curso = curso['nombre']
                            estado_curso = curso['estado']
                            cursos_list.append(curso)
                            print("\n\t- Nombre del curso:", nombre_curso, "\n\t  Estado:", estado_curso)
            while True:
                print("\nSeleccione una opción:")
                print("\t1) Mostrar más detalles de los cursos")
                print("\t2) Volver")
                opcion_elegida_2 = input(">>> ")
                if (opcion_elegida_2=='1'):
                    mostrar_detalles_curso(cursos_list)
                    break
                if (opcion_elegida_2=='2'):    
                    break
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida del menú.")

        elif (filtro_cursos=='3'):    
            print("\nTodos los cursos existentes:")
            if 'cursos' in datos:
                lista_cursos = datos['cursos']
                if not lista_cursos:
                    print("\n\tNo hay cursos en la base de datos.\n")
                else:
                    for curso in lista_cursos:
                        nombre_curso = curso['nombre']
                        estado_curso = curso['estado']
                        print("\n\t- Nombre del curso:", nombre_curso, "\n\t  Estado:", estado_curso)
                while True:
                    print("\nSeleccione una opción:")
                    print("\t1) Mostrar más detalles de los cursos")
                    print("\t2) Volver")
                    opcion_elegida_2 = input(">>> ")
                    if (opcion_elegida_2=='1'):
                        mostrar_detalles_curso(lista_cursos)
                        break
                    if (opcion_elegida_2=='2'):    
                        break
                    else:
                        print("Opción no válida. Por favor, seleccione una opción válida del menú.")
            else:
                print("No hay cursos en la base de datos.")
        elif (filtro_cursos=='4'):
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida del menú.")

def mostrar_detalles_curso(lista_cursos):
    for curso in lista_cursos:
        nombre_curso = curso['nombre']
        print("\n\t- Nombre del curso:", nombre_curso)
        codigo_curso = curso['codigo']
        print("\t  Codigo del curso:", codigo_curso)
        estado_curso = curso['estado']
        print("\t  Estado del curso:", estado_curso)
        alumnos_curso = curso['alumnos']
        print("\t  Alumnos del curso:")
        for alumno in alumnos_curso:
            print("\t\t\t-", alumno)
        servidores_curso = curso['servidores']
        print("\t  Servidores del curso:")
        for servidor in servidores_curso:
            nombre_servidor = servidor['nombre']
            servicios_permitidos = servidor.get('servicios_permitidos', [])
            print("\t\t\t- Nombre del servidor:", nombre_servidor)
            for servicio in servicios_permitidos:
                print("\t\t\t  Servicios permitidos:", servicio)

def borrar_curso(codigo_curso, datos):
    if 'cursos' in datos:
        lista_cursos = datos['cursos']
        curso_encontrado = None
        for curso in lista_cursos:
            if curso['codigo'] == codigo_curso:
                curso_encontrado = curso
                break
        if curso_encontrado:
            lista_cursos.remove(curso_encontrado)
            return True
        else:
            print(f"No se encontró ningún curso con el código {codigo_curso}.")
            return False
    else:
        print("No hay cursos en la base de datos.")
        return False

def agregar_alumno_a_curso(datos):
    lista_cursos = datos['cursos']
    lista_alumnos = datos['alumnos']
    i=1
    j=1
    print("\nSeleccione la opción del curso al que desee agregar un alumno:")
    for curso in lista_cursos:
        print(f"\t{i}) {curso['codigo']} - {curso['nombre']}")
        i=i+1   
    opcion_elegida = input(">>> ")
    curso_elegido = lista_cursos[int(opcion_elegida)-1]
    print(f"\nSeleccione la opción del alumno que desee agregar al curso {curso_elegido['nombre']}:")
    for alumno in lista_alumnos:
        print(f"\t{j}) {alumno['nombre']}")  
        j=j+1 
    opcion_elegida_2 = input(">>> ")
    alumno_elegido = lista_alumnos[int(opcion_elegida_2)-1]

    alumno_matriculado = False
    for codigo in curso_elegido['alumnos']:
        if codigo == alumno_elegido['codigo']:
            alumno_matriculado = True
        else:
            alumno_matriculado = False
            
    if alumno_matriculado == True:
        print(f"El alumno {alumno_elegido['nombre']} ya pertenece al curso {curso_elegido['nombre']}")
    else:
        curso_elegido['alumnos'].append(alumno_elegido['codigo'])
        print(f"El alumno {alumno_elegido['nombre']} fue agregado al curso {curso_elegido['nombre']}")    
    
def seccion_alumnos(datos):
    while True:
        if 'alumnos' in datos:
            lista_alumnos = datos['alumnos']
            if not lista_alumnos:
                print("No hay alumnos en la base de datos.")
            else:
                print("\nSeleccione una opción:")
                print("\t1) Listar alumnos")
                print("\t2) Agregar alumno")
                print("\t3) Volver al menú principal")
                opcion_alumnos = input(">>> ")
                if opcion_alumnos == '1':
                    listar_alumnos(datos)                    
                elif opcion_alumnos == '2':
                    agregar_alumno(datos)    
                elif opcion_alumnos == '3':
                    break       
                else:
                    print("Opción no válida. Por favor, seleccione una opción válida.")

def listar_alumnos(datos):
    lista_cursos = datos['cursos']
    lista_alumnos = datos['alumnos']
    i = 1
    while True:
        print("\nSeleccione la manera de listar alumnos:")
        print("\t1) Listar alumnos por curso")
        print("\t2) Listar todos los alumnos")
        print("\t3) Volver")
        filtro_listar = input(">>> ")
        if(filtro_listar=='1'):
            print("\nSeleccione uno de los siguiente cursos:")
            for curso in lista_cursos:
                print(f"\t{i}) {curso['codigo']} - {curso['nombre']}")
                i=i+1
            opcion_elegida = input(">>>") 
            curso_elegido = lista_cursos[int(opcion_elegida)-1]
            lista_alumnos_por_curso = curso_elegido['alumnos']
            print("\nAlumnos del curso",curso_elegido['codigo'],"-", curso_elegido['nombre'],":")
            for codigo_alumno in lista_alumnos_por_curso:
                alumno = None
                for a in lista_alumnos:
                    if a['codigo'] == codigo_alumno:
                        alumno = a
                        mostrar_detalles_alumno(alumno)
                        break            
        elif (filtro_listar=='2'):
            print("\nTodos los alumnos existentes:")
            for alumno in lista_alumnos:
                mostrar_detalles_alumno(alumno)
        elif (filtro_listar=='3'):
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")
        

def mostrar_detalles_alumno(alumno):
    print("\n\t- Alumno:", alumno['nombre'])
    print("\t  Código:", alumno['codigo'])
    print("\t  MAC:", alumno['mac'])  

def agregar_alumno(datos):
    if 'alumnos' in datos:
        lista_alumnos = datos['alumnos']
        nuevo_alumno = {}
        nuevo_alumno['nombre'] = input("Ingrese el nombre del nuevo alumno:\n>>> ")
        nuevo_alumno['codigo'] = int(input("Ingrese el código del nuevo alumno:\n>>> "))
        nuevo_alumno['mac'] = input("Ingrese la MAC del nuevo alumno:\n>>> ")

        # Se verifica si el código del nuevo alumno ya existe
        codigo_existente = False
        for alumno in lista_alumnos:
            if alumno['codigo'] == nuevo_alumno['codigo']:
                codigo_existente = True
                break

        if not codigo_existente:
            lista_alumnos.append(nuevo_alumno)
            print("Alumno agregado con éxito.")
        else:
            print("Error: El código del alumno ya existe en la base de datos.")
    else:
        print("No se pudo agregar al alumno. Primero importa el archivo de datos.")
    
def listar_servidores(datos):
    while True:
        if 'servidores' in datos:
            lista_servidores = datos['servidores']
            if not lista_servidores:
                print("No hay servidores en la base de datos.")
            else:
                print("\nTodos los servidores existentes:")
                for servidor in lista_servidores:
                    nombre_servidor = servidor['nombre']
                    ip_servidor = servidor['ip']
                    print("\n\tNombre del servidor:", nombre_servidor)
                    print("\tIP del servidor:", ip_servidor)
        else:
            print("No hay servidores en la base de datos.")
        print("\nSeleccione un opción:")    
        opcion_servidor = input("\t1) Ver más detalles de los servidores.\n\t2) Volver al menú principal.\n>>>")
        if opcion_servidor == '1':
            print("Ingrese el nombre del servidor:")
            servidor_elegido = input(">>> ")
            s = None
            for serv in lista_servidores:
                if (servidor_elegido==serv['nombre']):
                    s = serv
            mostrar_detalles_servidor(s)
        elif opcion_servidor == '2':
            break       
        else:
            print("Opción no válida. Por favor, seleccione una opción válida del menú.")     
    
def mostrar_detalles_servidor(servidor):
    print("\nDetalles del",servidor['nombre'],":")
    print("\tNombre del servidor:", servidor['nombre'])
    print("\tIP del servidor:", servidor['ip'])
    print("\tServicios brindados:")  
    lista_servicios = servidor.get('servicios', [])
    for servicio in lista_servicios:
        print("\t\tNombre del servicio:", servicio['nombre'])
        print("\t\tProtocolo:", servicio['protocolo'])
        print("\t\tPuerto:", servicio['puerto'])          

def seccion_conexiones(data):
    while True:
        print("\nSeleccione un opción:")
        print("1) Crear conexión.")
        print("2) Listar las conexiones.")
        print("3) Borrar conexión.")
        print("4) Volver al menú principal.")
        opcion_conexiones = input(">>> ")
        while True:
            if opcion_conexiones == '1':
                codigo_alumno = input("Ingrese el código del alumno:\n>>> ")
                servicio = input("Ingrese el servicio que desea enrutar:\n>>> ")
                autorizado = verificar_autorizacion(data, codigo_alumno, servicio)
                if autorizado:
                    print("El alumno está autorizado para acceder al servicio en el servidor.")
                    alumno_seleccionado = None
                    for a in data['alumnos']:
                        if a['codigo']==int(codigo_alumno):
                            alumno_seleccionado = a
                            break
                    mac_alumno = alumno_seleccionado['mac']
                    ip_serv = 0
                    for s in data['servidores']:
                        ip_serv = s['ip']  
                    #mac_server = get_mac(ip_serv)
                    mac_server = 'fa:16:3e:9d:2e:10'
                    dpid_orig, puerto_orig = get_attachment_point(mac_alumno)
                    dpid_dest, puerto_dest = get_attachment_point(mac_server) 
                    print(f'DPID origen: {dpid_orig}, Puerto origen: {puerto_orig}')
                    print(f'DPID destino: {dpid_dest}, Puerto destino: {puerto_dest}')

                    try:
                        get_route(dpid_orig, puerto_orig, dpid_dest, puerto_dest)
                        build_route()
                    except Exception as e:
                        print(f"Error al obtener la ruta: {e}")               
                    break
                else:
                    print("El alumno no está autorizado para acceder al servicio indicado.")  
                    break
            if opcion_conexiones == '2':
                    listar_conexiones()
                    break
            if opcion_conexiones == '4':
                    break
            else:
                print("Opción no válida. Por favor, seleccione una opción válida del menú.")
                break

def get_mac(hostip):
    ip_controller = "10.20.12.132"
    url = f"http://{ip_controller}:8080/wm/device/"
    resp = requests.get(url)
    resp = resp.json()
    for i in resp:
        if((hostip in i["ipv4"] )):
            return i["mac"][0]
    return "MAC no encontrada"

def verificar_autorizacion(datos, alumno_codigo, servicio_nombre):
    if 'cursos' in datos and 'alumnos' in datos and 'servidores' in datos:
        alumno = None
        for a in datos['alumnos']:
            if a['codigo'] == int(alumno_codigo):
                alumno = a
                break
        if alumno is None:
            return False 
        for curso in datos['cursos']:
            if curso['estado'] == 'DICTANDO':
                servidores_curso = curso['servidores']
                for servidor in servidores_curso:
                    if servicio_nombre in servidor.get('servicios_permitidos', []):
                        return True 
    
    return False 

def listar_conexiones():
    print("listado...")

if __name__ == "__main__":
    data = None
    while True:
        opcion_seleccionada = menu()
        if opcion_seleccionada == '1':
            data = importar('database.yaml')
            if data:
                print("Archivo importado correctamente.")

        elif opcion_seleccionada == '3':
            if data:
                seccion_cursos(data)
            else:
                print("Primero importe el archivo de datos.")

        elif opcion_seleccionada == '4':
            if data:
                seccion_alumnos(data)
            else:
                print("Primero importe el archivo de datos.")

        elif opcion_seleccionada == '5':
            if data:
                listar_servidores(data)
            else:
                print("Primero importe el archivo de datos.")

        elif opcion_seleccionada == '7':
            if data:
                seccion_conexiones(data)
            else:
                print("Primero importe el archivo de datos.")

        elif opcion_seleccionada == '8':
            break
        else:
            print("Opción no válida. Por favor, seleccione una opción válida del menú.")
