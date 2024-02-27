import React, { useMemo } from 'react';

import DataList from './../../components/DataList/DataList';
import { useData } from '../../context/DataProvider';

function SeasonsPage() {
    const { filteredSeasons } = useData();
    console.log(filteredSeasons);

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

    const groupBySeason = useMemo(() => {
        const uniqueSeasons = [...new Set(filteredSeasons.map((season) => season.key.split(' ')[0]))];

        return uniqueSeasons.map((seasonName) => ({
            key: seasonName,
            values: filteredSeasons.filter((season) => season.key.includes(seasonName)),
        }));
    }, [filteredSeasons]);

    console.log(groupBySeason);

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
