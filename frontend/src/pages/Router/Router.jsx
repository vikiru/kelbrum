import React, { Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

import Home from '../Home/Home';
import InfinitePagination from '../InfinitePagination/InfinitePagination';
import Footer from './../../components/Footer/Footer';
import NavBar from './../../components/NavBar/NavBar';

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
                    <Route path="anime">
                        <Route path="top" element={<TopAnimePage />} />
                        <Route path=":id" element={<AnimeDetails />} />
                        <Route path="search" element={<SearchAnime />} />
                        <Route path="genres" element={<GenresPage />}>
                            <Route path=":id" element={<InfinitePagination />} />
                        </Route>
                        <Route path="demographics" element={<GenresPage />}>
                            <Route path=":id" element={<InfinitePagination />} />
                        </Route>
                        <Route path="themes" element={<GenresPage />}>
                            <Route path=":id" element={<InfinitePagination />} />
                        </Route>
                        <Route path="licensors" element={<LicensorsPage />}>
                            <Route path=":id" element={<InfinitePagination />} />
                        </Route>
                        <Route path="producers" element={<ProducersPage />}>
                            <Route path=":id" element={<InfinitePagination />} />
                        </Route>
                        <Route path="studios" element={<StudiosPage />}>
                            <Route path=":id" element={<InfinitePagination />} />
                        </Route>
                        <Route path="seasons" element={<SeasonsPage />}>
                            <Route path=":id" element={<InfinitePagination />} />
                        </Route>
                    </Route>
                </Routes>
            </Suspense>
            <Footer />
        </BrowserRouter>
    );
}

export default Router;
