import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('${sls:stage}-t_cines')
    t_usuarios = dynamodb.Table('${sls:stage}-t_usuarios')
    
    # Obtener user_id
    user_id = event.get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }
    
    user_response = t_usuarios.get_item(Key={'user_id': user_id})
    if 'Item' not in user_response or 'role' not in user_response['Item']:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'User not found or role not defined'})
        }
    
    role = user_response['Item']['role']
    
    # Verificar permisos (solo admin puede crear cines)
    if role != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permiso denegado'})
        }
    
    # Obtener los datos para crear el cine
    cinema_id = event.get('cinema_id')
    name = event.get('name')
    address = event.get('address')
    district = event.get('district')
    number_of_halls = event.get('number_of_halls')
    
    # Validación de entrada
    if not cinema_id or not name or not address or not district:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields'})
        }
    
    # Verificar si el cine ya existe
    existing_cinema = t_cines.get_item(Key={'cinema_id': cinema_id, 'district': district})
    if 'Item' in existing_cinema:
        return {
            'statusCode': 409,
            'body': json.dumps({'error': 'Cinema already exists in this district'})
        }
    
    # Agregar el nuevo cine
    t_cines.put_item(
        Item={
            'cinema_id': cinema_id,
            'name': name,
            'address': address,
            'district': district,
            'number_of_halls': number_of_halls
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Cinema added successfully'})
    }
