import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import DataList from './../../components/DataList/DataList';
import { useFilteredData } from '../../context/FilteredDataProvider';

function ProducersPage() {
    const { filteredProducers } = useFilteredData();
    const location = useLocation();
    const isProducerDetailPage = location.pathname === '/anime/producers';
    return (
        <section
            className="min-h-screen bg-secondary pb-16 dark:bg-gray-900"
            id="producers"
        >
            {isProducerDetailPage && (
                <DataList
                    data={filteredProducers}
                    path="producers"
                    title="Producers"
                />
            )}
            <Outlet />
        </section>
    );
}

export default React.memo(ProducersPage);
