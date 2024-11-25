const AWS = require('aws-sdk');
const dynamoDB = new AWS.DynamoDB.DocumentClient();

module.exports.listarPeliculas = async () => {
  const params = {
    TableName: process.env.TABLE_NAME_PELICULAS, // Tabla que contiene las películas en cartelera
  };

  try {
    const data = await dynamoDB.scan(params).promise();
    const peliculas = data.Items.map(pelicula => ({
      title: pelicula.title,
      genre: pelicula.genre,
      rating: pelicula.rating,
    }));

    return {
      statusCode: 200,
      body: JSON.stringify(peliculas),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Could not retrieve movies' }),
    };
  }
};
