import React, { Suspense } from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';

import Footer from './components/Footer/Footer';
import NavBar from './components/NavBar/NavBar';
import DataProvider, { useData } from './context/DataProvider';

const Home = React.lazy(() => import('./pages/Home/Home'));
const SearchAnime = React.lazy(() => import('./pages/SearchAnime/SearchAnime'));
const TopAnimePage = React.lazy(() => import('./pages/TopAnimePage/TopAnimePage'));
const AnimeDetails = React.lazy(() => import('./pages/AnimeDetails/AnimeDetails'));

function App() {
    const { data, featureArray, kmeans, titleIDMap } = useData();
    const sortedData = [...data].sort((a, b) => b.score - a.score);
    const top100Anime = sortedData.slice(0, 100);

    return (
        <DataProvider>
            <Router>
                <NavBar />
                <Suspense
                    fallback={
                        <div className="flex h-screen items-center justify-center">
                            <div className="spinner spinner-lg text-primary"></div>
                        </div>
                    }
                >
                    <Routes>
                        <Route path="/" element={<Home data={data} />} />
                        <Route path="/topAnime" element={<TopAnimePage top100Anime={top100Anime} />} />
                        <Route path="/search" element={<SearchAnime data={data} titleIDMap={titleIDMap} />} />
                        <Route
                            path="/anime/:id"
                            element={<AnimeDetails data={data} kmeans={kmeans} featureArray={featureArray} />}
                        />
                    </Routes>
                </Suspense>
                <Footer />
            </Router>
        </DataProvider>
    );
}

export default App;
