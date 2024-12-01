import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_cines = dynamodb.Table('t_cines')
    t_usuarios = dynamodb.Table('t_usuarios')

    # Obtener el cuerpo del evento y decodificarlo si es un string
    body = event.get('body')
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON in body'})
            }

    # Obtener user_id y cinema_id del body
    user_id = body.get('user_id')
    cinema_id = body.get('cinema_id')
    cinema_name = body.get('cinema_name')

    # Validar campos requeridos
    if not user_id or not cinema_id or not cinema_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id, cinema_id and cinema_name are required'})
        }

    # Consultar el rol del usuario
    try:
        user_response = t_usuarios.get_item(
            Key={
                'cinema_id': cinema_id,
                'user_id': user_id
            }
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error querying user data: {str(e)}'})
        }

    if 'Item' not in user_response or 'role' not in user_response['Item']:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'User not found or role not defined'})
        }

    role = user_response['Item']['role']
    if role != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permission denied'})
        }

    # Verificar si el cine existe
    try:
        existing_cinema = t_cines.get_item(
            Key={
                'cinema_id': cinema_id,
                'cinema_name': cinema_name
            }
        )
        if 'Item' not in existing_cinema:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Cinema not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error checking cinema existence: {str(e)}'})
        }

    # Obtener campos actualizables
    address = body.get('address')
    number_of_halls = body.get('number_of_halls')

    # Construir expresión de actualización
    update_expression = "SET "
    expression_values = {}
    
    if address:
        update_expression += "address = :address, "
        expression_values[':address'] = address
    
    if number_of_halls:
        update_expression += "number_of_halls = :number_of_halls, "
        expression_values[':number_of_halls'] = number_of_halls

    # Verificar si hay algo que actualizar
    if not expression_values:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No fields to update'})
        }

    # Remover la última coma y espacio
    update_expression = update_expression.rstrip(', ')

    # Ejecutar la actualización
    try:
        t_cines.update_item(
            Key={
                'cinema_id': cinema_id,
                'cinema_name': cinema_name
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error updating cinema: {str(e)}'})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Cinema updated successfully'})
    }