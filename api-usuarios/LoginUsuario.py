import boto3
import hashlib
import uuid
from datetime import datetime, timedelta

def hash_password(password):
   return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
   try:
       # Obtener credenciales
       cinema_id = event.get('cinema_id') 
       user_id = event.get('user_id')
       password = event.get('password')

       # Validar campos requeridos
       if not all([cinema_id, user_id, password]):
           return {
               'statusCode': 400,
               'body': 'Faltan campos requeridos'
           }

       # Hashear password
       hashed_password = hash_password(password)

       # Buscar usuario
       dynamodb = boto3.resource('dynamodb')
       users_table = dynamodb.Table('t_usuarios')

       response = users_table.get_item(
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

       # Verificar password
       hashed_password_bd = response['Item']['password']
       if hashed_password != hashed_password_bd:
           return {
               'statusCode': 403, 
               'body': 'Password incorrecto'
           }

       # Generar token
       token_id = str(uuid.uuid4())
           
       return {
           'statusCode': 200,
           'token_id': token_id
       }

   except Exception as e:
       print(f"Error: {str(e)}")
       return {
           'statusCode': 500,
           'body': str(e)
       }