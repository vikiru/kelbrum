import React, { useEffect, useMemo, useState } from 'react';

import DataList from './../../components/DataList/DataList';
import { useData } from '../../context/DataProvider';

function SeasonsPage() {
    const { filteredSeasons } = useData();

    return (
        <div className="min-h-screen bg-secondary pb-16">
            <DataList title="Seasons" data={filteredSeasons} path="seasons" />
        </div>
    );
}

export default SeasonsPage;
