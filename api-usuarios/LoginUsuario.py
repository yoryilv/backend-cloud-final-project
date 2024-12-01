import boto3
import hashlib
import json

# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
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
            except (json.JSONDecodeError, TypeError):
                body = event['body'] if isinstance(event['body'], dict) else event
        else:
            body = event

        # Obtener los valores
        cinema_id = body.get('cinema_id')
        user_id = body.get('user_id')
        password = body.get('password')

        # Imprimir para depuración
        print(f"Valores extraídos:")
        print(f"cinema_id: {cinema_id}")
        print(f"user_id: {user_id}")
        print(f"password: {password}")
        # Validar que cinema_id, user_id y password estén presentes
        if not cinema_id or not user_id or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing cinema_id, user_id, or password',
                    'received': {
                        'cinema_id': cinema_id,
                        'user_id': user_id,
                        'password': bool(password)
                    }
                })
            }

        # Hashear la contraseña antes de almacenarla
        hashed_password = hash_password(password)

        # Conectar con DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_usuarios')

        # Verificar si el usuario ya existe en la tabla de usuarios
        try:
            response = table.get_item(
                Key={
                    'cinema_id': cinema_id,  # partition key
                    'user_id': user_id       # sort key
                }
            )

            if 'Item' in response:
                return {
                    'statusCode': 409,
                    'body': json.dumps({
                        'error': 'User already exists',
                        'user_id': user_id,
                        'cinema_id': cinema_id
                    })
                }

        except Exception as check_error:
            print(f"Error checking existing user: {check_error}")
            # Si hay un error al verificar, continuamos con el registro

        # Almacenar los datos del usuario en la tabla de DynamoDB
        try:
            table.put_item(
                Item={
                    'cinema_id': str(cinema_id),
                    'user_id': str(user_id),
                    'password': hashed_password
                }
            )
        except Exception as put_error:
            print(f"Error storing user: {put_error}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Error storing user data',
                    'details': str(put_error)
                })
            }

        # Retornar un mensaje de éxito
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'User registered successfully', 
                'user_id': user_id,
                'cinema_id': cinema_id
            })
        }

    except Exception as e:
        # Manejo de excepciones generales
        print("General Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error', 
                'details': str(e)
            })
        }