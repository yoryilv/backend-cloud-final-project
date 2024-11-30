const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const body = JSON.parse(event.body); // Parsear el body de la solicitud
        const { user_id, cinema_id, title, genre, duration, rating } = body;

        // Validar entrada
        if (!user_id || !title) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Faltan campos obligatorios: user_id o title' }),
            };
        }

        // Verificar permisos del usuario
        const t_usuarios = process.env.TABLE_NAME_USUARIOS;
        const userResponse = await dynamodb
            .get({
                TableName: t_usuarios,
                Key: { user_id },
            })
            .promise();

        if (!userResponse.Item || userResponse.Item.role !== 'admin') {
            return {
                statusCode: 403,
                body: JSON.stringify({ error: 'Permiso denegado' }),
            };
        }

        // Construir expresión de actualización
        const updateExpression = [];
        const expressionValues = {};

        if (title) {
            updateExpression.push('title = :title');
            expressionValues[':title'] = title;
        }
        if (genre) {
            updateExpression.push('genre = :genre');
            expressionValues[':genre'] = genre;
        }
        if (duration) {
            updateExpression.push('duration = :duration');
            expressionValues[':duration'] = duration;
        }
        if (rating) {
            updateExpression.push('rating = :rating');
            expressionValues[':rating'] = rating;
        }

        if (updateExpression.length === 0) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'No hay campos para actualizar' }),
            };
        }

        // Actualizar la película
        const t_peliculas = process.env.TABLE_NAME_PELICULAS;
        await dynamodb
            .update({
                TableName: t_peliculas,
                Key: { title },
                UpdateExpression: `SET ${updateExpression.join(', ')}`,
                ExpressionAttributeValues: expressionValues,
            })
            .promise();

        return {
            statusCode: 200,
            body: JSON.stringify({ message: 'Película actualizada correctamente' }),
        };
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Error interno del servidor', details: error.message }),
        };
    }
};
