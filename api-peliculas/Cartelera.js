const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        // Obtener el cinema_id desde la solicitud
        const cinema_id = event.pathParameters.cinema_id;  // Obtener cinema_id de los parámetros de la URL
        if (!cinema_id) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Missing cinema_id in the request' })
            };
        }

        // Obtener el nombre dinámico de la tabla de Cartelera
        const tableName = `${process.env.STAGE}-t_cartelera`;  // Usa la variable de entorno STAGE

        // Consultar todas las películas de la cartelera para el cinema_id
        const params = {
            TableName: tableName,
            KeyConditionExpression: 'cinema_id = :cinema_id',
            ExpressionAttributeValues: {
                ':cinema_id': cinema_id
            }
        };

        const response = await dynamodb.query(params).promise();

        // Verificar si hay películas en la cartelera
        if (!response.Items || response.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron películas en esta cartelera del cine' })
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

        // Responder con la lista de películas
        return {
            statusCode: 200,
            body: JSON.stringify(moviesList)
        };

    } catch (error) {
        console.error("Exception:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: 'Internal server error',
                details: error.message
            })
        };
    }
};
