import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { useFilteredData } from '../../context/FilteredDataProvider';
import DataList from './../../components/DataList/DataList';

function ProducersPage() {
    const { filteredProducers } = useFilteredData();
    const location = useLocation();
    const isProducerDetailPage = location.pathname === '/anime/producers';
    return (
        <div className="min-h-screen bg-secondary pb-16">
            {isProducerDetailPage && <DataList title="Producers" data={filteredProducers} path="producers" />}
            <Outlet />
        </div>
    );
}

export default React.memo(ProducersPage);
