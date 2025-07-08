import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import DataList from './../../components/DataList/DataList';
import { useFilteredData } from '../../context/FilteredDataProvider';

function StudiosPage() {
    const { filteredStudios } = useFilteredData();
    const location = useLocation();
    const isStudioDetailPage = location.pathname === '/anime/studios';
    return (
        <section
            className="min-h-screen bg-secondary pb-16 dark:bg-gray-900"
            id="studios"
        >
            {isStudioDetailPage && (
                <DataList
                    data={filteredStudios}
                    path="studios"
                    title="Studios"
                />
            )}
            <Outlet />
        </section>
    );
}

export default React.memo(StudiosPage);
