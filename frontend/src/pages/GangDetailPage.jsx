import { useState, useEffect, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import { getFactionBySlug, getLiveStatuses } from "../services/api";
import PersonCard from "../components/people/PersonCard";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";

export default function GangDetailPage() {
  const { slug } = useParams();
  const [factionState, setFactionState] = useState({
    slug: null,
    data: null,
    error: null,
  });
  const [liveStatuses, setLiveStatuses] = useState([]);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    let isMounted = true;

    getFactionBySlug(slug)
      .then((data) => {
        if (isMounted) {
          setFactionState({ slug, data: data || null, error: null });
          setImgError(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setFactionState({
            slug,
            data: null,
            error: err?.message || "Failed to load gang details.",
          });
        }
      });

    return () => {
      isMounted = false;
    };
  }, [slug]);

  // Poll live statuses periodically (~60 seconds) to display live indicators for roster members
  useEffect(() => {
    let isMounted = true;
    let isFetching = false;

    const fetchLive = async () => {
      if (isFetching || !slug) return;
      isFetching = true;
      try {
        const statuses = await getLiveStatuses();
        if (isMounted && Array.isArray(statuses)) {
          setLiveStatuses(statuses);
        }
      } catch (err) {
        console.warn("Failed to fetch live statuses for gang roster:", err?.message || err);
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
  }, [slug]);

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

  const loading = factionState.slug !== slug;
  const faction = factionState.data;
  const error = factionState.error;

  if (loading) {
    return <Loading message="Loading gang details..." />;
  }

  // Network or server error
  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-white">Unable to Load Gang Details</h1>
        <p className="mt-2 text-sm text-neutral-400">{error}</p>
        <Link
          to="/gangs"
          className="mt-6 inline-flex items-center rounded-lg bg-emerald-500 px-4 py-2 text-xs font-semibold text-neutral-950 hover:bg-emerald-400"
        >
          &larr; Back to Gangs Directory
        </Link>
      </div>
    );
  }

  // Gang / Faction not found (404)
  if (!faction) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-white">Gang Not Found</h1>
        <p className="mt-2 text-sm text-neutral-400">
          The requested gang or faction &ldquo;{slug}&rdquo; could not be located in the directory.
        </p>
        <Link
          to="/gangs"
          className="mt-6 inline-flex items-center rounded-lg bg-emerald-500 px-4 py-2 text-xs font-semibold text-neutral-950 hover:bg-emerald-400"
        >
          &larr; Back to Gangs Directory
        </Link>
      </div>
    );
  }

  const members = Array.isArray(faction.members) ? faction.members : [];
  const memberCount =
    typeof faction.member_count === "number" ? faction.member_count : members.length;

  const statusColor =
    faction.status === "active"
      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      : "bg-neutral-800 text-neutral-400 border-neutral-700";

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Breadcrumb Navigation */}
      <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-xs text-neutral-400">
        <Link to="/" className="hover:text-emerald-400 transition-colors">
          Home
        </Link>
        <span>/</span>
        <Link to="/gangs" className="hover:text-emerald-400 transition-colors">
          Gangs & Factions
        </Link>
        <span>/</span>
        <span className="text-neutral-200 font-medium">{faction.name}</span>
      </nav>

      {/* Main Gang Header Card */}
      <section className="overflow-hidden rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 sm:p-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
            {/* Gang Logo / Insignia with Fallback */}
            <div className="relative flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl border-2 border-emerald-500/40 bg-neutral-950/80 shadow-lg shadow-black/40 overflow-hidden">
              {faction.logo_url && !imgError ? (
                <img
                  src={faction.logo_url}
                  alt={`${faction.name} insignia`}
                  width={96}
                  height={96}
                  loading="eager"
                  onError={() => setImgError(true)}
                  className="h-full w-full object-cover"
                />
              ) : (
                <span className="text-2xl font-black text-emerald-400 select-none">
                  {faction.tag || faction.name?.charAt(0) || "G"}
                </span>
              )}
            </div>

            {/* Name, Tag & Status */}
            <div>
              <div className="flex flex-wrap items-center gap-2.5">
                {faction.tag && (
                  <span className="rounded bg-neutral-800 px-2 py-0.5 text-xs font-bold text-emerald-400 border border-neutral-700/60">
                    [{faction.tag}]
                  </span>
                )}
                <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
                  {faction.name}
                </h1>
                <span
                  className={`rounded-full border px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${statusColor}`}
                >
                  {faction.status || "active"}
                </span>
              </div>

              {/* Member Count & Category */}
              <div className="mt-2 flex items-center gap-4 text-xs text-neutral-400">
                <span>
                  <strong className="text-white font-semibold">{memberCount}</strong>{" "}
                  {memberCount === 1 ? "Current Member" : "Current Members"}
                </span>
                <span>&bull;</span>
                <span>Xlantis RP Organization</span>
              </div>
            </div>
          </div>

          {/* Quick Action: Back to all gangs */}
          <div className="self-start">
            <Link
              to="/gangs"
              className="inline-flex items-center gap-1.5 rounded-xl border border-neutral-700 bg-neutral-800/80 px-3.5 py-2 text-xs font-medium text-neutral-200 transition-colors hover:border-emerald-500/50 hover:text-white"
            >
              &larr; All Factions
            </Link>
          </div>
        </div>

        {/* Description Section */}
        <div className="mt-6 border-t border-neutral-800/80 pt-5">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
            About the Organization
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-neutral-300 whitespace-pre-line">
            {faction.description || "No official description recorded for this faction."}
          </p>
        </div>
      </section>

      {/* Published Member Roster Section */}
      <section className="mt-10">
        <div className="flex items-center justify-between border-b border-neutral-800 pb-4">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Active Roster
            </div>
            <h2 className="mt-1 text-xl font-extrabold tracking-tight text-white sm:text-2xl">
              Faction Members ({memberCount})
            </h2>
          </div>
          <p className="hidden text-xs text-neutral-400 sm:block">
            Verified characters and streamers affiliated with {faction.name}
          </p>
        </div>

        <div className="mt-6">
          {members.length === 0 ? (
            <EmptyState
              title="No active members registered"
              description="This faction does not currently have any active members listed in the public directory."
            />
          ) : (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {members.map((member) => {
                const personData = member.person || {};
                const personForCard = {
                  ...personData,
                  platform_accounts: member.platform_accounts || [],
                  memberships: [
                    {
                      role: member.role,
                      started_on: member.started_on,
                      ended_on: member.ended_on,
                      faction: {
                        name: faction.name,
                        tag: faction.tag,
                      },
                    },
                  ],
                };

                return (
                  <div key={member.id || personData.id} className="flex flex-col">
                    {/* Role header above each member card */}
                    {member.role && (
                      <div className="mb-2 flex items-center justify-between px-1">
                        <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-emerald-400 border border-emerald-500/20">
                          {member.role}
                        </span>
                        {member.started_on && (
                          <span className="text-[11px] text-neutral-400">
                            Since {member.started_on}
                          </span>
                        )}
                      </div>
                    )}
                    <PersonCard
                      person={personForCard}
                      liveStatus={liveStatusMap[personData.slug]}
                    />
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
