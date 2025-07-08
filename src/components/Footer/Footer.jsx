import { Link } from 'react-router-dom';

function Footer() {
    return (
        <section className="bottom-0" id="footer">
            <footer
                className="footer grid justify-between bg-neutral p-10 text-neutral-content lg:grid-cols-2 dark:bg-gray-800"
                id="navigation-footer"
            >
                <nav>
                    <h6 className="footer-title text-xl">Discover</h6>
                    <Link
                        className="link-hover link text-lg 2xl:text-2xl"
                        to="/"
                    >
                        Home
                    </Link>
                    <Link
                        className="link-hover link text-lg  2xl:text-2xl"
                        to="/anime/search"
                    >
                        Search for an anime
                    </Link>
                    <Link
                        className="link-hover link text-lg 2xl:text-2xl"
                        to="/anime/top"
                    >
                        View top 100 anime
                    </Link>
                </nav>
                <nav>
                    <h6 className="footer-title text-xl">Information</h6>

                    <Link
                        className="link-hover link text-lg 2xl:text-2xl"
                        to="/anime/genres"
                    >
                        View all genres
                    </Link>
                    <Link
                        className="link-hover link text-lg 2xl:text-2xl"
                        to="/anime/licensors"
                    >
                        View all licensors
                    </Link>
                    <Link
                        className="link-hover link text-lg 2xl:text-2xl"
                        to="/anime/studios"
                    >
                        View all studios
                    </Link>
                    <Link
                        className="link-hover link text-lg 2xl:text-2xl"
                        to="/anime/producers"
                    >
                        View all producers
                    </Link>
                    <Link
                        className="link-hover link text-lg 2xl:text-2xl"
                        to="/anime/seasons"
                    >
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
                    <a
                        className="link-hover link text-lg 2xl:text-2xl"
                        href="https://vikiru.github.io/kelbrum/"
                    >
                        Documentation
                    </a>
                    <a
                        className="link-hover link text-lg 2xl:text-2xl"
                        href="https://github.com/vikiru/kelbrum/"
                        rel="noopener noreferrer"
                        target="_blank"
                    >
                        GitHub
                    </a>
                </nav>
            </footer>
            <footer
                className="footer footer-center border-t border-base-300 bg-neutral px-10 py-4 text-base-content dark:bg-gray-800"
                id="copyright"
            >
                <div className="text-center text-lg text-neutral-content 2xl:text-2xl">
                    &copy; {new Date().getFullYear()} Kelbrum, built by Visakan
                    Kirubakaran. All images and text belong to their rightful
                    owners.
                </div>
            </footer>
        </section>
    );
}

export default Footer;
