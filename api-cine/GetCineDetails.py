import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    try:
        # Obtener cinema_id y district desde la solicitud
        cinema_id = event.get('cinema_id')
        district = event.get('district')
        if not cinema_id or not district:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing cinema_id or district in the request'})
            }

        # Conectar con DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_cines = dynamodb.Table('t_cines')

        # Consulta en la tabla principal con cinema_id y district como claves
        response = t_cines.query(
            KeyConditionExpression=Key('cinema_id').eq(cinema_id) & Key('district').eq(district)
        )

        # Verificar si hay resultados
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No hay cines en este distrito'})
            }

        # Responder con los detalles del cine específico
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'])
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
