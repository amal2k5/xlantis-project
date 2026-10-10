import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="mx-auto flex max-w-7xl flex-col items-center justify-center px-4 py-24 text-center sm:px-6 lg:px-8">
      <div className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-emerald-400">
        404 Error
      </div>
      <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-white sm:text-5xl">
        Citizen Not Found in Directory
      </h1>
      <p className="mt-3 max-w-md text-sm text-neutral-400">
        The profile, faction, or route you are looking for does not exist in the Xlantis database or may have moved.
      </p>
      <div className="mt-8 flex gap-4">
        <Link
          to="/"
          className="inline-flex items-center rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-neutral-950 transition-colors hover:bg-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-neutral-950"
        >
          Return to Home
        </Link>
        <Link
          to="/creators"
          className="inline-flex items-center rounded-lg border border-neutral-700 bg-neutral-800 px-4 py-2 text-sm font-semibold text-neutral-200 transition-colors hover:bg-neutral-700 focus:outline-none focus:ring-2 focus:ring-neutral-600"
        >
          Browse Directory
        </Link>
      </div>
    </div>
  );
}
