import { Link } from "react-router-dom";

export default function PersonCard({ person }) {
  if (!person) return null;

  // Find active faction membership (ended_on is null)
  const currentMembership = person.memberships?.find((m) => !m.ended_on);
  const currentFaction = currentMembership?.faction;

  return (
    <article className="group relative flex flex-col justify-between rounded-xl border border-neutral-800/90 bg-neutral-900/60 p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-500/40 hover:bg-neutral-900/90 hover:shadow-lg hover:shadow-emerald-950/20">
      <div>
        {/* Top Header: Avatar + Featured & Faction Badges */}
        <div className="flex items-start justify-between gap-3">
          <div className="relative">
            <img
              src={person.avatar_url || "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=120&auto=format&fit=crop&q=80"}
              alt={person.display_name}
              width={56}
              height={56}
              loading="lazy"
              className="h-14 w-14 rounded-full border-2 border-neutral-800 object-cover transition-colors group-hover:border-emerald-500/60"
            />
            {person.is_featured && (
              <span
                title="Featured Creator"
                className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-neutral-950 shadow-sm"
              >
                <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </span>
            )}
          </div>

          {currentFaction && (
            <span
              className="inline-flex items-center rounded-md border border-neutral-700/80 bg-neutral-800/80 px-2.5 py-1 text-xs font-semibold text-neutral-200"
              style={{
                borderColor: currentFaction.color ? `${currentFaction.color}40` : undefined,
              }}
            >
              {currentFaction.tag && (
                <span className="mr-1 text-emerald-400 font-bold">[{currentFaction.tag}]</span>
              )}
              <span className="truncate max-w-[110px]">{currentFaction.name}</span>
            </span>
          )}
        </div>

        {/* Name and Categories */}
        <div className="mt-4">
          <h3 className="text-base font-bold text-white transition-colors group-hover:text-emerald-300">
            <Link
              to={`/person/${person.slug}`}
              className="focus:outline-none focus:underline"
            >
              {person.display_name}
            </Link>
          </h3>

          {/* Categories */}
          {person.categories && person.categories.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {person.categories.map((category) => (
                <span
                  key={category.id || category.slug}
                  className="rounded bg-neutral-800 px-2 py-0.5 text-[11px] font-medium text-neutral-400"
                >
                  {category.name}
                </span>
              ))}
            </div>
          )}

          {/* Bio Preview */}
          {person.bio && (
            <p className="mt-3 line-clamp-2 text-xs leading-relaxed text-neutral-400">
              {person.bio}
            </p>
          )}
        </div>
      </div>

      {/* Footer: Platforms & View Profile Action */}
      <div className="mt-5 flex items-center justify-between border-t border-neutral-800/80 pt-3">
        <div className="flex items-center gap-2">
          {person.platform_accounts?.slice(0, 3).map((acc) => (
            <a
              key={acc.id}
              href={acc.url}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`${acc.platform?.name} profile of ${person.display_name}`}
              className="flex h-7 items-center rounded bg-neutral-800/90 px-2 text-[11px] font-medium text-neutral-300 transition-colors hover:bg-emerald-500/20 hover:text-emerald-300 focus:outline-none focus:ring-1 focus:ring-emerald-400"
            >
              {acc.platform?.name}
            </a>
          ))}
        </div>

        <Link
          to={`/person/${person.slug}`}
          className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 inline-flex items-center gap-1 focus:outline-none focus:underline"
        >
          Profile
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </article>
  );
}
