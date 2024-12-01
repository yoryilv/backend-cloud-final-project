const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    try {
        // Verifica si el cuerpo está en formato JSON o ya es un objeto
        let body = event.body;
        if (typeof body === 'string') {
            body = JSON.parse(body);
        }

        const { user_id, cinema_id, title, genre, duration, rating } = body;

        // Validar entrada
        const requiredFields = ['user_id', 'cinema_id', 'title', 'genre', 'duration', 'rating'];
        for (let field of requiredFields) {
            if (!body[field]) {
                return {
                    statusCode: 400,
                    body: JSON.stringify({ error: `Falta el campo obligatorio: ${field}` }),
                };
            }
        }

        // Verificar permisos del usuario
        const userResponse = await dynamodb
            .get({
                TableName: process.env.TABLE_NAME_USUARIOS,
                Key: { 
                    cinema_id,
                    user_id
                },
            })
            .promise();

        if (!userResponse.Item || userResponse.Item.role !== 'admin') {
            return {
                statusCode: 403,
                body: JSON.stringify({ error: 'Permiso denegado: el usuario no tiene acceso como admin' }),
            };
        }

        // Verificar si la película ya existe
        const existingMovie = await dynamodb
            .get({
                TableName: process.env.TABLE_NAME_PELICULAS,
                Key: { cinema_id, title },
            })
            .promise();

        if (existingMovie.Item) {
            return {
                statusCode: 409,
                body: JSON.stringify({ error: 'La película ya existe' }),
            };
        }

        // Agregar la nueva película
        await dynamodb
            .put({
                TableName: process.env.TABLE_NAME_PELICULAS,
                Item: {
                    cinema_id,
                    title,
                    genre,
                    duration,
                    rating,
                },
            })
            .promise();

        return {
            statusCode: 201,
            body: JSON.stringify({ message: 'Película agregada correctamente' }),
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