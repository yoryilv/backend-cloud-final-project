module.exports.consultarDisponibilidadDeAsientos = async (event) => {
    const { show_id } = event.queryStringParameters;
  
    const params = {
      TableName: process.env.TABLE_NAME_FUNCIONES, // Tabla de funciones
      Key: {
        show_id: show_id,
      },
    };
  
    try {
      const data = await dynamoDB.get(params).promise();
      return {
        statusCode: 200,
        body: JSON.stringify(data.Item.seats),
      };
    } catch (error) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Could not retrieve seat availability' }),
      };
    }
  };
  