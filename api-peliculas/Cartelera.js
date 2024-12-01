const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    try {
        // Verifica si el cuerpo está en formato JSON o ya es un objeto
        let body = event.body;
        if (typeof body === 'string') {
            body = JSON.parse(body);
        }

        const { cinema_id } = body;

        // Validar entrada
        if (!cinema_id) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Falta el campo obligatorio: cinema_id' }),
            };
        }

        // Consultar todas las películas para el cinema_id
        const params = {
            TableName: process.env.TABLE_NAME_PELICULAS,
            KeyConditionExpression: 'cinema_id = :cinema_id',
            ExpressionAttributeValues: {
                ':cinema_id': cinema_id
            }
        };

        const response = await dynamodb.query(params).promise();

        // Verificar si hay películas
        if (!response.Items || response.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron películas para este cine' })
            };
        }

        // Formatear la lista de películas
        const moviesList = response.Items.map(movie => ({
            cinema_id: movie.cinema_id,
            title: movie.title,
            genre: movie.genre,
            duration: movie.duration,
            rating: movie.rating
        }));

        return {
            statusCode: 200,
            body: JSON.stringify(moviesList)
        };

    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: 'Error interno del servidor',
                details: error.message,
            }),
        };
    }
};