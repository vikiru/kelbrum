import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ReactSearchAutocomplete } from 'react-search-autocomplete';
import ReactSearchBox from 'react-search-box';

import './App.css';
import NavBar from './components/NavBar/NavBar';
import { useData } from './context/DataProvider';

function normalizeString(str) {
    return str.replace(/[^a-zA-Z0-9\s]/g, ' ');
}

function App() {
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const { titleIDMap } = useData();

    const items = titleIDMap.map((item) => ({ id: item.value, name: item.title }));

    const handleOnSearch = (selectedItem) => {
        setInputValue(selectedItem.name);
        console.log(selectedItem);
        setSuggestions([]);
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
            <div className="hero min-h-screen">
                <div className="hero-overlay bg-opacity-60"></div>
                <div className="hero-content text-center text-neutral-content">
                    <div className="max-w-md">
                        <h1 className="text-5xl font-bold">Placeholder</h1>
                        <p>Placeholder text.</p>
                    </div>
                </div>
            </div>
            <div className="container">
                <ReactSearchAutocomplete
                    items={items}
                    onSearch={handleOnSearch}
                    onSelect={handleOnSelect}
                    formatResult={formatResult}
                    maxResults={10}
                    placeholder="Type to filter titles..."
                    className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
                    autocompleteItemClassName="p-2 hover:bg-gray-200 cursor-pointer"
                    autocompleteItemActiveClassName="bg-blue-500 text-white"
                />
            </div>
        </section>
    );
}

export default App;
