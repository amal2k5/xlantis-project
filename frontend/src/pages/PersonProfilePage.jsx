import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getPersonBySlug } from "../services/api";
import Loading from "../components/common/Loading";

export default function PersonProfilePage() {
  const { slug } = useParams();
  const [personState, setPersonState] = useState({ slug: null, data: null, error: null });

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
                className="h-24 w-24 rounded-2xl border-2 border-emerald-500/40 object-cover shadow-lg shadow-black/40"
              />
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
                  to={`/creators?faction=${encodeURIComponent(faction.slug)}`}
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
              {person.platform_accounts.map((acc) => (
                <a
                  key={acc.id}
                  href={acc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between rounded-xl border border-neutral-800 bg-neutral-950/60 p-3.5 transition-all hover:border-emerald-500/40 hover:bg-neutral-950/90 hover:text-emerald-300"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-900 border border-neutral-800 text-emerald-400 font-bold text-xs">
                      {acc.platform?.name?.charAt(0) || "P"}
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-white">
                        {acc.platform?.name}
                      </div>
                      <div className="text-xs text-neutral-400">@{acc.handle}</div>
                    </div>
                  </div>
                  {acc.is_verified && (
                    <span
                      title="Verified Platform Handle"
                      className="rounded-full bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-medium text-emerald-400 border border-emerald-500/20"
                    >
                      Verified
                    </span>
                  )}
                </a>
              ))}
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
