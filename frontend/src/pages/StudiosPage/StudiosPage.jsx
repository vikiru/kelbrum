import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { useData } from '../../context/DataProvider';
import DataList from './../../components/DataList/DataList';

function StudiosPage() {
    const { filteredStudios } = useData();
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
