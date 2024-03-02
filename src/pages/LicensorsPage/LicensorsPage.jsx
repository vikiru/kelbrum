import { Outlet, useLocation } from 'react-router-dom';
import React, { useEffect, useMemo, useState } from 'react';

import DataList from './../../components/DataList/DataList';
import { useFilteredData } from '../../context/FilteredDataProvider';

function LicensorsPage() {
    const { filteredLicensors } = useFilteredData();
    const location = useLocation();
    const isLicensorDetailPage = location.pathname === '/anime/licensors';
    return (
        <div className="min-h-screen bg-secondary pb-16">
            {isLicensorDetailPage && <DataList title="Licensors" data={filteredLicensors} path="licensors" />}
            <Outlet />
        </div>
    );
}

export default React.memo(LicensorsPage);
