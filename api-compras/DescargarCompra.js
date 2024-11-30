const AWS = require('aws-sdk');
const PDFDocument = require('pdfkit');
const s3 = new AWS.S3();
const dynamodb = new AWS.DynamoDB.DocumentClient(); // Cliente de DynamoDB

exports.descargarRecibo = async (event) => {
    try {
        const { user_id, compra_id } = JSON.parse(event.body);

        if (!user_id || !compra_id) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'El user_id y compra_id son obligatorios.' }),
            };
        }

        // Obtener los datos del recibo desde DynamoDB usando el compra_id
        const params = {
            TableName: process.env.TABLE_NAME_COMPRAS,  // Nombre de la tabla de compras de DynamoDB
            Key: {
                'compra_id': compra_id,  // La clave primaria de la tabla es compra_id
            },
        };

        const data = await dynamodb.get(params).promise();

        if (!data.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({ error: 'Compra no encontrada' }),
            };
        }

        // Datos obtenidos de la base de datos
        const receiptData = {
            user_id,
            compra_id,
            cinema: data.Item.cinema,
            movie: data.Item.movie,
            showtime: data.Item.showtime,
            seats: data.Item.seats,
            total: data.Item.total,
        };

        const doc = new PDFDocument();
        const chunks = [];
        doc.on('data', (chunk) => chunks.push(chunk));
        doc.on('end', async () => {
            const pdfBuffer = Buffer.concat(chunks);

            const uploadResponse = await s3
                .putObject({
                    Bucket: process.env.S3_BUCKET_NAME,
                    Key: `receipts/${compra_id}.pdf`,
                    Body: pdfBuffer,
                    ContentType: 'application/pdf',
                })
                .promise();

            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Recibo generado exitosamente',
                    url: `https://${process.env.S3_BUCKET_NAME}.s3.amazonaws.com/receipts/${compra_id}.pdf`,
                }),
            };
        });

        // Crear el contenido del PDF
        doc.fontSize(18).text("Recibo de Compra", { align: "center" });
        doc.moveDown();
        doc.fontSize(12).text(`Usuario: ${receiptData.user_id}`);
        doc.text(`Compra ID: ${receiptData.compra_id}`);
        doc.text(`Cine: ${receiptData.cinema}`);
        doc.text(`Película: ${receiptData.movie}`);
        doc.text(`Horario: ${receiptData.showtime}`);
        doc.text(`Asientos: ${receiptData.seats.join(", ")}`);
        doc.text(`Total: $${receiptData.total}`);
        doc.end();
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
