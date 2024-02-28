import React, { useEffect, useMemo, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { useData } from '../../context/DataProvider';
import DataList from './../../components/DataList/DataList';

function LicensorsPage() {
    const { filteredLicensors } = useData();
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
