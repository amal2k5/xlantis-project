import { useState } from "react";
import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Creators & Profiles", path: "/creators" },
    { name: "Gangs & Factions", path: "/gangs" },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-neutral-800/80 bg-[#090a0f]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Brand */}
        <Link
          to="/"
          className="group flex items-center gap-2.5 transition-opacity focus:outline-none focus:ring-2 focus:ring-emerald-500/50 rounded-lg p-1"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-black tracking-wider text-sm transition-colors group-hover:border-emerald-400">
            X
          </div>
          <div className="flex flex-col">
            <span className="text-base font-bold tracking-tight text-white group-hover:text-emerald-300 transition-colors">
              XLANTIS <span className="text-emerald-400 font-extrabold">RP</span>
            </span>
            <span className="text-[10px] uppercase tracking-widest text-neutral-400 font-medium">
              Directory
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav aria-label="Main Navigation" className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `rounded-lg px-3.5 py-1.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : "text-neutral-300 hover:bg-neutral-900 hover:text-white"
                }`
              }
            >
              {link.name}
            </NavLink>
          ))}
        </nav>

        {/* Status indicator on desktop */}
        <div className="hidden sm:flex items-center gap-2.5 text-xs text-neutral-400">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-medium text-neutral-300">City Online</span>
        </div>

        {/* Mobile menu button */}
        <button
          type="button"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-expanded={mobileMenuOpen}
          aria-label="Toggle navigation menu"
          className="flex md:hidden rounded-lg p-2 text-neutral-400 hover:bg-neutral-900 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <svg
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            {mobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <nav aria-label="Mobile Navigation" className="border-t border-neutral-800 bg-[#0c0e14] px-4 py-3 md:hidden">
          <div className="flex flex-col space-y-1">
            {navLinks.map((link) => (
              <NavLink
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium ${
                    isActive
                      ? "bg-emerald-500/15 text-emerald-400 font-semibold"
                      : "text-neutral-300 hover:bg-neutral-900 hover:text-white"
                  }`
                }
              >
                {link.name}
              </NavLink>
            ))}
          </div>
        </nav>
      )}
    </header>
  );
}
