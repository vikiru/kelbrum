import React, { useMemo } from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { useFilteredData } from '../../context/FilteredDataProvider';
import DataList from './../../components/DataList/DataList';

function SeasonsPage() {
    const { filteredSeasons } = useFilteredData();
    const location = useLocation();
    const isSeasonDetailPage = location.pathname === '/anime/seasons';

    const compareSeasons = useMemo(() => {
        const seasons = ['spring', 'summer', 'fall', 'winter'];

        return (a, b) => {
            const [seasonA, yearA] = a.key.split(' ');
            const [seasonB, yearB] = b.key.split(' ');

            const isUnknownA = seasonA === 'Unknown';
            const isUnknownB = seasonB === 'Unknown';

            if (isUnknownA && isUnknownB) return 0;

            if (isUnknownA) return 1;

            if (isUnknownB) return -1;

            const seasonValueA = seasons.indexOf(seasonA);
            const seasonValueB = seasons.indexOf(seasonB);

            if (yearA < yearB) return -1;
            if (yearA > yearB) return 1;

            if (seasonValueA < seasonValueB) return -1;
            if (seasonValueA > seasonValueB) return 1;

            return 0;
        };
    }, []);

    return (
        <section id="seasons" className="min-h-screen bg-secondary pb-16 dark:bg-gray-900">
            {isSeasonDetailPage && (
                <DataList
                    title="Seasons"
                    data={filteredSeasons}
                    path="seasons"
                    customSort={compareSeasons}
                    capitalizeTitle={true}
                />
            )}
            <Outlet />
        </section>
    );
}

export default React.memo(SeasonsPage);
