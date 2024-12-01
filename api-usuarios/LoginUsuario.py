import boto3
import hashlib
import uuid
from datetime import datetime, timedelta
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Manejar diferentes formatos de entrada
        if isinstance(event, str):
            event = json.loads(event)
        
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except (json.JSONDecodeError, TypeError):
                body = event['body'] if isinstance(event['body'], dict) else event
        else:
            body = event

        # Obtener credenciales
        cinema_id = body.get('cinema_id')
        user_id = body.get('user_id')
        password = body.get('password')

        # Validar datos necesarios
        if not user_id or not password or not cinema_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required fields (user_id, password, cinema_id)'
                })
            }

        # Hashear password
        hashed_password = hash_password(password)

        # Conectar a DynamoDB
        dynamodb = boto3.resource('dynamodb')
        users_table = dynamodb.Table('t_usuarios')

        # Buscar usuario
        response = users_table.get_item(
            Key={
                'cinema_id': cinema_id,
                'user_id': user_id
            }
        )

        # Verificar si existe el usuario
        if 'Item' not in response:
            return {
                'statusCode': 403,
                'body': json.dumps({
                    'error': 'Usuario no existe'
                })
            }

        # Verificar password
        stored_password = response['Item']['password']
        if hashed_password != stored_password:
            return {
                'statusCode': 403,
                'body': json.dumps({
                    'error': 'Password incorrecto'
                })
            }

        # Generar token y fecha de expiración
        token = str(uuid.uuid4())
        expiration_date = datetime.now() + timedelta(minutes=60)

        # Crear registro de token
        token_record = {
            'token': token,
            'cinema_id': cinema_id,
            'user_id': user_id,
            'role': response['Item'].get('role', 'client'),
            'expires': expiration_date.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Guardar token en DynamoDB
        tokens_table = dynamodb.Table('t_tokens_acceso')
        tokens_table.put_item(Item=token_record)

        # Respuesta exitosa
        return {
            'statusCode': 200,
            'body': json.dumps({
                'token': token,
                'expires': expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': user_id,
                'role': response['Item'].get('role', 'client')
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)
            })
        }