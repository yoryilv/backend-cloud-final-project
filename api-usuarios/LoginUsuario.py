import boto3
import hashlib
import uuid
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        print("Evento recibido:", event)  # Para debug
        
        # Manejo de diferentes formatos de entrada
        if isinstance(event.get('body'), str):
            import json
            body = json.loads(event['body'])
        else:
            body = event
            
        # Entrada (json)
        user_id = body.get('user_id')
        password = body.get('password')
        
        if not user_id or not password:
            return {
                'statusCode': 400,
                'body': 'Faltan campos requeridos (user_id, password)'
            }
            
        hashed_password = hash_password(password)
        
        # Proceso
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_usuarios')
        response = table.get_item(
            Key={
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
            token = str(uuid.uuid4())
            fecha_hora_exp = datetime.now() + timedelta(minutes=60)
            registro = {
                'token': token,
                'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S')
            }
            table = dynamodb.Table('t_tokens_acceso')
            dynamodbResponse = table.put_item(Item = registro)
            
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
        print(f"Error: {str(e)}")  # Para debug
        return {
            'statusCode': 500,
            'body': str(e)
        }