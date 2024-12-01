import boto3
import hashlib
import json

# Hashear contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función que maneja el registro de user y validación del password
def lambda_handler(event, context):
    try:
        # Obtener el body de la solicitud
        body = json.loads(event.get('body', '{}'))  # Cargar el body JSON

        # Extraer los campos del cuerpo de la solicitud
        cinema_id = body.get('cinema_id')
        user_id = body.get('user_id')
        password = body.get('password')
        role = body.get('role', 'client')

        # Validar campos obligatorios
        required_fields = ['user_id', 'cinema_id', 'password']
        for field in required_fields:
            if not body.get(field):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Falta el campo obligatorio: {field}'})  # Asegúrate de convertir el diccionario a JSON
                }

        # Verificar que el rol sea válido
        valid_roles = ['client', 'admin']
        if role not in valid_roles:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Rol Invalido. Debe ser "client" o "admin"'})
            }

        # Hashea la contraseña antes de almacenarla
        hashed_password = hash_password(password)

        # Conectar DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_usuarios = dynamodb.Table('t_usuarios')

        # Verificar si el usuario ya existe
        existing_user = t_usuarios.get_item(Key={'user_id': user_id})
        if 'Item' in existing_user:
            return {
                'statusCode': 409,
                'body': json.dumps({'error': 'User already exists'})
            }

        # Almacenar los datos del user en la tabla de usuarios en DynamoDB
        t_usuarios.put_item(
            Item={
                'cinema_id': cinema_id,
                'user_id': user_id,
                'password': hashed_password,
                'role': role
            }
        )

        # Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User registered successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
