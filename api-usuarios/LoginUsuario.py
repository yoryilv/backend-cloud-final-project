import boto3
import hashlib
import uuid
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Entrada (json)
        user_id = event.get('user_id')
        password = event.get('password')

        if not user_id or not password:
            return {
                'statusCode': 400,
                'body': 'Faltan campos requeridos (user_id, password)'
            }

        hashed_password = hash_password(password)
        
        # Proceso
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_usuarios')

        # Buscar usuario usando scan con filtro
        response = table.scan(
            FilterExpression=Key('user_id').eq(user_id)
        )
        
        # Verificar si se encontró el usuario
        if not response['Items']:
            return {
                'statusCode': 403,
                'body': 'Usuario no existe'
            }

        # Obtener el primer (y debería ser único) usuario encontrado
        user = response['Items'][0]
        hashed_password_bd = user['password']
        
        if hashed_password == hashed_password_bd:
            # Genera token
            token = str(uuid.uuid4())
            return {
                'statusCode': 200,
                'token': token
            }
        else:
            return {
                'statusCode': 403,
                'body': 'Password incorrecto'
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }