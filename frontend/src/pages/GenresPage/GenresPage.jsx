import React, { useEffect, useMemo, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { useData } from '../../context/DataProvider';
import DataList from './../../components/DataList/DataList';

function GenresPage() {
    const { filteredGenres, filteredThemes, filteredDemographics } = useData();
    const location = useLocation();
    const allowedUrls = ['/anime/genres', '/anime/themes', '/anime/demographics'];
    const isGenreDetailPage = allowedUrls.includes(location.pathname);

    return (
        <div className="min-h-screen bg-secondary pb-16">
            {isGenreDetailPage && (
                <>
                    <DataList title="Genres" data={filteredGenres} path="genres" />
                    <DataList title="Themes" data={filteredThemes} path="themes" />
                    <DataList title="Demographics" data={filteredDemographics} path="demographics" />
                </>
            )}
            <Outlet />
        </div>
    );
}

export default GenresPage;
