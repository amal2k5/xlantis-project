import { Link } from "react-router-dom";

export default function FactionCard({ faction }) {
  if (!faction) return null;

  const statusColor =
    faction.status === "active"
      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      : "bg-neutral-800 text-neutral-400 border-neutral-700";

  return (
    <article className="group flex flex-col justify-between rounded-xl border border-neutral-800/90 bg-neutral-900/60 p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-500/40 hover:bg-neutral-900/90 hover:shadow-lg hover:shadow-emerald-950/20">
      <div>
        {/* Header: Tag + Name + Status */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            {faction.logo_url && (
              <img
                src={faction.logo_url}
                alt={`${faction.name} insignia`}
                width={48}
                height={48}
                loading="lazy"
                className="h-12 w-12 rounded-lg border border-neutral-800 object-cover"
              />
            )}
            <div>
              <div className="flex items-center gap-1.5">
                {faction.tag && (
                  <span className="rounded bg-neutral-800 px-1.5 py-0.5 text-xs font-bold text-emerald-400 border border-neutral-700/60">
                    {faction.tag}
                  </span>
                )}
                <h3 className="text-base font-bold text-white group-hover:text-emerald-300 transition-colors">
                  {faction.name}
                </h3>
              </div>
              {faction.member_count && (
                <span className="text-xs text-neutral-400">
                  {faction.member_count} Known Affiliates
                </span>
              )}
            </div>
          </div>

          <span
            className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${statusColor}`}
          >
            {faction.status}
          </span>
        </div>

        {/* Description */}
        <p className="mt-4 line-clamp-3 text-xs leading-relaxed text-neutral-400">
          {faction.description}
        </p>
      </div>

      {/* Action / View members */}
      <div className="mt-5 border-t border-neutral-800/80 pt-3 flex items-center justify-between">
        <span className="text-xs text-neutral-500">Faction Directory</span>
        <Link
          to={`/creators?faction=${encodeURIComponent(faction.slug)}`}
          className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400 hover:text-emerald-300 focus:outline-none focus:underline"
        >
          View Members
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </article>
  );
}
