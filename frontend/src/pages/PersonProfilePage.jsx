import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getPersonBySlug, getLiveStatuses } from "../services/api";
import Loading from "../components/common/Loading";

function formatViewerCount(count) {
  if (typeof count !== "number" || isNaN(count) || count < 0) return null;
  if (count >= 1_000_000) {
    return `${(count / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  }
  if (count >= 1_000) {
    return `${(count / 1_000).toFixed(1).replace(/\.0$/, "")}K`;
  }
  return count.toLocaleString();
}

function getPlatformDisplayName(platform) {
  if (!platform) return "Live";
  const map = {
    kick: "Kick",
    youtube: "YouTube",
    twitch: "Twitch",
    x: "X",
    facebook: "Facebook",
    discord: "Discord",
    tiktok: "TikTok",
  };
  return map[platform.toLowerCase()] || platform.charAt(0).toUpperCase() + platform.slice(1);
}

function formatStreamStartTime(dateString) {
  if (!dateString) return null;
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return null;
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return null;
  }
}

export default function PersonProfilePage() {
  const { slug } = useParams();
  const [personState, setPersonState] = useState({ slug: null, data: null, error: null });
  const [liveStatus, setLiveStatus] = useState(null);

  useEffect(() => {
    let isMounted = true;

    getPersonBySlug(slug)
      .then((data) => {
        if (isMounted) {
          setPersonState({ slug, data: data || null, error: null });
        }
      })
      .catch((err) => {
        if (isMounted) {
          setPersonState({
            slug,
            data: null,
            error: err?.message || "Failed to load profile.",
          });
        }
      });

    return () => {
      isMounted = false;
    };
  }, [slug]);

  // Poll live status for this profile periodically (~60 seconds)
  useEffect(() => {
    let isMounted = true;
    let isFetching = false;

    const fetchLive = async () => {
      if (isFetching || !slug) return;
      isFetching = true;
      try {
        const statuses = await getLiveStatuses();
        if (isMounted && Array.isArray(statuses)) {
          const match = statuses.find((s) => s?.person_slug === slug) || null;
          setLiveStatus(match);
        }
      } catch (err) {
        console.warn("Failed to fetch live status for profile:", err?.message || err);
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

  const loading = personState.slug !== slug;
  const person = personState.data;
  const error = personState.error;

  if (loading) {
    return <Loading message="Loading profile details..." />;
  }

  // Network / server error (distinct from "not found")
  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-white">Unable to Load Profile</h1>
        <p className="mt-2 text-sm text-neutral-400">{error}</p>
        <Link
          to="/creators"
          className="mt-6 inline-flex items-center rounded-lg bg-emerald-500 px-4 py-2 text-xs font-semibold text-neutral-950 hover:bg-emerald-400"
        >
          &larr; Back to Creators Directory
        </Link>
      </div>
    );
  }

  // Profile not found (404 or null response)
  if (!person) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-white">Profile Not Found</h1>
        <p className="mt-2 text-sm text-neutral-400">
          The requested profile &ldquo;{slug}&rdquo; could not be located in the directory.
        </p>
        <Link
          to="/creators"
          className="mt-6 inline-flex items-center rounded-lg bg-emerald-500 px-4 py-2 text-xs font-semibold text-neutral-950 hover:bg-emerald-400"
        >
          &larr; Back to Creators Directory
        </Link>
      </div>
    );
  }

  const currentMembership = person.memberships?.find((m) => !m.ended_on);
  const faction = currentMembership?.faction;

  const isLive = Boolean(liveStatus && liveStatus.is_live);
  const platformName = isLive ? getPlatformDisplayName(liveStatus.platform) : null;
  const formattedViewers = isLive ? formatViewerCount(liveStatus.viewer_count) : null;
  const formattedStartTime = isLive ? formatStreamStartTime(liveStatus.stream_started_at) : null;

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      {/* Breadcrumb Navigation */}
      <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-xs text-neutral-400">
        <Link to="/" className="hover:text-emerald-400 transition-colors">
          Home
        </Link>
        <span>/</span>
        <Link to="/creators" className="hover:text-emerald-400 transition-colors">
          Creators & Profiles
        </Link>
        <span>/</span>
        <span className="text-neutral-200 font-medium">{person.display_name}</span>
      </nav>

      {/* Main Profile Header Card */}
      <div className="overflow-hidden rounded-2xl border border-neutral-800 bg-neutral-900/60 p-6 sm:p-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
            {/* Avatar */}
            <div className="relative">
              <img
                src={
                  person.avatar_url ||
                  "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=240&auto=format&fit=crop&q=80"
                }
                alt={person.display_name}
                width={96}
                height={96}
                loading="eager"
                className={`h-24 w-24 rounded-2xl border-2 object-cover shadow-lg shadow-black/40 ${
                  isLive
                    ? "border-red-500 ring-2 ring-red-500/40 shadow-red-500/20"
                    : "border-emerald-500/40"
                }`}
              />
              {isLive && (
                <span
                  title={`Live on ${platformName}`}
                  className="absolute -top-2 -right-2 rounded-md bg-red-600 px-1.5 py-0.5 text-[10px] font-black uppercase text-white shadow-md animate-pulse"
                >
                  LIVE
                </span>
              )}
              {person.is_featured && (
                <span
                  title="Featured"
                  className="absolute -bottom-2 -right-2 rounded-md bg-emerald-500 px-1.5 py-0.5 text-[10px] font-bold text-neutral-950 uppercase"
                >
                  Featured
                </span>
              )}
            </div>

            {/* Name, Status & Categories */}
            <div>
              <div className="flex flex-wrap items-center gap-2.5">
                <h1 className="text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
                  {person.display_name}
                </h1>
                <span className="rounded-full border border-neutral-700 bg-neutral-800/80 px-2 py-0.5 text-[10px] font-semibold uppercase text-emerald-400">
                  {person.status || "Published"}
                </span>
                {isLive ? (
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-red-500/30 bg-red-500/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-red-400">
                    <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
                    LIVE ON {platformName.toUpperCase()}
                  </span>
                ) : (
                  liveStatus && (
                    <span className="rounded-full border border-neutral-700 bg-neutral-800/80 px-2.5 py-0.5 text-[10px] font-semibold uppercase text-neutral-400">
                      Offline
                    </span>
                  )
                )}
              </div>

              {/* Categories */}
              {person.categories && person.categories.length > 0 && (
                <div className="mt-2.5 flex flex-wrap gap-1.5">
                  {person.categories.map((cat) => (
                    <span
                      key={cat.id || cat.slug}
                      className="rounded-md border border-neutral-800 bg-neutral-800/60 px-2.5 py-0.5 text-xs font-medium text-neutral-300"
                    >
                      {cat.name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quick Faction Badge on Header if Active */}
          {faction && (
            <div className="self-start rounded-xl border border-neutral-800 bg-neutral-900/90 p-3.5 sm:text-right">
              <span className="text-[11px] font-medium uppercase tracking-wider text-neutral-400">
                Current Affiliation
              </span>
              <div className="mt-1 flex items-center gap-2 sm:justify-end">
                {faction.tag && (
                  <span className="rounded bg-neutral-800 px-1.5 py-0.5 text-xs font-bold text-emerald-400">
                    [{faction.tag}]
                  </span>
                )}
                <span className="font-bold text-white">{faction.name}</span>
              </div>
              <p className="mt-0.5 text-xs text-emerald-400 capitalize">
                Role: {currentMembership.role}
              </p>
            </div>
          )}
        </div>

        {/* Live Broadcast Spotlight Banner */}
        {isLive && (
          <div className="mt-8 rounded-xl border border-red-500/30 bg-red-500/10 p-5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded bg-red-600 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white">
                  <span className="h-1.5 w-1.5 rounded-full bg-white animate-pulse" />
                  LIVE NOW
                </span>
                <span className="text-xs font-bold text-red-400 uppercase tracking-wide">
                  {platformName}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-xs text-neutral-300">
                {formattedViewers && (
                  <span className="font-semibold text-white">
                    {formattedViewers} viewers
                  </span>
                )}
                {formattedStartTime && (
                  <span className="text-neutral-400">
                    Started at {formattedStartTime}
                  </span>
                )}
              </div>
            </div>
            {liveStatus.stream_title && (
              <h3 className="mt-3 text-sm font-semibold text-white sm:text-base">
                {liveStatus.stream_title}
              </h3>
            )}
          </div>
        )}

        {/* Biography Section */}
        <div className="mt-8 border-t border-neutral-800/80 pt-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-neutral-300">
            Character Background & Biography
          </h2>
          <div className="mt-3 text-sm leading-relaxed text-neutral-300 whitespace-pre-line">
            {person.bio || "No biography provided for this profile."}
          </div>
        </div>

        {/* Faction & Membership Details */}
        {faction && (
          <div className="mt-8 border-t border-neutral-800/80 pt-6">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-neutral-300">
              Faction Overview
            </h2>
            <div className="mt-3 rounded-xl border border-neutral-800/80 bg-neutral-950/50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-white text-base">
                    {faction.name} {faction.tag ? `[${faction.tag}]` : ""}
                  </h3>
                  <p className="mt-1 text-xs text-neutral-400">{faction.description}</p>
                </div>
                <Link
                  to={`/gangs/${encodeURIComponent(faction.slug)}`}
                  className="ml-4 shrink-0 rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-1.5 text-xs font-medium text-neutral-200 hover:border-emerald-500/50 hover:text-white"
                >
                  View Roster
                </Link>
              </div>
              {currentMembership.started_on && (
                <div className="mt-3 text-[11px] text-neutral-400 border-t border-neutral-800/60 pt-2">
                  Active Member since{" "}
                  <time dateTime={currentMembership.started_on} className="text-neutral-300">
                    {currentMembership.started_on}
                  </time>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Platform Account Links */}
        <div className="mt-8 border-t border-neutral-800/80 pt-6">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-neutral-300">
            Streaming & Content Channels
          </h2>
          {person.platform_accounts && person.platform_accounts.length > 0 ? (
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3">
              {person.platform_accounts.map((acc) => {
                const isAccLive =
                  isLive &&
                  (acc.handle?.toLowerCase() === liveStatus?.handle?.toLowerCase() ||
                    acc.platform?.slug?.toLowerCase() === liveStatus?.platform?.toLowerCase());
                return (
                  <a
                    key={acc.id}
                    href={acc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={`${acc.platform?.name} profile of ${person.display_name}${isAccLive ? " (Live now)" : ""}`}
                    className={`flex items-center justify-between rounded-xl border p-3.5 transition-all ${
                      isAccLive
                        ? "border-red-500/40 bg-red-950/20 hover:border-red-500/60 hover:bg-red-950/40 text-red-300"
                        : "border-neutral-800 bg-neutral-950/60 hover:border-emerald-500/40 hover:bg-neutral-950/90 hover:text-emerald-300"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-9 w-9 items-center justify-center rounded-lg border font-bold text-xs ${
                          isAccLive
                            ? "border-red-500/40 bg-red-900/40 text-red-400"
                            : "border-neutral-800 bg-neutral-900 text-emerald-400"
                        }`}
                      >
                        {acc.platform?.name?.charAt(0) || "P"}
                      </div>
                      <div>
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-white">
                          <span>{acc.platform?.name}</span>
                          {isAccLive && (
                            <span className="inline-flex items-center gap-1 rounded bg-red-600 px-1.5 py-0.2 text-[9px] font-bold uppercase text-white">
                              <span className="h-1 w-1 rounded-full bg-white animate-pulse" />
                              LIVE
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-neutral-400">@{acc.handle}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {isAccLive && formattedViewers && (
                        <span className="rounded-full border border-red-500/30 bg-red-500/10 px-2 py-0.5 text-[10px] font-semibold text-red-300">
                          {formattedViewers} viewers
                        </span>
                      )}
                      {acc.is_verified && (
                        <span
                          title="Verified Platform Handle"
                          className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-medium text-emerald-400"
                        >
                          Verified
                        </span>
                      )}
                    </div>
                  </a>
                );
              })}
            </div>
          ) : (
            <p className="mt-2 text-xs text-neutral-400">
              No public platform handles linked to this account yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
