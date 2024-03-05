import fs from 'fs';
import { initializeDataFile } from './utils.js';
import { lemmatizer } from 'lemmatizer';
import natural from 'natural';
import { readJSONFile } from '../dataAccess/readFile.js';
import sw from 'remove-stopwords';
import wordList from 'word-list';

const tfidf = new natural.TfIdf();
const wordArray = fs.readFileSync(wordList, 'utf8').split('\n');
const AggressiveTokenizer = natural.AggressiveTokenizer;
const tokenizer = new AggressiveTokenizer();

function cleanSynopsis(synopsis, keywords) {
    const splitSynopsis = synopsis.includes('\n') ? synopsis.split('\n') : synopsis.split(' ');
    const filteredSynopsis = splitSynopsis
        .filter((text) => text !== '' && !text.includes('Source:') && !text.includes('Written by MAL Rewrite'))
        .join(' ');
    let tokens = tokenizer.tokenize(filteredSynopsis);
    tokens = tokens.map((token) => token.toLowerCase());
    tokens = tokens.filter((token) => keywords.includes(token));
    tokens = sw.removeStopwords(tokens, 'en');

    const synopsistfIDF = new natural.TfIdf();
    synopsistfIDF.addDocument(tokens.join(' '));
    const terms = synopsistfIDF.listTerms(0);

    let topTerms = terms
        .sort((a, b) => b.tfidf - a.tfidf)
        .map((term) => term.term);
    return topTerms.join(' ');
}


async function constructTFIDF(data, keywords) {
    data.forEach((entry) => {
        const cleanedSynopsis = cleanSynopsis(entry.synopsis, keywords);
        tfidf.addDocument(cleanedSynopsis);
    });
    return tfidf;
}

function returnTopTerms() {
    const topTerms = new Map();
    for (let i = 0; i < tfidf.documents.length; i++) {
        const terms = tfidf.listTerms(i);
        terms.forEach((term) => {
            const currentScore = topTerms.get(term.term) || 0;
            topTerms.set(term.term, currentScore + term.tfidf);
        });
    }
    const sortedTerms = Array.from(topTerms.entries())
        .sort((a, b) => b[1] - a[1]);
    return sortedTerms;
}

function constructVector(keywords) {
    const normalizedVectors = [];
    for (let i = 0; i < tfidf.documents.length; i++) {
        const terms = tfidf.listTerms(i);
        const vector = [];
        keywords.forEach(keyword => {
            const isKeywordPresent = terms.some(t => t.term === keyword);
            vector.push(isKeywordPresent ? 1 : 0);
        });
        normalizedVectors.push(vector);
    }
    return normalizedVectors;
}


async function normalizeSynopsis(data) {
    const keywords = await readJSONFile('../data/includedKeywords.json');
    await constructTFIDF(data, keywords);
    const vector = constructVector(keywords);
    return vector;
}

export {
    returnTopTerms,
    constructTFIDF,
    cleanSynopsis,
    normalizeSynopsis,
}