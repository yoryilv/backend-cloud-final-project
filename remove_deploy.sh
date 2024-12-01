#!/bin/bash

echo "Eliminando servicio general"
sls remove --stage prod --region us-east-1

# Lista de directorios donde están los proyectos Serverless
services=("api-cine" "api-peliculas" "api-proyecciones" "api-reserva" "api-usuarios" "api-visitas")

# Recorrer cada directorio y ejecutar el remove
for service in "${services[@]}"
do
    echo "Eliminando servicio: $service"
    
    # Cambiar al directorio del servicio
    cd $service || exit
    
    # Ejecutar el remove con Serverless
    sls remove --stage prod --region us-east-1
    
    # Volver al directorio original
    cd ..
done