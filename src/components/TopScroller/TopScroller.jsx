import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const TopScroller = () => {
    const { pathname } = useLocation();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    return null;
};

export default TopScroller;
