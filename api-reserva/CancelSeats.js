module.exports.cancelarReservaDeAsientos = async (event) => {
    const { show_id, seats } = JSON.parse(event.body);
  
    const params = {
      TableName: process.env.TABLE_NAME_FUNCIONES,
      Key: {
        show_id: show_id,
      },
      UpdateExpression: 'REMOVE seats :seats',
      ExpressionAttributeValues: {
        ':seats': seats,
      },
    };
  
    try {
      await dynamoDB.update(params).promise();
      return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Reservation cancelled successfully' }),
      };
    } catch (error) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Could not cancel reservation' }),
      };
    }
  };
  