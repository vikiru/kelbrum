import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Footer() {
    return (
        <section id="footer" className="bottom-0">
            <footer
                id="navigation-footer"
                className="footer flex justify-between bg-neutral p-10 text-neutral-content lg:grid-cols-2 dark:bg-gray-800"
            >
                <nav>
                    <h6 className="footer-title text-xl">Discover</h6>
                    <Link to="/" className="link-hover link text-lg 2xl:text-2xl">
                        Home
                    </Link>
                    <Link to="/anime/search" className="link-hover link text-lg  2xl:text-2xl">
                        Search for an anime
                    </Link>
                    <Link to="/anime/top" className="link-hover link text-lg 2xl:text-2xl">
                        View top 100 anime
                    </Link>
                </nav>
                <nav>
                    <h6 className="footer-title text-xl">Information</h6>

                    <Link to="/anime/genres" className="link-hover link text-lg 2xl:text-2xl">
                        View all genres
                    </Link>
                    <Link to="/anime/licensors" className="link-hover link text-lg 2xl:text-2xl">
                        View all licensors
                    </Link>
                    <Link to="/anime/studios" className="link-hover link text-lg 2xl:text-2xl">
                        View all studios
                    </Link>
                    <Link to="/anime/producers" className="link-hover link text-lg 2xl:text-2xl">
                        View all producers
                    </Link>
                    <Link to="/anime/seasons" className="link-hover link text-lg 2xl:text-2xl">
                        View all seasons
                    </Link>
                </nav>
                <nav>
                    <h6 className="footer-title text-xl">About</h6>
                    <a
                        className="link-hover link text-lg 2xl:text-2xl"
                        href="https://vikiru.github.io/kelbrum/acknowledgments/"
                    >
                        Acknowledgments
                    </a>
                    <a className="link-hover link text-lg 2xl:text-2xl" href="https://vikiru.github.io/kelbrum/">
                        Documentation
                    </a>
                    <a
                        className="link-hover link text-lg 2xl:text-2xl"
                        href="https://github.com/vikiru/kelbrum/"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        GitHub
                    </a>
                </nav>
            </footer>
            <footer
                id="copyright"
                className="footer footer-center border-t border-base-300 bg-neutral px-10 py-4 text-base-content dark:bg-gray-800"
            >
                <div className="text-center text-lg text-neutral-content 2xl:text-2xl">
                    &copy; {new Date().getFullYear()} Kelbrum, built by Visakan Kirubakaran. All images and text belong
                    to their rightful owners.
                </div>
            </footer>
        </section>
    );
}

export default Footer;
