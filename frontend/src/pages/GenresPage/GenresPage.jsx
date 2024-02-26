import React, { useEffect, useMemo, useState } from 'react';

import { useData } from '../../context/DataProvider';
import DataList from './../../components/DataList/DataList';

function GenresPage() {
    const { filteredGenres, filteredDemographics } = useData();

    return (
        <div className="min-h-screen bg-secondary pb-16">
            <DataList title="Genres" data={filteredGenres} path="genres" />
            <DataList title="Demographics" data={filteredDemographics} path="demographics" />
        </div>
    );
}

export default GenresPage;
