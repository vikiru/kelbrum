import React, { Suspense } from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';

import { useData } from '../../context/DataProvider';

const AnimeDetails = React.lazy(() => import('../AnimeDetails/AnimeDetails'));
const Home = React.lazy(() => import('../Home/Home'));
const SearchAnime = React.lazy(() => import('../SearchAnime/SearchAnime'));
const TopAnimePage = React.lazy(() => import('../TopAnimePage/TopAnimePage'));

function AppRouter() {
    const { data, featureArray, kmeans, titleIDMap } = useData();
    const sortedData = [...data].sort((a, b) => b.score - a.score);
    const top100Anime = sortedData.slice(0, 100);
    const memoizedTopAnimePage = useMemo(() => <TopAnimePage top100Anime={top100Anime} />, [top100Anime]);

    return (
        <Router>
            <Suspense fallback={<div>Loading...</div>}>
                <Routes>
                    <Route path="/" element={<Home data={data} />} />
                    <Route path="/topAnime" element={memoizedTopAnimePage} />
                    <Route path="/search" element={<SearchAnime data={data} titleIDMap={titleIDMap} />} />
                    {data.map((anime) => (
                        <Route
                            key={anime.id}
                            path={`/anime/${anime.id}`}
                            element={
                                <AnimeDetails anime={anime} data={data} kmeans={kmeans} featureArray={featureArray} />
                            }
                        />
                    ))}
                </Routes>
            </Suspense>
        </Router>
    );
}

export default AppRouter;
