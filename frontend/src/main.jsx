import React from 'react';
import ReactDOM from 'react-dom/client';

import './App.css';
import App from './App.jsx';
import DataProvider from './context/DataProvider';

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <DataProvider>
            <App />
        </DataProvider>
    </React.StrictMode>,
);
