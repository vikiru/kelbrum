import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

function NavBar() {
    // Mobile Dropdown States
    const [isDropdownVisible, setIsDropdownVisible] = useState(false);
    const toggleDropdown = () => {
        setIsDropdownVisible(!isDropdownVisible);
    };

    const location = useLocation();
    const [openDropdowns, setOpenDropdowns] = useState({
        discover: false,
        information: false,
    });

    useEffect(() => {
        setOpenDropdowns({
            discover: false,
            information: false,
        });
    }, [location]);

    return (
        <div className="navbar bg-base-100">
            <div className="navbar-start">
                <div className="dropdown">
                    <div tabIndex={0} role="button" className="btn btn-ghost lg:hidden" onClick={toggleDropdown}>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M4 6h16M4 12h8m-8 6h16"
                            />
                        </svg>
                    </div>
                    <ul
                        tabIndex={0}
                        className={`menu dropdown-content menu-sm z-[1] mt-3 w-52 rounded-box bg-base-100 p-2 shadow ${isDropdownVisible ? '' : 'hidden'}`}
                    >
                        <li>
                            <span>Discover</span>
                            <ul>
                                <li>
                                    <a onClick={toggleDropdown}>View top 100 anime</a>
                                </li>
                            </ul>
                        </li>
                        <li>
                            <a onClick={toggleDropdown}>Information</a>
                            <ul className="p-2">
                                <li className="p-2">
                                    <Link to="/anime/genres" onClick={toggleDropdown}>
                                        View all genres
                                    </Link>
                                </li>
                                <li className="p-2">
                                    <Link to="/anime/licensors" onClick={toggleDropdown}>
                                        View all licensors
                                    </Link>
                                </li>
                                <li className="p-2">
                                    <Link to="/anime/studios" onClick={toggleDropdown}>
                                        View all studios
                                    </Link>
                                </li>
                                <li className="p-2">
                                    <Link to="/anime/producers" onClick={toggleDropdown}>
                                        View all producers
                                    </Link>
                                </li>
                                <li className="p-2">
                                    <Link to="/anime/seasons" onClick={toggleDropdown}>
                                        View all seasons
                                    </Link>
                                </li>
                            </ul>
                        </li>
                    </ul>
                </div>
                <Link to="/" className="btn btn-ghost lg:text-xl">
                    AnimeRecommendation
                </Link>
            </div>
            <div className="navbar-center z-50 hidden lg:flex">
                <ul className="menu menu-horizontal px-4">
                    <li>
                        <details open={openDropdowns.discover}>
                            <summary>Discover</summary>
                            <ul className="p-2">
                                <li className="p-2">
                                    <Link to="/anime/top">View top anime</Link>
                                </li>
                            </ul>
                        </details>
                    </li>
                    <li>
                        <details open={openDropdowns.information}>
                            <summary>Information</summary>
                            <ul className="p-2">
                                <li className="p-2">
                                    <Link to="/anime/genres">View all genres</Link>
                                </li>
                                <li className="p-2">
                                    <Link to="/anime/licensors">View all licensors</Link>
                                </li>
                                <li className="p-2">
                                    <Link to="/anime/studios">View all studios</Link>
                                </li>
                                <li className="p-2">
                                    <Link to="/anime/producers">View all producers</Link>
                                </li>
                                <li className="p-2">
                                    <Link to="/anime/seasons">View all seasons</Link>
                                </li>
                            </ul>
                        </details>
                    </li>
                </ul>
            </div>
            <div className="navbar-end">
                <Link to="/anime/search">
                    <button className="btn btn-circle btn-ghost">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                            />
                        </svg>
                    </button>
                </Link>
            </div>
        </div>
    );
}

export default NavBar;
