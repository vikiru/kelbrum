import { Route, Routes } from 'react-router-dom';

import AnimeDetails from '../AnimeDetails/AnimeDetails';
import Home from '../Home/Home';
import TopAnimePage from '../TopAnimePage/TopAnimePage';
import { useData } from '../../context/DataProvider';

function Router() {
    const { data, kmeans, featureArray, titleIDMap } = useData();
    const top100Anime = data.sort((a, b) => b.score - a.score).slice(0, 100);

    return (
        <Routes>
            <Route path="/" element={<Home data={data} />} />
            <Route path="/topAnime" element={<TopAnimePage top100Anime={top100Anime} />} />
            {data.map((anime) => (
                <Route
                    key={anime.id}
                    path={`/anime/${anime.id}`}
                    element={<AnimeDetails anime={anime} data={data} kmeans={kmeans} featureArray={featureArray} />}
                />
            ))}
        </Routes>
    );
}

export default Router;
