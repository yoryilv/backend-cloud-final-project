import boto3
import hashlib
import uuid
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Manejo de diferentes formatos de entrada
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event

        # Entrada (json) con manejo seguro
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
        
        # Primero buscar el cinema_id usando scan
        response_scan = table.scan(
            FilterExpression=Key('user_id').eq(user_id)
        )
        
        if not response_scan['Items']:
            return {
                'statusCode': 403,
                'body': 'Usuario no existe'
            }
        
        # Obtener el cinema_id del resultado
        cinema_id = response_scan['Items'][0]['cinema_id']
        
        # Ahora hacer get_item con la clave compuesta completa
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
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }