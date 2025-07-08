import React, { Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Footer from './../../components/Footer/Footer';
import NavBar from './../../components/NavBar/NavBar';
import TopScroller from '../../components/TopScroller/TopScroller';
import Home from '../Home/Home';

const RecommendationsPage = React.lazy(
    () => import('../RecommendationsPage/RecommendationsPage'),
);
const Pagination = React.lazy(() => import('../Pagination/Pagination'));
const AnimeDetails = React.lazy(() => import('../AnimeDetails/AnimeDetails'));
const TopAnimePage = React.lazy(() => import('../TopAnimePage/TopAnimePage'));
const SearchAnime = React.lazy(() => import('../SearchAnime/SearchAnime'));
const GenresPage = React.lazy(() => import('../GenresPage/GenresPage'));
const LicensorsPage = React.lazy(
    () => import('../LicensorsPage/LicensorsPage'),
);
const ProducersPage = React.lazy(
    () => import('../ProducersPage/ProducersPage'),
);
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
                    <Route element={<Home />} path="/" />
                    <Route element={<AnimeDetails />} path="anime/:id" />
                    <Route element={<TopAnimePage />} path="anime/top" />
                    <Route element={<SearchAnime />} path="anime/search" />
                    <Route element={<GenresPage />} path="anime/genres" />
                    <Route element={<Pagination />} path="anime/genres/:id" />
                    <Route element={<GenresPage />} path="anime/demographics" />
                    <Route
                        element={<Pagination />}
                        path="anime/demographics/:id"
                    />
                    <Route element={<GenresPage />} path="anime/themes" />
                    <Route element={<Pagination />} path="anime/themes/:id" />
                    <Route element={<LicensorsPage />} path="anime/licensors" />
                    <Route
                        element={<Pagination />}
                        path="anime/licensors/:id"
                    />
                    <Route element={<ProducersPage />} path="anime/producers" />
                    <Route
                        element={<Pagination />}
                        path="anime/producers/:id"
                    />
                    <Route element={<StudiosPage />} path="anime/studios" />
                    <Route element={<Pagination />} path="anime/studios/:id" />
                    <Route element={<SeasonsPage />} path="anime/seasons" />
                    <Route element={<Pagination />} path="anime/seasons/:id" />
                    <Route
                        element={<RecommendationsPage />}
                        path="anime/recommendations/:id"
                    />
                </Routes>
            </Suspense>
            <Footer />
        </BrowserRouter>
    );
}

export default Router;
