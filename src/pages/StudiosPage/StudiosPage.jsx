import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { useFilteredData } from '../../context/FilteredDataProvider';
import DataList from './../../components/DataList/DataList';

function StudiosPage() {
    const { filteredStudios } = useFilteredData();
    const location = useLocation();
    const isStudioDetailPage = location.pathname === '/anime/studios';
    return (
        <section id="studios" className="min-h-screen bg-secondary pb-16 dark:bg-gray-900">
            {isStudioDetailPage && <DataList title="Studios" data={filteredStudios} path="studios" />}
            <Outlet />
        </section>
    );
}

export default React.memo(StudiosPage);
