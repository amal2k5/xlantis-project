import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getFeaturedPeople, getFactions, getPeople } from "../services/api";
import PersonCard from "../components/people/PersonCard";
import FactionCard from "../components/factions/FactionCard";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";

export default function HomePage() {
  const navigate = useNavigate();
  const [searchInput, setSearchInput] = useState("");
  const [featuredPeople, setFeaturedPeople] = useState([]);
  const [factionsPreview, setFactionsPreview] = useState([]);
  const [allCreators, setAllCreators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    Promise.all([getFeaturedPeople(), getFactions(), getPeople()])
      .then(([featuredData, factionsData, peopleData]) => {
        if (isMounted) {
          setFeaturedPeople(featuredData || []);
          setFactionsPreview((factionsData || []).slice(0, 3));
          setAllCreators((peopleData || []).slice(0, 4));
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

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      navigate(`/creators?search=${encodeURIComponent(searchInput.trim())}`);
    } else {
      navigate("/creators");
    }
  };

  return (
    <div className="flex flex-col space-y-16 pb-16">
      {/* 1. Introductory Hero Section */}
      <section className="relative border-b border-neutral-800/80 bg-radial from-neutral-900/60 via-[#090a0f] to-[#090a0f] pt-14 pb-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            {/* Tagline Badge */}
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-1 text-xs font-semibold text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Xlantis Roleplay Hub
            </div>

            {/* Hero Heading */}
            <h1 className="mt-5 text-3xl font-extrabold tracking-tight text-white sm:text-5xl sm:leading-tight">
              Connect With Every Streamer & Gang in{" "}
              <span className="text-emerald-400">Xlantis RP</span>
            </h1>

            {/* Subheading */}
            <p className="mt-4 text-base text-neutral-400 sm:text-lg">
              The premier open directory for characters, syndicates, and content creators.
              Discover storylines, track live feeds, and explore faction affiliations.
            </p>

            {/* Hero Search Interface */}
            <form onSubmit={handleSearchSubmit} className="mt-8 mx-auto max-w-xl">
              <div className="relative flex items-center">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-neutral-400">
                  <svg
                    className="h-5 w-5"
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
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Search streamer, character, or faction..."
                  aria-label="Search directory"
                  className="w-full rounded-2xl border border-neutral-800 bg-neutral-900/90 py-3.5 pl-11 pr-28 text-sm text-neutral-100 placeholder-neutral-500 transition-colors focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 shadow-xl shadow-black/30"
                />
                <button
                  type="submit"
                  className="absolute right-1.5 rounded-xl bg-emerald-500 px-4 py-2 text-xs font-semibold text-neutral-950 transition-colors hover:bg-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  Search
                </button>
              </div>
            </form>

            {/* Quick Navigation CTAs */}
            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
              <Link
                to="/creators"
                className="rounded-xl bg-neutral-800 border border-neutral-700/80 px-4 py-2 text-xs font-semibold text-neutral-200 transition-colors hover:border-emerald-500/50 hover:text-white"
              >
                Browse All Profiles &rarr;
              </Link>
              <Link
                to="/gangs"
                className="rounded-xl bg-neutral-800 border border-neutral-700/80 px-4 py-2 text-xs font-semibold text-neutral-200 transition-colors hover:border-emerald-500/50 hover:text-white"
              >
                Explore Factions &rarr;
              </Link>
            </div>

            {/* Server Stats Indicators — static promotional text, not database counts */}
            <div className="mt-12 grid grid-cols-3 gap-3 border-t border-neutral-800/80 pt-8 text-center">
              <div>
                <div className="text-xl font-black text-white sm:text-2xl">Open</div>
                <div className="text-[11px] font-medium text-neutral-400 uppercase tracking-wider">
                  Community
                </div>
              </div>
              <div>
                <div className="text-xl font-black text-emerald-400 sm:text-2xl">Growing</div>
                <div className="text-[11px] font-medium text-neutral-400 uppercase tracking-wider">
                  Gangs & Orgs
                </div>
              </div>
              <div>
                <div className="text-xl font-black text-white sm:text-2xl">100%</div>
                <div className="text-[11px] font-medium text-neutral-400 uppercase tracking-wider">
                  Roleplay Focus
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Error Alert — shown if the API is unreachable */}
      {error && (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-sm text-red-300">
            <strong className="font-semibold">Connection error:</strong> {error}
          </div>
        </div>
      )}

      {/* 2. Featured People Section */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between border-b border-neutral-800 pb-4">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Spotlight
            </div>
            <h2 className="mt-1 text-xl font-extrabold tracking-tight text-white sm:text-2xl">
              Featured Roleplayers & Streamers
            </h2>
          </div>
          <Link
            to="/creators"
            className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1"
          >
            View all
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        <div className="mt-6">
          {loading ? (
            <Loading message="Loading featured personalities..." />
          ) : featuredPeople.length > 0 ? (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {featuredPeople.map((person) => (
                <PersonCard key={person.id || person.slug} person={person} />
              ))}
            </div>
          ) : (
            !error && (
              <EmptyState
                title="No featured profiles yet"
                description="Featured roleplayers and streamers will appear here once added to the directory."
              />
            )
          )}
        </div>
      </section>

      {/* 3. Gang Directory Preview Section */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex items-end justify-between border-b border-neutral-800 pb-4">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Underworld & Authority
            </div>
            <h2 className="mt-1 text-xl font-extrabold tracking-tight text-white sm:text-2xl">
              Factions & Gangs Preview
            </h2>
          </div>
          <Link
            to="/gangs"
            className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1"
          >
            View all factions
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        <div className="mt-6">
          {loading ? (
            <Loading message="Loading gangs..." />
          ) : factionsPreview.length > 0 ? (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {factionsPreview.map((faction) => (
                <FactionCard key={faction.id || faction.slug} faction={faction} />
              ))}
            </div>
          ) : (
            !error && (
              <EmptyState
                title="No factions registered yet"
                description="Gangs and organizations will appear here once added to the directory."
              />
            )
          )}
        </div>
      </section>

      {/* 4. Content Creator Section */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="rounded-2xl border border-neutral-800 bg-neutral-900/40 p-6 sm:p-10">
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div className="max-w-2xl">
              <span className="rounded-md bg-emerald-500/10 px-2 py-0.5 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
                MULTI-PLATFORM BROADCASTING
              </span>
              <h2 className="mt-3 text-2xl font-extrabold tracking-tight text-white">
                Never Miss an In-Character Stream
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-neutral-400">
                Whether streaming on Twitch, Kick, or archiving VODs on YouTube,
                the Xlantis Directory provides direct links to your favorite POV streamers.
                Follow crime arcs, court cases, and high-speed pursuits across perspectives.
              </p>
            </div>
            <div className="shrink-0">
              <Link
                to="/creators"
                className="inline-flex items-center rounded-xl bg-emerald-500 px-5 py-2.5 text-xs font-bold text-neutral-950 transition-colors hover:bg-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                Browse All Creators
              </Link>
            </div>
          </div>

          {allCreators.length > 0 && (
            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 border-t border-neutral-800/80 pt-6">
              {allCreators.map((creator) => (
                <div
                  key={creator.id}
                  className="flex items-center gap-3 rounded-lg border border-neutral-800/80 bg-neutral-950/40 p-3"
                >
                  <img
                    src={creator.avatar_url}
                    alt={creator.display_name}
                    width={40}
                    height={40}
                    loading="lazy"
                    className="h-10 w-10 rounded-full border border-neutral-700 object-cover"
                  />
                  <div className="min-w-0 flex-1">
                    <Link
                      to={`/person/${creator.slug}`}
                      className="block truncate text-xs font-bold text-white hover:text-emerald-400"
                    >
                      {creator.display_name}
                    </Link>
                    {/* platform_accounts are not available in list responses;
                        show categories as a compact fallback */}
                    <span className="text-[11px] text-neutral-400 truncate block">
                      {creator.platform_accounts?.[0]
                        ? `${creator.platform_accounts[0].platform?.name} @${creator.platform_accounts[0].handle}`
                        : creator.categories?.map((c) => c.name).join(", ") || "Creator"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
