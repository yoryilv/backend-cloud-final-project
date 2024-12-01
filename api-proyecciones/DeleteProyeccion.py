import boto3
import json

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    t_proyecciones = dynamodb.Table('t_proyecciones')
    t_usuarios = dynamodb.Table('t_usuarios')
    t_cines = dynamodb.Table('t_cines')

    # Verificar user_id y permisos
    user_id = event.get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }

    try:
        # Consultar rol del usuario
        user_response = t_usuarios.get_item(Key={'user_id': user_id})
        if 'Item' not in user_response or user_response['Item'].get('role') != 'admin':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Permission denied'})
            }

        # Obtener identificadores clave
        cinema_id = event.get('cinema_id')
        cinema_name = event.get('cinema_name')
        show_id = event.get('show_id')

        # Validar campos obligatorios
        if not cinema_id or not cinema_name or not show_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'cinema_id, cinema_name, and show_id are required'})
            }

        # Verificar si el cine existe
        cinema_response = t_cines.get_item(Key={'cinema_id': cinema_id, 'cinema_name': cinema_name})
        if 'Item' not in cinema_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Cinema not found'})
            }

        # Intentar eliminar la función
        t_proyecciones.delete_item(
            Key={
                'cinema_id': cinema_id,
                'cinema_name': cinema_name,
                'show_id': show_id
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Function deleted successfully'})
        }

    except Exception as e:
        print("Exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
