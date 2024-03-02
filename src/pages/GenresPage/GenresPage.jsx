import { Outlet, useLocation } from 'react-router-dom';
import React, { useEffect, useMemo, useState } from 'react';

import DataList from './../../components/DataList/DataList';
import { useData } from '../../context/DataProvider';

function GenresPage() {
    const { filteredGenres, filteredThemes, filteredDemographics } = useData();
    const location = useLocation();
    const allowedUrls = ['/anime/genres', '/anime/themes', '/anime/demographics'];
    const isGenreDetailPage = allowedUrls.includes(location.pathname);

    return (
        <section id='genres' className="min-h-screen bg-secondary pb-16">
            {isGenreDetailPage && (
                <>
                    <DataList title="Genres" data={filteredGenres} path="genres" />
                    <DataList title="Themes" data={filteredThemes} path="themes" />
                    <DataList title="Demographics" data={filteredDemographics} path="demographics" />
                </>
            )}
            <Outlet />
        </section>
    );
}

export default React.memo(GenresPage);
