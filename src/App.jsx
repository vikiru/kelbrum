import { AppProvider } from './context/AppProvider';
import React from 'react';
import Router from './pages/Router/Router';

function App() {
    return (
        <Router />
    );
}

export default AppProvider(App);
