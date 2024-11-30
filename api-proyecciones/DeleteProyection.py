import boto3
import json

def lambda_handler(event, context):
    # Conectar con DynamoDB
    dynamodb = boto3.resource('dynamodb')
    t_proyecciones = dynamodb.Table('${sls:stage}-t_proyecciones')  # Nombre dinámico de la tabla de proyecciones
    t_usuarios = dynamodb.Table('${sls:stage}-t_usuarios')  # Nombre dinámico de la tabla de usuarios

    # Verificar user_id y permisos
    user_id = event.get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id is required'})
        }

    # Consultar rol del usuario
    user_response = t_usuarios.get_item(Key={'user_id': user_id})
    if 'Item' not in user_response or user_response['Item'].get('role') != 'admin':
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Permission denied'})
        }

    # Obtener identificadores clave
    cinema_id = event.get('cinema_id')
    show_id = event.get('show_id')

    # Validar campos obligatorios
    if not cinema_id or not show_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'cinema_id and show_id are required'})
        }

    # Intentar eliminar la función
    try:
        t_proyecciones.delete_item(
            Key={
                'cinema_id': cinema_id,
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
