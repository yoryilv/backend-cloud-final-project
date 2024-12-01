import boto3
import hashlib
import uuid
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Imprimir el evento para debug
        print("Event recibido:", event)

        # Intentar diferentes maneras de obtener el cinema_id
        if isinstance(event, str):
            data = json.loads(event)
        else:
            data = event

        # Entrada (json)
        cinema_id = data.get('cinema_id')
        user_id = data.get('user_id')
        password = data.get('password')

        print(f"Valores extraídos: cinema_id={cinema_id}, user_id={user_id}, password={password}")

        if not cinema_id or not user_id or not password:
            return {
                'statusCode': 400,
                'body': 'Faltan campos requeridos'
            }
        
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

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }