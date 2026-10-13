import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { getFactions } from "../services/api";
import FactionCard from "../components/factions/FactionCard";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";

const PAGE_SIZE = 24;

export default function GangDirectoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchParam = searchParams.get("search") || "";
  const statusParam = searchParams.get("status") || "all";
  const pageParam = parseInt(searchParams.get("page") || "1", 10) || 1;

  // Filter & search states
  const [searchTerm, setSearchTerm] = useState(searchParam);
  const [debouncedSearch, setDebouncedSearch] = useState(searchParam);
  const [statusFilter, setStatusFilter] = useState(statusParam);
  const [currentPage, setCurrentPage] = useState(pageParam);

  // Data states
  const [factions, setFactions] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Debounce search input (300ms) to avoid querying on every keystroke
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setCurrentPage(1);
    }, 300);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm]);

  // Synchronize URL parameters with active filters & pagination
  useEffect(() => {
    const nextParams = new URLSearchParams();
    if (debouncedSearch.trim()) nextParams.set("search", debouncedSearch.trim());
    if (statusFilter !== "all") nextParams.set("status", statusFilter);
    if (currentPage > 1) nextParams.set("page", String(currentPage));
    setSearchParams(nextParams, { replace: true });
  }, [debouncedSearch, statusFilter, currentPage, setSearchParams]);

  // Query backend API whenever search, status filter, or page changes
  useEffect(() => {
    let isMounted = true;

    const queryOptions = {
      search: debouncedSearch.trim() || undefined,
      status: statusFilter !== "all" ? statusFilter : undefined,
      page: currentPage,
      page_size: PAGE_SIZE,
      paginated: true,
    };

    getFactions(queryOptions)
      .then((data) => {
        if (isMounted) {
          setFactions(data?.results || []);
          setTotalCount(data?.count || 0);
          setError(null);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err?.message || "Failed to load factions.");
          setFactions([]);
          setTotalCount(0);
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [debouncedSearch, statusFilter, currentPage]);

  const handleStatusChange = (status) => {
    setStatusFilter(status);
    setCurrentPage(1);
  };

  const resetFilters = () => {
    setSearchTerm("");
    setDebouncedSearch("");
    setStatusFilter("all");
    setCurrentPage(1);
  };

  const totalPages = Math.ceil(totalCount / PAGE_SIZE) || 1;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="border-b border-neutral-800 pb-6">
        <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
          Gangs & Factions Directory
        </h1>
        <p className="mt-1 text-sm text-neutral-400">
          Official registry of gangs, syndicates, departments, and organizations in Xlantis.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-300">
          <strong className="font-semibold">Error:</strong> {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <label htmlFor="search-factions" className="sr-only">
            Search gangs and factions
          </label>
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-neutral-400">
            <svg
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
              />
            </svg>
          </div>
          <input
            id="search-factions"
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by gang name, tag (e.g. SYN, LSPD)..."
            className="w-full rounded-xl border border-neutral-800 bg-neutral-900/80 py-2.5 pl-10 pr-4 text-sm text-neutral-100 placeholder-neutral-500 transition-colors focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          />
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-neutral-400 font-medium">Status:</span>
          {["all", "active", "inactive"].map((status) => (
            <button
              key={status}
              type="button"
              onClick={() => handleStatusChange(status)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold uppercase tracking-wider transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500/50 ${
                statusFilter === status
                  ? "bg-emerald-500 text-neutral-950 shadow-sm"
                  : "border border-neutral-800 bg-neutral-900/60 text-neutral-400 hover:border-neutral-700 hover:text-white"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div className="mt-8">
        {loading ? (
          <Loading message="Loading factions and gangs..." />
        ) : factions.length > 0 ? (
          <div>
            <div className="mb-4 flex items-center justify-between text-xs text-neutral-400">
              <span>
                Showing <strong className="text-neutral-200">{factions.length}</strong> of{" "}
                <strong className="text-neutral-200">{totalCount}</strong> faction
                {totalCount === 1 ? "" : "s"}
              </span>
              {(debouncedSearch || statusFilter !== "all") && (
                <button
                  type="button"
                  onClick={resetFilters}
                  className="text-emerald-400 hover:text-emerald-300 underline focus:outline-none"
                >
                  Clear filters
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {factions.map((faction) => (
                <FactionCard key={faction.id || faction.slug} faction={faction} />
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-between border-t border-neutral-800/80 pt-4 text-xs">
                <button
                  type="button"
                  disabled={currentPage <= 1}
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  className="rounded-lg border border-neutral-800 bg-neutral-900/80 px-3 py-1.5 font-medium text-neutral-300 transition-colors hover:border-neutral-700 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  &larr; Previous
                </button>
                <span className="text-neutral-400">
                  Page <strong className="text-neutral-200">{currentPage}</strong> of{" "}
                  <strong className="text-neutral-200">{totalPages}</strong>
                </span>
                <button
                  type="button"
                  disabled={currentPage >= totalPages}
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  className="rounded-lg border border-neutral-800 bg-neutral-900/80 px-3 py-1.5 font-medium text-neutral-300 transition-colors hover:border-neutral-700 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next &rarr;
                </button>
              </div>
            )}
          </div>
        ) : (
          <EmptyState
            title={error ? "Unable to load factions" : "No factions or gangs found"}
            description={
              error
                ? "The server could not be reached. Please try again later."
                : "No organizations match your current search criteria."
            }
            actionLabel={error ? undefined : "Reset Search"}
            onAction={error ? undefined : resetFilters}
          />
        )}
      </div>
    </div>
  );
}
