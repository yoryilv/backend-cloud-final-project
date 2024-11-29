module.exports.consultarHorariosPorCineYPelicula = async (event) => {
    const { cinema_id, movie_id, date } = event.queryStringParameters;
  
    const params = {
      TableName: process.env.TABLE_NAME_FUNCIONES, // Tabla de funciones
      KeyConditionExpression: 'cinema_id = :cinema_id and movie_id = :movie_id',
      ExpressionAttributeValues: {
        ':cinema_id': cinema_id,
        ':movie_id': movie_id,
        ':date': date,
      },
    };
  
    try {
      const data = await dynamoDB.query(params).promise();
      const horarios = data.Items.filter(item => item.date === date).map(item => ({
        show_id: item.show_id,
        start_time: item.start_time,
      }));
  
      return {
        statusCode: 200,
        body: JSON.stringify(horarios),
      };
    } catch (error) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Could not retrieve schedules' }),
      };
    }
  };
  