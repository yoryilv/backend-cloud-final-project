import boto3
import hashlib
import uuid
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Entrada (json)
        cinema_id = event['cinema_id']  # Usando acceso directo como en tu código original
        user_id = event['user_id']
        password = event['password']
        
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
        print(f"Error: Campo faltante - {str(e)}")
        return {
            'statusCode': 400,
            'body': f'Campo requerido faltante: {str(e)}'
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }