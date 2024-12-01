const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');
const dynamoDB = new AWS.DynamoDB.DocumentClient();

module.exports.reservarAsientos = async (event) => {
    try {
        const { 
            user_id,
            cinema_name,
            show_id,
            seats_reserved
        } = JSON.parse(event.body);

        if (!user_id || !cinema_name || !show_id || !seats_reserved) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Missing required fields' })
            };
        }

        const cinemaParams = {
            TableName: process.env.TABLE_NAME_CINES,
            FilterExpression: 'cinema_name = :cinema_name',
            ExpressionAttributeValues: {
                ':cinema_name': cinema_name
            }
        };

        const cinemaResult = await dynamoDB.scan(cinemaParams).promise();
        
        if (!cinemaResult.Items || cinemaResult.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'Cinema not found' })
            };
        }

        const cinema_id = cinemaResult.Items[0].cinema_id;

        // Verificar disponibilidad en la proyección usando el ShowIdIndex
        const showParams = {
            TableName: process.env.TABLE_NAME_PROYECCIONES,
            IndexName: 'ShowIdIndex',
            KeyConditionExpression: 'cinema_id = :cinema_id AND show_id = :show_id',
            ExpressionAttributeValues: {
                ':cinema_id': cinema_id,
                ':show_id': show_id
            }
        };

        const showResult = await dynamoDB.query(showParams).promise();

        if (!showResult.Items || showResult.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'Show not found' })
            };
        }

        const existingShow = showResult.Items[0];
        const currentSeatsAvailable = existingShow.seats_available || 0;

        if (currentSeatsAvailable < seats_reserved) {
            return {
                statusCode: 400,
                body: JSON.stringify({ 
                    error: 'Not enough seats available',
                    seats_available: currentSeatsAvailable 
                })
            };
        }

        // Crear reservación
        const reservation_id = uuidv4();
        const reservationParams = {
            TableName: process.env.TABLE_NAME_RESERVAS,
            Item: {
                reservation_id,
                user_id,
                cinema_id,
                cinema_name,
                show_id,
                seats_reserved,
                reservation_date: new Date().toISOString(),
                status: 'CONFIRMED',
                show_details: {
                    title: existingShow.title,
                    hall: existingShow.hall,
                    date: existingShow.date,
                    start_time: existingShow.start_time,
                    end_time: existingShow.end_time
                }
            }
        };

        await dynamoDB.put(reservationParams).promise();

        // Actualizar asientos disponibles
        const updateParams = {
            TableName: process.env.TABLE_NAME_PROYECCIONES,
            Key: { 
                cinema_id,
                cinema_name
            },
            UpdateExpression: 'SET seats_available = seats_available - :seats_reserved',
            ConditionExpression: 'seats_available >= :seats_reserved',
            ExpressionAttributeValues: {
                ':seats_reserved': seats_reserved
            },
            ReturnValues: 'ALL_NEW'
        };

        const updatedShow = await dynamoDB.update(updateParams).promise();

        const responseBody = {
            reservation_id,
            user_id,
            cinema_details: {
                cinema_id,
                cinema_name
            },
            show_details: {
                show_id,
                title: existingShow.title,
                hall: existingShow.hall,
                date: existingShow.date,
                start_time: existingShow.start_time,
                end_time: existingShow.end_time
            },
            reservation_details: {
                seats_reserved,
                reservation_date: reservationParams.Item.reservation_date,
                status: 'CONFIRMED'
            },
            seats_available: updatedShow.Attributes.seats_available
        };

        return {
            statusCode: 200,
            body: JSON.stringify(responseBody)
        };

    } catch (error) {
        console.error('Reservation error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ 
                error: 'Internal server error', 
                details: error.message 
            })
        };
    }
};