import React, { useState } from 'react';
import StarRatings from 'react-rating-stars-component';
import { Link } from 'react-router-dom';
import { ReactSearchAutocomplete } from 'react-search-autocomplete';

import './App.css';
import AnimeCard from './components/AnimeCard/AnimeCard';
import NavBar from './components/NavBar/NavBar';
import { useData } from './context/DataProvider';

function normalizeString(str) {
    return str.replace(/[^a-zA-Z0-9\s]/g, ' ');
}

function truncateSynopsis(synopsis) {
    const maxLength = 1024;
    if (synopsis.length > maxLength) {
        return synopsis.substring(0, maxLength) + '...';
    }
    return synopsis;
}

function App() {
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const { data, titleIDMap } = useData();

    const anime = {
        id: 0,
        malID: 35405,
        title: '?/Sankaku no Rhythm/Trump no Arasoi',
        englishName: '?/Rhythmic Triangles/Fighting Cards',
        otherName: '?  三角のリズム  トランプの爭',
        titles: [
            '?/Sankaku no Rhythm/Trump no Arasoi',
            'Question Mark',
            '?  三角のリズム  トランプの爭',
            '?/Rhythmic Triangles/Fighting Cards',
        ],
        score: 4.26,
        genres: ['Avant Garde'],
        themes: [],
        demographics: [],
        synopsis:
            'Four short vignettes in this early animated film. In the first, shadows pull away to reveal a puddle, and automobile and bicycle tires pass through it. In the second, cutout shadows of a variety of shoes of people walking are seen. The third is a flurry of geometric forms. In the fourth, the playing card spade courts the heart and pushes away the club, but eventually the club returns, beats up the spade, and wins the heart. \n\n(Source: AniDB)',
        type: 'Movie',
        episodes: 1,
        aired: '1932',
        premiered: 'Unknown',
        season: 'Unknown',
        year: 1932,
        status: 'Finished Airing',
        producers: [],
        licensors: [],
        studios: [],
        source: 'Original',
        durationText: '4 min',
        durationMinutes: 4,
        rating: 'G',
        rank: 12566,
        popularity: 13347,
        favourites: 0,
        scoredBy: 453,
        members: 806,
        imageURL: 'https://cdn.myanimelist.net/images/anime/2/85267.jpg',
        trailerURL: 'Unknown',
        pageURL: 'https://myanimelist.net/anime/35405/?/Sankaku no Rhythm/Trump no Arasoi',
    };
    const items = titleIDMap.map((item) => ({ id: item.value, name: item.title, synonyms: item.synonyms }));

    const handleOnSearch = (string) => {
        const newSuggestions = items.filter((item) => {
            const itemStr = normalizeString(item.name);
            const stringStr = normalizeString(string);
            const nameMatches = itemStr.includes(stringStr);
            const synonymsMatch = item.synonyms.some((synonym) => normalizeString(synonym).includes(stringStr));
            return nameMatches || synonymsMatch;
        });
        const sortedSuggestions = newSuggestions.sort((a, b) => {
            return a.id - b.id;
        });
        setSuggestions(sortedSuggestions);
    };

    const handleOnSelect = (selectedItem) => {
        setInputValue(selectedItem.name);
        setSuggestions([]);
    };

    const formatResult = (item) => (
        <div className="p-2 hover:bg-gray-200 cursor-pointer">
            <span>{item.name}</span>
        </div>
    );

    return (
        <section id="main">
            <NavBar />
            <div className="p-2 grid xs:grid-cols-1 lg:grid-cols-2 3xl:grid-cols-3 3xl:grid-cols-5 gap-y-2">
                {data
                    .sort((a, b) => b.score - a.score)
                    .slice(0, 100)
                    .map((d) => {
                        return <AnimeCard key={d.title} anime={d} />;
                    })}
            </div>

            <div className="container min-h-screen flex-grow">
                <div className="min-h-[20rem] flex-shrink-0">
                    <ReactSearchAutocomplete
                        items={items}
                        onSearch={handleOnSearch}
                        onSelect={handleOnSelect}
                        formatResult={formatResult}
                        maxResults={6}
                        placeholder="Type to filter titles..."
                        className="w-full p-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                        autocompleteItemClassName="p-2 hover:bg-gray-200 cursor-pointer"
                        autocompleteItemActiveClassName="bg-blue-500 text-white"
                    />
                </div>
            </div>
        </section>
    );
}

export default App;
