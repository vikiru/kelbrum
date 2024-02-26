import React, { useEffect, useMemo, useState } from 'react';

import { useData } from '../../context/DataProvider';
import DataList from './../../components/DataList/DataList';

function ProducersPage() {
    const { filteredProducers } = useData();

    return (
        <div className="min-h-screen bg-secondary pb-16">
            <DataList title="Producers" data={filteredProducers} path="producers" />
        </div>
    );
}

export default ProducersPage;
