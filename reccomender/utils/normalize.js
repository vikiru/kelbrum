function jaccardSimilarity(setA, setB) {
    const intersection = new Set([...setA].filter((x) => setB.has(x)));
    const union = new Set([...setA, ...setB]);
    return intersection.size / union.size;
}

function normalizeGenres(anime, uniqueGenres) {
    const inputGenres = anime.genres;
    return uniqueGenres.map((genre) => (inputGenres.includes(genre) ? 1 : 0));
}

function normalizeOrder(data, property) {
    const orders = data.map((d) => d[property]);
    const orderMapping = {};
    let currentOrder = 1;
    const defaultValue = Math.max(...orders) + 1;
    orders.forEach((order) => {
        if (!orderMapping[order] && order >= 1) {
            orderMapping[order] = currentOrder++;
        } else if (order === 0) {
            orderMapping[order] = defaultValue;
        }
    });
    return data.map((d) => orderMapping[d[property]]);
}

function normalizeStatus(data) {
    const uniqueStatus = returnUniqueArray(data, 'status');
    const normalizedStatus = data.map((entry) => {
        return uniqueStatus.map((status) => (entry.status === status ? 1 : 0));
    });
    return normalizedStatus;
}

function normalizeEpisodes(data) {
    const episodes = data.map((d) => (d.episodes >= 1 ? d.episodes : 0.001));
    const minEpisodes = Math.min(...episodes);
    const maxEpisodes = Math.max(...episodes);
    return episodes.map((ep) => (ep - minEpisodes) / (maxEpisodes - minEpisodes));
}

module.exports = {
    normalizeGenres,
    normalizeOrder,
    normalizeStatus,
    normalizeEpisodes,
    jaccardSimilarity
}