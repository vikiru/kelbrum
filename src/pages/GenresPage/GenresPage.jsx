import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import DataList from './../../components/DataList/DataList';
import { useFilteredData } from '../../context/FilteredDataProvider';

function GenresPage() {
    const { filteredGenres, filteredThemes, filteredDemographics } =
        useFilteredData();
    const location = useLocation();
    const allowedUrls = [
        '/anime/genres',
        '/anime/themes',
        '/anime/demographics',
    ];
    const isGenreDetailPage = allowedUrls.includes(location.pathname);

    return (
        <section
            className="min-h-screen bg-secondary pb-16 dark:bg-gray-900"
            id="genres"
        >
            {isGenreDetailPage && (
                <>
                    <DataList
                        data={filteredGenres}
                        path="genres"
                        title="Genres"
                    />
                    <DataList
                        data={filteredThemes}
                        path="themes"
                        title="Themes"
                    />
                    <DataList
                        data={filteredDemographics}
                        path="demographics"
                        title="Demographics"
                    />
                </>
            )}
            <Outlet />
        </section>
    );
}

export default React.memo(GenresPage);
