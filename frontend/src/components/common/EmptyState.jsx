export default function EmptyState({
  title = "No results found",
  description = "Try adjusting your search query or filter settings.",
  actionLabel,
  onAction,
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-neutral-800 bg-neutral-900/40 px-6 py-14 text-center">
      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-neutral-800 bg-neutral-900 text-neutral-400">
        <svg
          className="h-6 w-6 text-neutral-500"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
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
      <h3 className="text-base font-semibold text-neutral-200">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-neutral-400">{description}</p>
      {actionLabel && onAction && (
        <button
          type="button"
          onClick={onAction}
          className="mt-4 inline-flex items-center rounded-lg border border-neutral-700 bg-neutral-800 px-3.5 py-1.5 text-xs font-medium text-neutral-200 transition-colors hover:border-emerald-500/50 hover:bg-neutral-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
