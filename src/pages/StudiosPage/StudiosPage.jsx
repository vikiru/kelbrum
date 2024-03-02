import { Outlet, useLocation } from 'react-router-dom';

import DataList from './../../components/DataList/DataList';
import React from 'react';
import { useFilteredData } from '../../context/FilteredDataProvider';

function StudiosPage() {
    const { filteredStudios } = useFilteredData();
    const location = useLocation();
    const isStudioDetailPage = location.pathname === '/anime/studios';
    return (
        <div className="min-h-screen bg-secondary pb-16">
            {isStudioDetailPage && <DataList title="Studios" data={filteredStudios} path="studios" />}
            <Outlet />
        </div>
    );
}

export default React.memo(StudiosPage);
