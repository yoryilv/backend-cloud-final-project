const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.lambda_handler = async (event) => {
    try {
        // Verifica si el cuerpo está en formato JSON o ya es un objeto
        let body = event.body;
        if (typeof body === 'string') {
            body = JSON.parse(body);
        }

        const { user_id, cinema_id, title } = body;

        // Validar entrada
        const requiredFields = ['user_id', 'cinema_id', 'title'];
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

        // Verificar que existe la película
        const existingMovie = await dynamodb
            .get({
                TableName: process.env.TABLE_NAME_PELICULAS,
                Key: { cinema_id, title },
            })
            .promise();

        if (!existingMovie.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'La película no existe' }),
            };
        }

        // Eliminar la película
        await dynamodb
            .delete({
                TableName: process.env.TABLE_NAME_PELICULAS,
                Key: { cinema_id, title },
            })
            .promise();

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Película eliminada correctamente' }),
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