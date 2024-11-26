const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

exports.filtrarCompras = async (event) => {
    try {
        const { user_id, start_date, end_date } = JSON.parse(event.body);

        if (!user_id || !start_date || !end_date) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'El user_id, start_date y end_date son obligatorios.' }),
            };
        }

        const response = await dynamodb
            .query({
                TableName: process.env.TABLE_NAME_COMPRAS,
                KeyConditionExpression: 'user_id = :user_id AND purchase_date BETWEEN :start_date AND :end_date',
                ExpressionAttributeValues: {
                    ':user_id': user_id,
                    ':start_date': start_date,
                    ':end_date': end_date,
                },
            })
            .promise();

        if (!response.Items || response.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'No se encontraron compras en el rango de fechas especificado.' }),
            };
        }

        return {
            statusCode: 200,
            body: JSON.stringify(response.Items),
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
