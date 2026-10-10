import { Link } from "react-router-dom";

const CURRENT_YEAR = new Date().getFullYear();

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-neutral-800/80 bg-[#07080b] py-8 text-neutral-400">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex flex-col items-center gap-1 text-center md:items-start md:text-left">
            <div className="flex items-center gap-2">
              <span className="font-bold text-neutral-200">XLANTIS RP</span>
              <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
                COMMUNITY DIRECTORY
              </span>
            </div>
            <p className="text-xs text-neutral-500">
              Community platform connecting roleplayers, streamers, and factions.
            </p>
          </div>

          <div className="flex items-center gap-6 text-xs text-neutral-400">
            <Link to="/" className="hover:text-emerald-400 transition-colors">
              Home
            </Link>
            <Link to="/creators" className="hover:text-emerald-400 transition-colors">
              Creators
            </Link>
            <Link to="/gangs" className="hover:text-emerald-400 transition-colors">
              Gangs & Factions
            </Link>
          </div>

          <div className="text-center text-xs text-neutral-500 md:text-right">
            &copy; {CURRENT_YEAR} Xlantis RP Community. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
