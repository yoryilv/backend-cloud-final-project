import boto3
import hashlib
import uuid
import json
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Debug prints para ver qué está llegando
        print("Evento completo:", event)
        print("Tipo de evento:", type(event))
        
        # Si el evento viene de API Gateway, estará en el body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
            
        print("Body procesado:", body)  # Ver el body después de procesarlo
        print("Tipo de body:", type(body))
        
        # Verificar si cinema_id existe y su valor
        print("cinema_id en body:", body.get('cinema_id'))
        
        # Entrada (json)
        cinema_id = body['cinema_id']
        print("cinema_id extraído:", cinema_id)  # Verificar el valor extraído
        user_id = body['user_id']
        password = body['password']
        
        hashed_password = hash_password(password)
        
        # Proceso
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_usuarios')
        
        response = table.get_item(
            Key={
                'cinema_id': cinema_id,
                'user_id': user_id
            }
        )

        if 'Item' not in response:
            return {
                'statusCode': 403,
                'body': 'Usuario no existe'
            }
        
        hashed_password_bd = response['Item']['password']
        
        if hashed_password == hashed_password_bd:
            # Genera token
            token_id = str(uuid.uuid4())
            
            return {
                'statusCode': 200,
                'token_id': token_id
            }
        else:
            return {
                'statusCode': 403,
                'body': 'Password incorrecto'
            }

    except KeyError as e:
        print(f"Error KeyError: {str(e)}")
        print(f"Contenido del body en el momento del error: {body}")
        return {
            'statusCode': 400,
            'body': f'Campo requerido faltante: {str(e)}'
        }
    except Exception as e:
        print(f"Error general: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }