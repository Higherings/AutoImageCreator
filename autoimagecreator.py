# igarcia 2019-10-29
# Version 2.1
# Funcion para generar AMIs de las Instancias con determinado Tag y que tambien tengan definido tag "Name"
# Elimina las AMIs mas alla del Historico
# Da opcion de reiniciar o no Instancia antes de crear Imagen


import boto3
import datetime
import json
import os

ec2 = boto3.resource('ec2')
TAGFECHACREACION = "FechaCreacion"
TAGGENERATED = "GeneratedBy"
TAGID = "EC2"

def lambda_handler(event, context):
    tagbusqueda = os.environ['TAGBUSQUEDA']
    tagvalor = os.environ['TAGVALOR']
    historico = int(os.environ['HISTORICO'])
    opreboot = not(bool(int(os.environ['OPREBOOT'])))

    iterator = ec2.instances.filter(Filters=[{'Name': 'tag:'+tagbusqueda, 'Values': [tagvalor]}])   # Obtiene listado de Instancias con Tag especificado

    dfecha = datetime.datetime.now()
    fecha = dfecha.strftime("%Y%m%d")
    taggeneratedby = 'AutoImageCreator'+ os.environ['AMBIENTE']
    errores=0
    imagenes=0

    for i in iterator:  # Para cada Instancia
        iname='no-name'
        itags=i.tags
        for t in itags: # Obtiene todos los Tags de la Instancia
            if t.get("Key") == 'Name':
                iname=t.get("Value")
        if iname != 'no-name':  # Si la Instancia tiene nombre (NO ES AutoScaling Instance)
            idesc = 'backup-'+iname+"-"+fecha
            try:
                iimage=i.create_image(Description=idesc,Name=idesc,NoReboot=opreboot)   # Genera AMI
                iimage.create_tags(
                    Tags=[
                        {'Key':tagbusqueda,'Value':tagvalor},
                        {'Key':TAGFECHACREACION,'Value':fecha},
                        {'Key':TAGGENERATED,'Value':taggeneratedby},
                        {'Key':TAGID,'Value':iname}
                    ]
                )
                imagenes+=1
                """Inicia proceso de Depuracion"""
                coll_imagenes = ec2.images.filter(Filters=[{'Name': 'tag:'+TAGID, 'Values': [iname]},{'Name': 'tag:'+TAGGENERATED, 'Values': [taggeneratedby]}])    # Obtiene listado de Imagenes autogeneradas para la Instancia
                lista_fechas = []
                for img in coll_imagenes:   # Para cada Imagen obtiene la fecha de creacion y ordena de mas viejo a mas nuevo
                    lista_fechas = lista_fechas + [(img.name).split('-')[-1]]
                lista_fechas.sort()
                cantidad_imagenes = len(lista_fechas)
                if cantidad_imagenes > historico:   # Si hay mas Imagenes que las definidas en Historico
                    c = 0
                    n = cantidad_imagenes - historico
                    while c < n :   # Elimina Imagenes hasta que haya el numero definido en Historico
                        imagen_eliminada = ec2.images.filter(Filters=[{'Name': 'tag:'+TAGFECHACREACION, 'Values': [lista_fechas[c]]},{'Name': 'tag:'+TAGGENERATED, 'Values': [taggeneratedby]}])    # Obtiene AMI a eliminar
                        for ami in imagen_eliminada:
                            ami.deregister()    # Elimina AMI
                        c+=1
            except:
                print("Error en Procesado de Instancia: "+iname)
                errores+=1

    return {
        'statusCode': 200,
        'body': json.dumps('Ejecucion Completada, Imagenes Creadas: '+str(imagenes)+' con '+str(errores)+' Errores.')
    }
