import React, { Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import TopScroller from '../../components/TopScroller/TopScroller';
import Home from '../Home/Home';
import Footer from './../../components/Footer/Footer';
import NavBar from './../../components/NavBar/NavBar';

const RecommendationsPage = React.lazy(() => import('../RecommendationsPage/RecommendationsPage'));
const Pagination = React.lazy(() => import('../Pagination/Pagination'));
const AnimeDetails = React.lazy(() => import('../AnimeDetails/AnimeDetails'));
const TopAnimePage = React.lazy(() => import('../TopAnimePage/TopAnimePage'));
const SearchAnime = React.lazy(() => import('../SearchAnime/SearchAnime'));
const GenresPage = React.lazy(() => import('../GenresPage/GenresPage'));
const LicensorsPage = React.lazy(() => import('../LicensorsPage/LicensorsPage'));
const ProducersPage = React.lazy(() => import('../ProducersPage/ProducersPage'));
const StudiosPage = React.lazy(() => import('../StudiosPage/StudiosPage'));
const SeasonsPage = React.lazy(() => import('../SeasonsPage/SeasonsPage'));

function Router() {
    return (
        <BrowserRouter basename="/">
            <TopScroller />
            <NavBar />
            <Suspense
                fallback={
                    <div className="flex min-h-screen items-center justify-center">
                        <div className="loading loading-lg text-secondary dark:bg-gray-900 dark:text-primary" />
                    </div>
                }
            >
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="anime/:id" element={<AnimeDetails />} />
                    <Route path="anime/top" element={<TopAnimePage />} />
                    <Route path="anime/search" element={<SearchAnime />} />
                    <Route path="anime/genres" element={<GenresPage />} />
                    <Route path="anime/genres/:id" element={<Pagination />} />
                    <Route path="anime/demographics" element={<GenresPage />} />
                    <Route path="anime/demographics/:id" element={<Pagination />} />
                    <Route path="anime/themes" element={<GenresPage />} />
                    <Route path="anime/themes/:id" element={<Pagination />} />
                    <Route path="anime/licensors" element={<LicensorsPage />} />
                    <Route path="anime/licensors/:id" element={<Pagination />} />
                    <Route path="anime/producers" element={<ProducersPage />} />
                    <Route path="anime/producers/:id" element={<Pagination />} />
                    <Route path="anime/studios" element={<StudiosPage />} />
                    <Route path="anime/studios/:id" element={<Pagination />} />
                    <Route path="anime/seasons" element={<SeasonsPage />} />
                    <Route path="anime/seasons/:id" element={<Pagination />} />
                    <Route path="anime/recommendations/:id" element={<RecommendationsPage />} />
                </Routes>
            </Suspense>
            <Footer />
        </BrowserRouter>
    );
}

export default Router;
