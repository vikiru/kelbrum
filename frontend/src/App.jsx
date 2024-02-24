import './App.css';

import { BrowserRouter, Link } from 'react-router-dom';
import React, { useState } from 'react';

import AnimeCard from './components/AnimeCard/AnimeCard';
import AnimeDetails from './pages/AnimeDetails/AnimeDetails';
import Footer from './components/Footer/Footer';
import Home from './pages/Home/Home';
import NavBar from './components/NavBar/NavBar';
import { ReactSearchAutocomplete } from 'react-search-autocomplete';
import Router from './pages/Router/Router';
import StarRatings from 'react-rating-stars-component';
import TopAnimePage from './pages/TopAnimePage/TopAnimePage';
import { useData } from './context/DataProvider';

function App() {
    const { data } = useData();
    data.sort((a, b) => b.score - a.score);
    return (
        <BrowserRouter>
            <NavBar />
            <Router />
            <Footer />
        </BrowserRouter>
    );
}

export default App;
