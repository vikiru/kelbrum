import React, { useState } from 'react';
import { Link } from 'react-router-dom';

import './App.css';
import NavBar from './components/NavBar/NavBar';

function App() {
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);

    const data = ['Naruto', 'One Piece', 'Attack on Titan', 'My Hero Academia'];

    const handleInputChange = (event) => {
        const value = event.target.value;
        setInputValue(value);

        if (value === '') {
            setSuggestions([]);
        } else {
            const filteredSuggestions = data
                .filter((item) => item.toLowerCase().includes(value.toLowerCase()))
                .slice(0, 5);

            setSuggestions(filteredSuggestions);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setInputValue(suggestion); // Update the input value with the selected suggestion
        setSuggestions([]); // Clear the suggestions list
    };

    return (
        <section id="main">
            <label className="input input-bordered flex items-center gap-2">
                <input
                    type="text"
                    className="grow"
                    placeholder="Enter an anime title"
                    value={inputValue}
                    onChange={handleInputChange}
                />
            </label>
            {suggestions.length > 0 && (
                <ul className="w-full absolute">
                    {suggestions.map((suggestion, index) => (
                        <li
                            key={index}
                            className="list-none bg-white hover:bg-gray-200 p-2"
                            onClick={() => handleSuggestionClick(suggestion)}
                        >
                            {suggestion}
                        </li>
                    ))}
                </ul>
            )}
        </section>
    );
}

export default App;
