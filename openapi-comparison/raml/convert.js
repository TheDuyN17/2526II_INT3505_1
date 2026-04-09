const { Converter, Formats } = require('oas-raml-converter');
const fs = require('fs');
const path = require('path');

async function run() {
    try {
        const converter = new Converter(Formats.RAML, Formats.OAS30);
        const filePath = path.join(__dirname, 'library_api.raml');
        const outputPath = path.join(__dirname, 'openapi.json');

        console.log('Converting RAML to OpenAPI 3.0...');
        const openapi = await converter.convertFile(filePath);
        fs.writeFileSync(outputPath, openapi);
        console.log('Successfully converted RAML to OpenAPI 3.0');
    } catch (err) {
        console.error('Error during conversion:', err);
        process.exit(1);
    }
}

run();
