import { useState, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { getPeople, getCategories, getFactions, getLiveStatuses } from "../services/api";
import PersonCard from "../components/people/PersonCard";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";

const PAGE_SIZE = 24;

export default function CreatorDirectoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchParam = searchParams.get("search") || "";
  const categoryParam = searchParams.get("category") || "all";
  const factionParam = searchParams.get("faction") || "all";
  const pageParam = parseInt(searchParams.get("page") || "1", 10) || 1;

  // Filter & search states
  const [searchTerm, setSearchTerm] = useState(searchParam);
  const [debouncedSearch, setDebouncedSearch] = useState(searchParam);
  const [selectedCategory, setSelectedCategory] = useState(categoryParam);
  const [selectedFaction, setSelectedFaction] = useState(factionParam);
  const [currentPage, setCurrentPage] = useState(pageParam);

  // Data states
  const [people, setPeople] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [categories, setCategories] = useState([]);
  const [factions, setFactions] = useState([]);
  const [liveStatuses, setLiveStatuses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load filter options (categories & factions) once on mount
  useEffect(() => {
    let isMounted = true;

    Promise.all([getCategories(), getFactions({ page_size: 100 })])
      .then(([categoriesData, factionsData]) => {
        if (isMounted) {
          setCategories(categoriesData || []);
          setFactions(factionsData || []);
        }
      })
      .catch((err) => {
        console.warn("Failed to load filter metadata:", err?.message || err);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Debounce search input (300ms) to prevent unnecessary requests while typing
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setCurrentPage(1);
    }, 300);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm]);

  // Synchronize URL parameters with current filters & pagination
  useEffect(() => {
    const nextParams = new URLSearchParams();
    if (debouncedSearch.trim()) nextParams.set("search", debouncedSearch.trim());
    if (selectedCategory !== "all") nextParams.set("category", selectedCategory);
    if (selectedFaction !== "all") nextParams.set("faction", selectedFaction);
    if (currentPage > 1) nextParams.set("page", String(currentPage));
    setSearchParams(nextParams, { replace: true });
  }, [debouncedSearch, selectedCategory, selectedFaction, currentPage, setSearchParams]);

  // Query the backend API whenever filters, search, or page change
  useEffect(() => {
    let isMounted = true;

    const queryOptions = {
      search: debouncedSearch.trim() || undefined,
      category: selectedCategory !== "all" ? selectedCategory : undefined,
      faction: selectedFaction !== "all" ? selectedFaction : undefined,
      page: currentPage,
      page_size: PAGE_SIZE,
      paginated: true,
    };

    getPeople(queryOptions)
      .then((data) => {
        if (isMounted) {
          setPeople(data?.results || []);
          setTotalCount(data?.count || 0);
          setError(null);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err?.message || "Failed to load directory data.");
          setPeople([]);
          setTotalCount(0);
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [debouncedSearch, selectedCategory, selectedFaction, currentPage]);

  // Poll live statuses periodically (~60 seconds)
  useEffect(() => {
    let isMounted = true;
    let isFetching = false;

    const fetchLive = async () => {
      if (isFetching) return;
      isFetching = true;
      try {
        const data = await getLiveStatuses();
        if (isMounted && Array.isArray(data)) {
          setLiveStatuses(data);
        }
      } catch (err) {
        console.warn("Failed to fetch live statuses:", err?.message || err);
      } finally {
        isFetching = false;
      }
    };

    fetchLive();
    const intervalId = setInterval(fetchLive, 60000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  // Map live statuses by person_slug for quick lookup
  const liveStatusMap = useMemo(() => {
    const map = {};
    if (Array.isArray(liveStatuses)) {
      liveStatuses.forEach((status) => {
        if (status?.person_slug) {
          map[status.person_slug] = status;
        }
      });
    }
    return map;
  }, [liveStatuses]);

  // Filter change handlers
  const handleCategoryChange = (slug) => {
    setSelectedCategory(slug);
    setCurrentPage(1);
  };

  const handleFactionChange = (slug) => {
    setSelectedFaction(slug);
    setCurrentPage(1);
  };

  const resetFilters = () => {
    setSearchTerm("");
    setDebouncedSearch("");
    setSelectedCategory("all");
    setSelectedFaction("all");
    setCurrentPage(1);
  };

  const totalPages = Math.ceil(totalCount / PAGE_SIZE) || 1;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="border-b border-neutral-800 pb-6">
        <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
          Creators & Roleplayers Directory
        </h1>
        <p className="mt-1 text-sm text-neutral-400">
          Search and discover streamers, roleplayers, and citizens active in Xlantis RP.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-300">
          <strong className="font-semibold">Error:</strong> {error}
        </div>
      )}

      {/* Search & Filter Toolbar */}
      <div className="mt-6 space-y-4">
        {/* Search input and Faction selector */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="relative sm:col-span-2">
            <label htmlFor="search-creators" className="sr-only">
              Search creators and streamers
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
              id="search-creators"
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by character name or bio..."
              className="w-full rounded-xl border border-neutral-800 bg-neutral-900/80 py-2.5 pl-10 pr-4 text-sm text-neutral-100 placeholder-neutral-500 transition-colors focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>

          <div>
            <label htmlFor="faction-select" className="sr-only">
              Filter by Faction
            </label>
            <select
              id="faction-select"
              value={selectedFaction}
              onChange={(e) => handleFactionChange(e.target.value)}
              className="w-full rounded-xl border border-neutral-800 bg-neutral-900/80 py-2.5 px-3 text-sm text-neutral-200 transition-colors focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              <option value="all">All Factions / Independent</option>
              {factions.map((f) => (
                <option key={f.id || f.slug} value={f.slug}>
                  {f.tag ? `[${f.tag}] ` : ""}
                  {f.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1" role="toolbar" aria-label="Category Filters">
          <button
            type="button"
            onClick={() => handleCategoryChange("all")}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500/50 ${
              selectedCategory === "all"
                ? "bg-emerald-500 text-neutral-950 shadow-sm"
                : "border border-neutral-800 bg-neutral-900/60 text-neutral-300 hover:border-neutral-700 hover:text-white"
            }`}
          >
            All Categories
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id || cat.slug}
              type="button"
              onClick={() => handleCategoryChange(cat.slug)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-500/50 ${
                selectedCategory === cat.slug
                  ? "bg-emerald-500 text-neutral-950 shadow-sm"
                  : "border border-neutral-800 bg-neutral-900/60 text-neutral-300 hover:border-neutral-700 hover:text-white"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      {/* Content Results */}
      <div className="mt-8">
        {loading ? (
          <Loading message="Fetching directory profiles..." />
        ) : people.length > 0 ? (
          <div>
            <div className="mb-4 flex items-center justify-between text-xs text-neutral-400">
              <span>
                Showing <strong className="text-neutral-200">{people.length}</strong> of{" "}
                <strong className="text-neutral-200">{totalCount}</strong> profile
                {totalCount === 1 ? "" : "s"}
              </span>
              {(debouncedSearch || selectedCategory !== "all" || selectedFaction !== "all") && (
                <button
                  type="button"
                  onClick={resetFilters}
                  className="text-emerald-400 hover:text-emerald-300 underline focus:outline-none"
                >
                  Clear all filters
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {people.map((person) => (
                <PersonCard
                  key={person.id || person.slug}
                  person={person}
                  liveStatus={liveStatusMap[person.slug]}
                />
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
            title={error ? "Unable to load profiles" : "No roleplayers or creators found"}
            description={
              error
                ? "The server could not be reached. Please try again later."
                : "No profiles match your current search criteria or active filters."
            }
            actionLabel={error ? undefined : "Reset Filters"}
            onAction={error ? undefined : resetFilters}
          />
        )}
      </div>
    </div>
  );
}
