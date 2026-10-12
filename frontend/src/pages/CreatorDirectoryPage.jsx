import { useState, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { getPeople, getCategories, getFactions } from "../services/api";
import PersonCard from "../components/people/PersonCard";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";

export default function CreatorDirectoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchParam = searchParams.get("search") || "";
  const selectedFaction = searchParams.get("faction") || "all";

  const [people, setPeople] = useState([]);
  const [categories, setCategories] = useState([]);
  const [factions, setFactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter states
  const [searchTerm, setSearchTerm] = useState(searchParam);
  const [selectedCategory, setSelectedCategory] = useState("all");

  useEffect(() => {
    let isMounted = true;

    Promise.all([getPeople(), getCategories(), getFactions()])
      .then(([peopleData, categoriesData, factionsData]) => {
        if (isMounted) {
          setPeople(peopleData || []);
          setCategories(categoriesData || []);
          setFactions(factionsData || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err?.message || "Failed to load directory data.");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Handle faction filter selection via searchParams
  const handleFactionChange = (slug) => {
    const nextParams = new URLSearchParams(searchParams);
    if (slug === "all") {
      nextParams.delete("faction");
    } else {
      nextParams.set("faction", slug);
    }
    setSearchParams(nextParams);
  };

  // Reset all filters
  const resetFilters = () => {
    setSearchTerm("");
    setSelectedCategory("all");
    const nextParams = new URLSearchParams(searchParams);
    nextParams.delete("faction");
    nextParams.delete("search");
    setSearchParams(nextParams);
  };

  // Memoized filtered people list
  // NOTE: The person list API does NOT return memberships or platform_accounts.
  // Text search, category filtering, and bio search are done client-side.
  // Faction filtering is not possible with list data (memberships are omitted)
  // so it is a no-op until the detail data is available or the backend adds
  // a faction filter parameter. For now we keep the UI control but skip the
  // membership check when memberships are absent.
  const filteredPeople = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return people.filter((person) => {
      // 1. Text Search (Name, Bio, or Platform handle)
      if (query) {
        const matchesName = person.display_name?.toLowerCase().includes(query);
        const matchesBio = person.bio?.toLowerCase().includes(query);
        // platform_accounts may not be present in list responses
        const matchesHandle = person.platform_accounts?.some((acc) =>
          acc.handle?.toLowerCase().includes(query)
        );
        if (!matchesName && !matchesBio && !matchesHandle) {
          return false;
        }
      }

      // 2. Category Filter
      if (selectedCategory !== "all") {
        const hasCategory = person.categories?.some(
          (cat) => cat.slug === selectedCategory
        );
        if (!hasCategory) return false;
      }

      // 3. Faction Filter — only apply when memberships data is available
      if (selectedFaction !== "all" && person.memberships) {
        const currentMembership = person.memberships.find((m) => !m.ended_on);
        if (currentMembership?.faction?.slug !== selectedFaction) {
          return false;
        }
      }

      return true;
    });
  }, [people, searchTerm, selectedCategory, selectedFaction]);

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
              placeholder="Search by character name, bio, or handle..."
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
            onClick={() => setSelectedCategory("all")}
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
              onClick={() => setSelectedCategory(cat.slug)}
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
        ) : filteredPeople.length > 0 ? (
          <div>
            <div className="mb-4 flex items-center justify-between text-xs text-neutral-400">
              <span>
                Showing <strong className="text-neutral-200">{filteredPeople.length}</strong> profile
                {filteredPeople.length === 1 ? "" : "s"}
              </span>
              {(searchTerm || selectedCategory !== "all" || selectedFaction !== "all") && (
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
              {filteredPeople.map((person) => (
                <PersonCard key={person.id || person.slug} person={person} />
              ))}
            </div>
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
