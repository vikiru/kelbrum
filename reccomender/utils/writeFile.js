let fs, path, url;

let dirname;
let __filename, __dirname;

if (typeof window === 'undefined') {
    fs = require('fs/promises');
    path = require('path');
    url = require('url');
    dirname = path.dirname;
    __filename = url.fileURLToPath(import.meta.url);
    __dirname = dirname(__filename);
}

/**
 * Formats a number to have two decimal places.
 *
 * @param {number} num - the number to be formatted
 * @return {string} the formatted number as a string
 */
function formatNumber(num) {
    return num.toFixed(2);
}

/**
 * Returns the appropriate file size unit for the given number of bytes.
 *
 * @param {number} bytes - The number of bytes to convert to a file size unit
 * @return {string} The appropriate file size unit ('B', 'KB', or 'MB')
 */
function getFileSizeUnit(bytes) {
    return bytes < 1024 ? 'B' : bytes < 1048576 ? 'KB' : 'MB';
}

/**
 * Formats the file size in a human-readable format.
 *
 * @param {number} bytes - the size of the file in bytes
 * @return {string} the formatted file size with unit
 */
function formatFileSize(bytes) {
    const unit = getFileSizeUnit(bytes);
    const size = unit === 'B' ? bytes : unit === 'KB' ? bytes / 1024 : bytes / 1048576;
    return `${formatNumber(size)} ${unit}`;
}

/**
 * Writes data to a file.
 *
 * @param {string} fileName - The name of the file
 * @param {object} data - The data to be written to the file
 * @returns {Promise<void>} A Promise that resolves when the data is successfully written
 */
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
export { writeData };
