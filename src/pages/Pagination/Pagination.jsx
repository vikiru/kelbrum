import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';

import AnimeCard from '../../components/AnimeCard/AnimeCard';
import { useFilteredData } from '../../context/FilteredDataProvider';

const Pagination = () => {
    const { id } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const parentPathSegments = location.pathname.split('/');
    const parentPath = parentPathSegments[2];
    const {
        filteredGenres,
        filteredThemes,
        filteredDemographics,
        filteredProducers,
        filteredStudios,
        filteredLicensors,
        filteredSeasons,
    } = useFilteredData();

    const itemsPerPage = 50;
    const [currentPage, setCurrentPage] = useState(1);
    const [items, setItems] = useState([]);
    const [displayedItems, setDisplayedItems] = useState([]);
    const [hasMore, setHasMore] = useState(true);

    let data;
    switch (parentPath) {
        case 'genres':
            data = filteredGenres[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'themes':
            data = filteredThemes[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'demographics':
            data = filteredDemographics[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'producers':
            data = filteredProducers[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'studios':
            data = filteredStudios[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'licensors':
            data = filteredLicensors[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'seasons':
            data = filteredSeasons[id ? parseInt(id, 10) - 1 : 0];
            break;
        default:
            data = null;
    }

    const title = `Top ${data.key} Anime`;
    const totalPages = Math.ceil(data.values.length / itemsPerPage);

    useEffect(() => {
        if (data && data.values) {
            const sortedData = [...data.values].sort((a, b) => b.score - a.score);
            setItems(sortedData);
        }
    }, [data]);

    useEffect(() => {
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const newItems = items.slice(startIndex, endIndex);
        setDisplayedItems(newItems);
        setHasMore(currentPage < totalPages);
    }, [currentPage, items, totalPages]);

    const handlePageChange = (newPage) => {
        if (newPage >= 1 && newPage <= totalPages) {
            setCurrentPage(newPage);
            navigate(`?page=${newPage}`);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    return (
        <section id={`top-${data ? data.key : 'anime'}-page-${currentPage}`} className="bg-secondary pb-6">
            <h2 className="bg-secondary pb-4 pt-6 text-center text-xl font-bold capitalize text-primary underline xs:text-lg lg:text-4xl">
                {title}
            </h2>
            <div className="m-8 grid gap-4 p-2 xs:grid-cols-1 lg:grid-cols-2 3xl:grid-cols-3">
                {displayedItems.map((item, index) => (
                    <AnimeCard key={item.title} anime={item} index={index + 1} />
                ))}
            </div>
            {hasMore && totalPages > 1 && (
                <section id="pagination" className="flex justify-center bg-secondary pb-6">
                    <div className="join">
                        <button
                            className="btn join-item"
                            onClick={() => handlePageChange(Math.max(currentPage - 1, 1))}
                            disabled={currentPage === 1}
                        >
                            «
                        </button>
                        <button className="btn join-item" onClick={() => handlePageChange(currentPage)}>
                            Page {currentPage} of {totalPages}
                        </button>
                        <button
                            className="btn join-item"
                            onClick={() => handlePageChange(Math.min(currentPage + 1, totalPages))}
                            disabled={currentPage === totalPages}
                        >
                            »
                        </button>
                    </div>
                </section>
            )}
        </section>
    );
};

export default Pagination;
