const fs = require('fs');
const path = require('path');

async function writeFile(fileName, data) {
    const filePath = path.resolve(__dirname, `../data/${fileName}`);
    try {
        const dataString = JSON.stringify(data, null, 2);
        await fs.promises.writeFile(filePath, dataString, 'utf8');
        console.log(`Data successfully written to ${filePath}`);
    } catch (err) {
        console.error('Error writing file:', err);
        throw err;
    }
}

module.exports = {
    writeFile,
};
