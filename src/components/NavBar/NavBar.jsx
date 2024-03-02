import { Link, useLocation } from 'react-router-dom';
import React, { useEffect, useState } from 'react';

function NavBar() {
    const [isDropdownVisible, setIsDropdownVisible] = useState(false);
    const toggleDropdown = () => {
        setIsDropdownVisible(!isDropdownVisible);
    };

    return (
        <section id='navbar' className="navbar bg-base-100 text-gray-100 dark:bg-gray-800 dark:text-gray-100">
            <div className="navbar-start">
                <div className="dropdown rounded-full dark:bg-gray-800">
                    <div tabIndex={0} role="button" className="btn btn-ghost rounded-full" onClick={toggleDropdown}>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5 fill-current text-gray-100 dark:text-gray-100"
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
                        className={`menu dropdown-content menu-sm z-[1] mt-3 w-52 rounded-box bg-base-100 p-2 shadow dark:bg-gray-800 ${isDropdownVisible ? '' : 'hidden'}`}
                    >
                        <li>
                            <span>Discover</span>
                            <ul>
                                <li>
                                    <Link to="anime/top" onClick={toggleDropdown}>
                                        View top 100 anime
                                    </Link>
                                </li>
                            </ul>
                        </li>
                        <li>
                            <span>Information</span>
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
            </div>
            <div className="xs:navbar-center">
                <Link
                    to="/"
                    className="btn btn-ghost font-logo text-xl text-gray-100 lg:text-3xl 2xl:text-4xl dark:text-gray-100"
                    role="button"
                    alt="Visit Kelbrum Homepage"
                >
                    <p>
                        <span className="inline whitespace-nowrap text-[#00ffff]">Kel</span>
                        <span className="inline whitespace-nowrap text-[#ffa500]">brum</span>
                    </p>
                </Link>
            </div>
            <div className="navbar-end">
                <Link to="/anime/search">
                    <button className="btn btn-circle btn-ghost">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5 fill-current text-gray-100 dark:text-gray-100"
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
        </section>
    );
}

export default NavBar;
