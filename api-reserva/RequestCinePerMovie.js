module.exports.consultarCinesPorPelicula = async (event) => {
    const { movie_id } = event.queryStringParameters;
  
    const params = {
      TableName: process.env.TABLE_NAME_CARTELERA, // Tabla de cartelera con cines y películas
      IndexName: 'movie-index', // GSI en la tabla de cartelera para consultar por movie_id
      KeyConditionExpression: 'movie_id = :movie_id',
      ExpressionAttributeValues: {
        ':movie_id': movie_id,
      },
    };
  
    try {
      const data = await dynamoDB.query(params).promise();
      const cines = data.Items.map(item => item.cinema_id);
  
      return {
        statusCode: 200,
        body: JSON.stringify(cines),
      };
    } catch (error) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Could not retrieve cinemas' }),
      };
    }
  };
  