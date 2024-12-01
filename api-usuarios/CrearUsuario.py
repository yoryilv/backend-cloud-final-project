import boto3
import hashlib
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Imprimir el evento completo para depuración
        print("Evento recibido:", json.dumps(event))
        
        # Manejar diferentes formatos de entrada
        if isinstance(event, str):
            event = json.loads(event)
        
        # Si event es un diccionario con 'body'
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                body = event['body'] if isinstance(event['body'], dict) else {}
        else:
            body = event

        # Obtener los valores
        cinema_id = body.get('cinema_id')
        user_id = body.get('user_id')
        password = body.get('password')
        role = body.get('role', 'client')
        
        # Depuración de valores extraídos
        print(f"cinema_id: {cinema_id}")
        print(f"user_id: {user_id}")
        print(f"password: {password}")
        print(f"role: {role}")
        
        # Verificación de valores
        if not all([cinema_id, user_id, password]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid request body: missing cinema_id, user_id, or password',
                    'received': {
                        'cinema_id': cinema_id,
                        'user_id': user_id,
                        'password': bool(password),  # solo mostrar si existe
                        'role': role
                    }
                })
            }
        
        # Resto del código permanece igual...
        hashed_password = hash_password(password)
        dynamodb = boto3.resource('dynamodb')
        t_usuarios = dynamodb.Table('t_usuarios')
        
        t_usuarios.put_item(
            Item={
                'cinema_id': cinema_id,
                'user_id': user_id,
                'password': hashed_password,
                'role': role
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User registered successfully',
                'user_id': user_id
            })
        }

    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }