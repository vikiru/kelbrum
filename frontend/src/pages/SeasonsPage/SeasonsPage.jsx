import React, { useMemo } from 'react';

import { useData } from '../../context/DataProvider';
import DataList from './../../components/DataList/DataList';

function SeasonsPage() {
    const { filteredSeasons } = useData();

    const compareSeasons = useMemo(() => {
        const seasons = ['spring', 'summer', 'fall', 'winter'];

        return (a, b) => {
            const [seasonA, yearA] = a[1].key.split(' ');
            const [seasonB, yearB] = b[1].key.split(' ');

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
        <div className="min-h-screen bg-secondary pb-16">
            <DataList
                title="Seasons"
                data={filteredSeasons}
                path="seasons"
                customSort={compareSeasons}
                capitalizeTitle={true}
            />
        </div>
    );
}

export default React.memo(SeasonsPage);
