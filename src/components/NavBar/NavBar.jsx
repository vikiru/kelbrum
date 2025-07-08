import { useState } from 'react';
import { Link } from 'react-router-dom';

function NavBar() {
    const [isDropdownVisible, setIsDropdownVisible] = useState(false);
    const toggleDropdown = () => {
        setIsDropdownVisible(!isDropdownVisible);
    };

    return (
        <section
            className="navbar bg-neutral text-secondary dark:bg-gray-800 dark:text-gray-100"
            id="navbar"
        >
            <div className="navbar-start">
                <div className="dropdown rounded-full dark:bg-gray-800">
                    <div
                        className="btn btn-ghost rounded-full"
                        onClick={toggleDropdown}
                        role="button"
                        tabIndex={0}
                    >
                        <svg
                            className="h-10 w-10 fill-current text-secondary 4xl:h-20 4xl:w-20 dark:text-gray-100"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M4 6h16M4 12h8m-8 6h16"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                            />
                        </svg>
                    </div>
                    <ul
                        className={`menu dropdown-content menu-sm z-[1] mt-3 w-52 rounded-box bg-base-100 p-2 shadow 2xl:w-60 dark:bg-gray-800 ${isDropdownVisible ? '' : 'hidden'}`}
                    >
                        <li>
                            <span className="2xl:text-2xl">Discover</span>
                            <ul className="p-2">
                                <li className="p-2">
                                    <Link
                                        className="2xl:text-xl"
                                        onClick={toggleDropdown}
                                        to="anime/top"
                                    >
                                        View top 100 anime
                                    </Link>
                                </li>
                            </ul>
                        </li>
                        <li>
                            <span className="2xl:text-2xl">Information</span>
                            <ul className="p-2">
                                <li className="p-2">
                                    <Link
                                        className="2xl:text-xl"
                                        onClick={toggleDropdown}
                                        to="/anime/genres"
                                    >
                                        View all genres
                                    </Link>
                                </li>
                                <li className="p-2">
                                    <Link
                                        className="2xl:text-xl"
                                        onClick={toggleDropdown}
                                        to="/anime/licensors"
                                    >
                                        View all licensors
                                    </Link>
                                </li>
                                <li className="p-2">
                                    <Link
                                        className="2xl:text-xl"
                                        onClick={toggleDropdown}
                                        to="/anime/studios"
                                    >
                                        View all studios
                                    </Link>
                                </li>
                                <li className="p-2">
                                    <Link
                                        className="2xl:text-xl"
                                        onClick={toggleDropdown}
                                        to="/anime/producers"
                                    >
                                        View all producers
                                    </Link>
                                </li>
                                <li className="p-2">
                                    <Link
                                        className="2xl:text-xl"
                                        onClick={toggleDropdown}
                                        to="/anime/seasons"
                                    >
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
                    alt="Visit Kelbrum Homepage"
                    className="btn btn-ghost font-logo text-xl text-secondary lg:text-4xl dark:text-gray-100"
                    role="button"
                    to="/"
                >
                    <p className="xs:text-lg lg:text-4xl 2xl:text-5xl">
                        <span className="inline whitespace-nowrap text-[#00ffff]">
                            Kel
                        </span>
                        <span className="inline whitespace-nowrap text-[#ffa500]">
                            brum
                        </span>
                    </p>
                </Link>
            </div>
            <div className="navbar-end mr-4">
                <Link to="/anime/search">
                    <button className="btn btn-circle btn-ghost">
                        <svg
                            className="h-10 w-10 fill-current text-secondary 4xl:h-20 4xl:w-20 dark:text-gray-100"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                            />
                        </svg>
                    </button>
                </Link>
            </div>
        </section>
    );
}

export default NavBar;
