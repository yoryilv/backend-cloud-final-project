const AWS = require('aws-sdk');
const PDFDocument = require('pdfkit');
const s3 = new AWS.S3();

exports.descargarRecibo = async (event) => {
    try {
        const { user_id, purchase_id } = JSON.parse(event.body);

        if (!user_id || !purchase_id) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'El user_id y purchase_id son obligatorios.' }),
            };
        }

        // Simular datos del recibo
        const receiptData = {
            user_id,
            purchase_id,
            cinema: "Cinepolis San Miguel",
            movie: "Inception",
            showtime: "2024-12-01 18:30",
            seats: ["A1", "A2"],
            total: 30.0,
        };

        const doc = new PDFDocument();
        const chunks = [];
        doc.on('data', (chunk) => chunks.push(chunk));
        doc.on('end', async () => {
            const pdfBuffer = Buffer.concat(chunks);

            const uploadResponse = await s3
                .putObject({
                    Bucket: process.env.S3_BUCKET_NAME,
                    Key: `receipts/${purchase_id}.pdf`,
                    Body: pdfBuffer,
                    ContentType: 'application/pdf',
                })
                .promise();

            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Recibo generado exitosamente',
                    url: `https://${process.env.S3_BUCKET_NAME}.s3.amazonaws.com/receipts/${purchase_id}.pdf`,
                }),
            };
        });

        // Crear el contenido del PDF
        doc.fontSize(18).text("Recibo de Compra", { align: "center" });
        doc.moveDown();
        doc.fontSize(12).text(`Usuario: ${receiptData.user_id}`);
        doc.text(`Compra ID: ${receiptData.purchase_id}`);
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
