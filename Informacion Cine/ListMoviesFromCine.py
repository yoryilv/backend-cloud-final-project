import boto3
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    try:
        # Obtener el cinema_id desde la solicitud
        cinema_id = event.get('cinema_id')
        if not cinema_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing cinema_id in the request'})
            }

        # Conectar con DynamoDB
        dynamodb = boto3.resource('dynamodb')
        t_cartelera = dynamodb.Table('t_cartelera')  # Nombre de la tabla de cartelera en DynamoDB

        # Consultar todas las películas de la cartelera para el cine específico
        response = t_cartelera.query(
            KeyConditionExpression=Key('cinema_id').eq(cinema_id)
        )

        # Verificar si hay películas en la cartelera
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No se encontraron películas en esta cartelera del cine'})
            }

        # Formatear la lista de películas
        movies_list = []
        for movie in response['Items']:
            movie_data = {
                'movie_id': movie['movie_id'],
                'title': movie['title'],
                'genre': movie['genre'],
                'duration': movie['duration'],
                'rating': movie['rating']
            }
            movies_list.append(movie_data)

        # Responder con la lista de películas
        return {
            'statusCode': 200,
            'body': json.dumps(movies_list)
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