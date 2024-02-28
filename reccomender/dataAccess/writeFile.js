import path from 'path';
import fs from 'fs/promises';

/**
 * Formats a number to have two decimal places.
 *
 * @param {number} num - The number to be formatted
 * @returns {string} The formatted number as a string
 */
function formatNumber(num) {
    return num.toFixed(2);
}

/**
 * Returns the appropriate file size unit for the given number of bytes.
 *
 * @param {number} bytes - The number of bytes to convert to a file size unit
 * @returns {string} The appropriate file size unit ('B', 'KB', or 'MB')
 */
function getFileSizeUnit(bytes) {
    return bytes < 1024 ? 'B' : bytes < 1048576 ? 'KB' : 'MB';
}

/**
 * Formats the file size in a human-readable format.
 *
 * @param {number} bytes - The size of the file in bytes
 * @returns {string} The formatted file size with unit
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

/**
 * Formats a number to have two decimal places.
 *
 * @param {number} num - The number to be formatted
 * @returns {string} The formatted number as a string
 */
function formatNumber(num) {
    return num.toFixed(2);
}

/**
 * Returns the appropriate file size unit for the given number of bytes.
 *
 * @param {number} bytes - The number of bytes to convert to a file size unit
 * @returns {string} The appropriate file size unit ('B', 'KB', or 'MB')
 */
function getFileSizeUnit(bytes) {
    return bytes < 1024 ? 'B' : bytes < 1048576 ? 'KB' : 'MB';
}

/**
 * Formats the file size in a human-readable format.
 *
 * @param {number} bytes - The size of the file in bytes
 * @returns {string} The formatted file size with unit
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
