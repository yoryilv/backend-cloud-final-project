import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    try:
        # Obtener cinema_id del evento
        cinema_id = event.get('cinema_id')

        if not cinema_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing cinema_id in the request'})
            }

        # Conectar con DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_cines = dynamodb.Table('t_cines')

        # Consulta usando solo cinema_id
        response = t_cines.query(
            KeyConditionExpression=Key('cinema_id').eq(cinema_id)
        )

        # Verificar si hay resultados
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No hay cines con ese ID'})
            }

        # Responder con los resultados y metadata
        return {
            'statusCode': 200,
            'body': json.dumps({
                'cinema_id': cinema_id,
                'cines': response['Items']
            })
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