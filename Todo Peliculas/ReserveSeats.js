module.exports.reservarAsientos = async (event) => {
    const { show_id, seats } = JSON.parse(event.body);
  
    const params = {
      TableName: process.env.TABLE_NAME_FUNCIONES,
      Key: {
        show_id: show_id,
      },
      UpdateExpression: 'SET seats = list_append(seats, :seats)',
      ConditionExpression: 'attribute_not_exists(seats)',
      ExpressionAttributeValues: {
        ':seats': seats,
      },
    };
  
    try {
      await dynamoDB.update(params).promise();
      return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Seats reserved successfully' }),
      };
    } catch (error) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Could not reserve seats' }),
      };
    }
  };
  