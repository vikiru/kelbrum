import React, { useMemo } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import DataList from './../../components/DataList/DataList';
import { useFilteredData } from '../../context/FilteredDataProvider';

function SeasonsPage() {
    const { filteredSeasons } = useFilteredData();
    const location = useLocation();
    const isSeasonDetailPage = location.pathname === '/anime/seasons';

    const compareSeasons = useMemo(() => {
        const seasons = ['spring', 'summer', 'fall', 'winter'];

        return (a, b) => {
            const isUnknownA = seasonA === 'Unknown';
            const isUnknownB = seasonB === 'Unknown';

            if (isUnknownA && isUnknownB) return 0;

            if (isUnknownA) return 1;

            if (isUnknownB) return -1;

            const [seasonA, yearA] = a.key.split(' ');
            const [seasonB, yearB] = b.key.split(' ');
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
        <section
            className="min-h-screen bg-secondary pb-16 dark:bg-gray-900"
            id="seasons"
        >
            {isSeasonDetailPage && (
                <DataList
                    capitalizeTitle={true}
                    customSort={compareSeasons}
                    data={filteredSeasons}
                    path="seasons"
                    title="Seasons"
                />
            )}
            <Outlet />
        </section>
    );
}

export default React.memo(SeasonsPage);
