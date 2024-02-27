import React, { Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { useData } from '../../context/DataProvider';
import AnimeDetails from '../AnimeDetails/AnimeDetails';
import Home from '../Home/Home';
import TopAnimePage from '../TopAnimePage/TopAnimePage';
import Footer from './../../components/Footer/Footer';
import NavBar from './../../components/NavBar/NavBar';

const SearchAnime = React.lazy(() => import('../SearchAnime/SearchAnime'));
const GenresPage = React.lazy(() => import('../GenresPage/GenresPage'));
const LicensorsPage = React.lazy(() => import('../LicensorsPage/LicensorsPage'));
const ProducersPage = React.lazy(() => import('../ProducersPage/ProducersPage'));
const StudiosPage = React.lazy(() => import('../StudiosPage/StudiosPage'));
const SeasonsPage = React.lazy(() => import('../SeasonsPage/SeasonsPage'));

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
                    <Route path="/anime/top" element={<TopAnimePage />} />
                    <Route path="/search" element={<SearchAnime />} />
                    <Route path="/anime/:id" element={<AnimeDetails />} />
                    <Route path="/anime/genres" element={<GenresPage />} />
                    <Route path="/anime/licensors" element={<LicensorsPage />} />
                    <Route path="/anime/producers" element={<ProducersPage />} />
                    <Route path="/anime/studios" element={<StudiosPage />} />
                    <Route path="/anime/seasons" element={<SeasonsPage />} />
                </Routes>
            </Suspense>
            <Footer />
        </BrowserRouter>
    );
}

export default Router;
