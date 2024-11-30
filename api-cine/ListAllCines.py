import boto3
import json

def lambda_handler(event, context):
    try:
        # Conectar con DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_cines = dynamodb.Table('${sls:stage}-t_cines')  # Nombre dinámico de la tabla

        # Escanear la tabla para obtener todos los cines
        response = t_cines.scan()

        # Verificar si hay cines en la respuesta
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No cines encontrados'})
            }

        # Construir la lista de cines con detalles básicos
        cinema_list = []
        for cinema in response['Items']:
            cinema_data = {
                'cinema_id': cinema['cinema_id'],
                'name': cinema['name'],
                'address': cinema['address'],
                'district': cinema['district']
            }
            cinema_list.append(cinema_data)

        # Responder con la lista de cines
        return {
            'statusCode': 200,
            'body': json.dumps(cinema_list)
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
