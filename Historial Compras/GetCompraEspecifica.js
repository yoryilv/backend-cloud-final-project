const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.detalleCompra = async (event) => {
    try {
        const { user_id, purchase_id } = JSON.parse(event.body);

        if (!user_id || !purchase_id) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'El user_id y purchase_id son obligatorios.' }),
            };
        }

        const response = await dynamodb
            .get({
                TableName: process.env.TABLE_NAME_COMPRAS,
                Key: { user_id, purchase_id },
            })
            .promise();

        if (!response.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontró la compra especificada.' }),
            };
        }

        return {
            statusCode: 200,
            body: JSON.stringify(response.Item),
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
