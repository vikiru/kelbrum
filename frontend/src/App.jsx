import './App.css';

import React, { useState } from 'react';

import AnimeCard from './components/AnimeCard/AnimeCard';
import Footer from './components/Footer/Footer';
import Home from './pages/Home/Home';
import { Link } from 'react-router-dom';
import NavBar from './components/NavBar/NavBar';
import { ReactSearchAutocomplete } from 'react-search-autocomplete';
import StarRatings from 'react-rating-stars-component';
import { useData } from './context/DataProvider';

function App() {
    return (
        <section id="main">
            <NavBar />
            <Home />
            <Footer />
        </section>
    );
}

export default App;
