const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const body = JSON.parse(event.body); // Parsear el body de la solicitud
        const { user_id, title, cinema_id } = body;

        // Validar entrada
        if (!user_id || !title || !cinema_id) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Faltan campos obligatorios: user_id, title o cinema_id' }),
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

        // Eliminar la película (utilizando cinema_id y title como claves)
        const t_peliculas = process.env.TABLE_NAME_PELICULAS;
        await dynamodb
            .delete({
                TableName: t_peliculas,
                Key: { cinema_id, title },  // Usamos ambas claves
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
            body: JSON.stringify({ error: 'Error interno del servidor', details: error.message }),
        };
    }
};
