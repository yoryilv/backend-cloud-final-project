import boto3
import hashlib
import uuid
from datetime import datetime, timedelta

# Hashear contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Obtener credenciales
        cinema_id = event.get('cinema_id')
        user_id = event.get('user_id')
        password = event.get('password')
        
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
        else:
            hashed_password_bd = response['Item']['password']
            
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
        return {
            'statusCode': 500,
            'body': str(e)
        }