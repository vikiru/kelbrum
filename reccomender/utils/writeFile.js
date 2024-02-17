const fs = require('fs').promises;
const path = require('path');

function formatNumber(num) {
    return num.toFixed(2);
}

function getFileSizeUnit(bytes) {
    return bytes <  1024 ? 'B' : bytes <  1048576 ? 'KB' : 'MB';
}

function formatFileSize(bytes) {
    const unit = getFileSizeUnit(bytes);
    const size = unit === 'B' ? bytes : unit === 'KB' ? bytes /  1024 : bytes /  1048576;
    return `${formatNumber(size)} ${unit}`;
}

async function writeData(fileName, data) {
    const filePath = path.resolve(__dirname, `../data/${fileName}`);
    try {
        const dataString = JSON.stringify(data, null);
        await fs.writeFile(filePath, dataString, 'utf8');
        const stats = await fs.stat(filePath);
        const fileSizeInBytes = stats.size;
        console.log(`Data successfully written to ${filePath}. \nFile size: ${formatFileSize(fileSizeInBytes)}`);
    } catch (err) {
        console.error('Error writing file:', err);
        throw err;
    }
}
module.exports = {
    writeData,
};
