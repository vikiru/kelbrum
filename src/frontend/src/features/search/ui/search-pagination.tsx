import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/shared/components/ui/pagination';

interface SearchPaginationProps {
  currentPage: number;
  pageCount: number;
  onPageChange: (page: number) => void;
}

export function SearchPagination({ currentPage, pageCount, onPageChange }: SearchPaginationProps) {
  const isFirstPage = currentPage === 1;
  const isLastPage = currentPage === pageCount;

  function goToPage(page: number) {
    onPageChange(Math.min(pageCount, Math.max(1, page)));
  }

  return (
    <Pagination className="mt-10" aria-label="Search result pages">
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            href="#search-results"
            aria-disabled={isFirstPage}
            tabIndex={isFirstPage ? -1 : undefined}
            className={isFirstPage ? 'pointer-events-none opacity-50' : undefined}
            onClick={(event) => {
              event.preventDefault();
              if (!isFirstPage) goToPage(currentPage - 1);
            }}
          />
        </PaginationItem>
        {getPaginationItems(currentPage, pageCount).map((item) => (
          <PaginationItem key={item.key}>
            {item.value === 'ellipsis' ? (
              <PaginationEllipsis />
            ) : (
              <PaginationLink
                href="#search-results"
                size="icon"
                isActive={item.value === currentPage}
                aria-label={`Go to page ${item.value}`}
                onClick={(event) => {
                  event.preventDefault();
                  goToPage(item.value);
                }}
              >
                {item.value}
              </PaginationLink>
            )}
          </PaginationItem>
        ))}
        <PaginationItem>
          <PaginationNext
            href="#search-results"
            aria-disabled={isLastPage}
            tabIndex={isLastPage ? -1 : undefined}
            className={isLastPage ? 'pointer-events-none opacity-50' : undefined}
            onClick={(event) => {
              event.preventDefault();
              if (!isLastPage) goToPage(currentPage + 1);
            }}
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}

type PaginationItem = { key: string; value: number } | { key: string; value: 'ellipsis' };

function getPaginationItems(currentPage: number, pageCount: number): PaginationItem[] {
  if (pageCount <= 8) {
    return Array.from({ length: pageCount }, (_, index) => ({ key: `page-${index + 1}`, value: index + 1 }));
  }
  if (currentPage <= 4) return createPaginationItems([1, 2, 3, 4, 5, 'ellipsis', pageCount], 'end');
  if (currentPage >= pageCount - 3) {
    return createPaginationItems(
      [1, 'ellipsis', pageCount - 4, pageCount - 3, pageCount - 2, pageCount - 1, pageCount],
      'start',
    );
  }
  return createPaginationItems([1, 'ellipsis', currentPage - 1, currentPage, currentPage + 1, 'ellipsis', pageCount]);
}

function createPaginationItems(
  items: Array<number | 'ellipsis'>,
  ellipsisPosition?: 'start' | 'end',
): PaginationItem[] {
  let ellipsisCount = 0;

  return items.map((value) => {
    if (value !== 'ellipsis') return { key: `page-${value}`, value };

    ellipsisCount += 1;
    const position = ellipsisPosition ?? (ellipsisCount === 1 ? 'start' : 'end');
    return { key: `ellipsis-${position}`, value };
  });
}
