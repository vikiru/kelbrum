import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { useFilteredData } from '../../context/FilteredDataProvider';
import DataList from './../../components/DataList/DataList';

function ProducersPage() {
    const { filteredProducers } = useFilteredData();
    const location = useLocation();
    const isProducerDetailPage = location.pathname === '/anime/producers';
    return (
        <section id="producers" className="min-h-screen bg-secondary pb-16 dark:bg-gray-900">
            {isProducerDetailPage && <DataList title="Producers" data={filteredProducers} path="producers" />}
            <Outlet />
        </section>
    );
}

export default React.memo(ProducersPage);
