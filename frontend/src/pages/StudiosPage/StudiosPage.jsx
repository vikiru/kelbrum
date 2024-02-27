import React from 'react';

import { useData } from '../../context/DataProvider';
import DataList from './../../components/DataList/DataList';

function StudiosPage() {
    const { filteredStudios } = useData();

    return (
        <div className="min-h-screen bg-secondary pb-16">
            <DataList title="Studios" data={filteredStudios} path="studios" />
        </div>
    );
}

export default React.memo(StudiosPage);
