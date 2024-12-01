import boto3
import hashlib
import uuid

def hash_password(password):
    if password is None:
        return None
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        # Debug print
        print("Evento recibido:", event)
        
        # Obtener credenciales
        cinema_id = event.get('cinema_id')
        user_id = event.get('user_id')
        password = event.get('password')
        
        # Debug print
        print(f"cinema_id: {cinema_id}")
        print(f"user_id: {user_id}")
        print(f"password: {password}")

        # Verificar cada campo individualmente
        if cinema_id is None:
            print("cinema_id es None")
        if user_id is None:
            print("user_id es None")
        if password is None:
            print("password es None")

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