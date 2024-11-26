const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.handler = async (event) => {
    try {
        const body = JSON.parse(event.body); // Parsear el body de la solicitud
        const { user_id, movie_id, title, genre, duration, rating } = body;

        // Validar entrada
        if (!user_id || !movie_id || !title || !genre || !duration || !rating) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Faltan campos obligatorios' }),
            };
        }

        // Conectar a la tabla de usuarios
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

        // Conectar a la tabla de películas
        const t_peliculas = process.env.TABLE_NAME_PELICULAS;
        const existingMovie = await dynamodb
            .get({
                TableName: t_peliculas,
                Key: { movie_id },
            })
            .promise();

        if (existingMovie.Item) {
            return {
                statusCode: 409,
                body: JSON.stringify({ error: 'La película ya existe' }),
            };
        }

        // Agregar la película
        await dynamodb
            .put({
                TableName: t_peliculas,
                Item: {
                    movie_id,
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
            body: JSON.stringify({ error: 'Error interno del servidor' }),
        };
    }
};
