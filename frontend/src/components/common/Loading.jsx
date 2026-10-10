export default function Loading({ message = "Loading directory data..." }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col items-center justify-center py-16 text-center"
    >
      <div className="relative mb-4 h-10 w-10">
        <div className="absolute inset-0 rounded-full border-2 border-emerald-500/20"></div>
        <div className="absolute inset-0 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent"></div>
      </div>
      <p className="text-sm font-medium text-neutral-400">{message}</p>
      <span className="sr-only">Loading</span>
    </div>
  );
}
