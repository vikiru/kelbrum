import React, { Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { useData } from '../../context/DataProvider';
import AnimeDetails from '../AnimeDetails/AnimeDetails';
import GenresPage from '../GenresPage/GenresPage';
import Home from '../Home/Home';
import SearchAnime from '../SearchAnime/SearchAnime';
import TopAnimePage from '../TopAnimePage/TopAnimePage';
import Footer from './../../components/Footer/Footer';
import NavBar from './../../components/NavBar/NavBar';
import LicensorsPage from './../LicensorsPage/LicensorsPage';
import ProducersPage from './../ProducersPage/ProducersPage';
import SeasonsPage from './../SeasonsPage/SeasonsPage';
import StudiosPage from './../StudiosPage/StudiosPage';

function Router() {
    return (
        <BrowserRouter>
            <NavBar />
            <Suspense
                fallback={
                    <div className="flex h-screen items-center justify-center">
                        <div className="spinner spinner-lg text-primary" />
                    </div>
                }
            >
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/topAnime" element={<TopAnimePage />} />
                    <Route path="/search" element={<SearchAnime />} />
                    <Route path="/anime/:id" element={<AnimeDetails />} />
                    <Route path="/anime/licensors" element={<LicensorsPage />} />
                    <Route path="/anime/producers" element={<ProducersPage />} />
                    <Route path="/anime/studios" element={<StudiosPage />} />
                    <Route path="/anime/seasons" element={<SeasonsPage />} />
                    <Route path="/anime/genres" element={<GenresPage />} />
                </Routes>
            </Suspense>
            <Footer />
        </BrowserRouter>
    );
}

export default Router;
