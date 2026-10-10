/**
 * Mock data module for Xlantis RP Streamer & Content Directory.
 * Matches backend Django models (Person, Category, Faction, Membership, Platform, PlatformAccount).
 */

export const mockCategories = [
  {
    id: 1,
    name: "Gang Member",
    slug: "gang-member",
    description: "Affiliated with criminal syndicates and street organizations.",
    sort_order: 1,
    is_active: true,
  },
  {
    id: 2,
    name: "Law Enforcement",
    slug: "law-enforcement",
    description: "Officers and detectives protecting Los Santos.",
    sort_order: 2,
    is_active: true,
  },
  {
    id: 3,
    name: "EMS & Medical",
    slug: "ems-medical",
    description: "Paramedics, doctors, and first responders.",
    sort_order: 3,
    is_active: true,
  },
  {
    id: 4,
    name: "Content Creator",
    slug: "content-creator",
    description: "Full-time streamers and community video producers.",
    sort_order: 4,
    is_active: true,
  },
  {
    id: 5,
    name: "Street Racer",
    slug: "street-racer",
    description: "Underground midnight racers and tuning specialists.",
    sort_order: 5,
    is_active: true,
  },
  {
    id: 6,
    name: "Civilian / Business",
    slug: "civilian-business",
    description: "Entrepreneurs, club owners, and civilian citizens.",
    sort_order: 6,
    is_active: true,
  },
];

export const mockPlatforms = [
  {
    id: 1,
    name: "Twitch",
    slug: "twitch",
    kind: "livestream",
    supports_live: true,
    url_template: "https://twitch.tv/{handle}",
  },
  {
    id: 2,
    name: "Kick",
    slug: "kick",
    kind: "livestream",
    supports_live: true,
    url_template: "https://kick.com/{handle}",
  },
  {
    id: 3,
    name: "YouTube",
    slug: "youtube",
    kind: "video",
    supports_live: true,
    url_template: "https://youtube.com/@{handle}",
  },
  {
    id: 4,
    name: "X (Twitter)",
    slug: "x",
    kind: "social",
    supports_live: false,
    url_template: "https://x.com/{handle}",
  },
];

export const mockFactions = [
  {
    id: 1,
    name: "The Syndicate",
    slug: "the-syndicate",
    tag: "SYN",
    description:
      "A disciplined criminal syndicate controlling ports, weapons transit, and illicit high-stakes operations across southern Los Santos.",
    logo_url: "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=300&auto=format&fit=crop&q=80",
    status: "active",
    member_count: 14,
    color: "#10b981", // Emerald accent
  },
  {
    id: 2,
    name: "Redline Racers",
    slug: "redline-racers",
    tag: "RLR",
    description:
      "The premier underground car club commanding the midnight expressway sprints, pink-slip battles, and mechanic chop shops.",
    logo_url: "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=300&auto=format&fit=crop&q=80",
    status: "active",
    member_count: 11,
    color: "#f59e0b",
  },
  {
    id: 3,
    name: "Los Santos Police Department",
    slug: "los-santos-police-department",
    tag: "LSPD",
    description:
      "The metropolitan policing agency defending civilians, intercepting narcotics, and carrying out tactical SWAT raids citywide.",
    logo_url: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=300&auto=format&fit=crop&q=80",
    status: "active",
    member_count: 22,
    color: "#3b82f6",
  },
  {
    id: 4,
    name: "Viper Motorcycle Club",
    slug: "viper-motorcycle-club",
    tag: "VMC",
    description:
      "A ruthless 1% outlaw motorcycle gang reigning over the Sandy Shores desert and Blaine County weapons trade.",
    logo_url: "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=300&auto=format&fit=crop&q=80",
    status: "active",
    member_count: 9,
    color: "#ef4444",
  },
  {
    id: 5,
    name: "Midnight Dynasty",
    slug: "midnight-dynasty",
    tag: "MD",
    description:
      "Luxury nightclub moguls and high-society fixers balancing VIP legal businesses with high-level money laundering.",
    logo_url: "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=300&auto=format&fit=crop&q=80",
    status: "active",
    member_count: 8,
    color: "#8b5cf6",
  },
];

export const mockPeople = [
  {
    id: 1,
    display_name: "Marcus 'Ghost' Vance",
    slug: "marcus-ghost-vance",
    bio: "Commander of The Syndicate. Notorious for calm tactical execution, discreet logistical networks, and ruthlessly protecting his crew during server-wide heists.",
    avatar_url: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&auto=format&fit=crop&q=80",
    status: "published",
    is_featured: true,
    categories: [mockCategories[0], mockCategories[3]], // Gang Member, Content Creator
    memberships: [
      {
        id: 101,
        role: "leader",
        started_on: "2025-02-01",
        ended_on: null,
        faction: mockFactions[0], // The Syndicate
      },
    ],
    platform_accounts: [
      {
        id: 201,
        platform: mockPlatforms[0], // Twitch
        handle: "GhostVanceRP",
        url: "https://twitch.tv/GhostVanceRP",
        is_verified: true,
      },
      {
        id: 202,
        platform: mockPlatforms[3], // X
        handle: "GhostVance",
        url: "https://x.com/GhostVance",
        is_verified: true,
      },
    ],
  },
  {
    id: 2,
    display_name: "Elena 'Red' Rostova",
    slug: "elena-red-rostova",
    bio: "Head mechanic and drift captain of Redline Racers. Known for legendary police chases, bespoke vehicle tuning, and organizing high-risk midnight tournaments.",
    avatar_url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&auto=format&fit=crop&q=80",
    status: "published",
    is_featured: true,
    categories: [mockCategories[4], mockCategories[3]], // Street Racer, Content Creator
    memberships: [
      {
        id: 102,
        role: "leader",
        started_on: "2025-03-10",
        ended_on: null,
        faction: mockFactions[1], // Redline Racers
      },
    ],
    platform_accounts: [
      {
        id: 203,
        platform: mockPlatforms[1], // Kick
        handle: "ElenaRedLive",
        url: "https://kick.com/ElenaRedLive",
        is_verified: true,
      },
      {
        id: 204,
        platform: mockPlatforms[2], // YouTube
        handle: "ElenaRedVODs",
        url: "https://youtube.com/@ElenaRedVODs",
        is_verified: false,
      },
    ],
  },
  {
    id: 3,
    display_name: "Captain Nathan Drake",
    slug: "captain-nathan-drake",
    bio: "Head of LSPD Tactical Operations. A veteran law officer pursuing organized crime networks with discipline, thorough investigations, and fair roleplay ethics.",
    avatar_url: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300&auto=format&fit=crop&q=80",
    status: "published",
    is_featured: true,
    categories: [mockCategories[1], mockCategories[3]], // Law Enforcement, Content Creator
    memberships: [
      {
        id: 103,
        role: "leader",
        started_on: "2024-11-15",
        ended_on: null,
        faction: mockFactions[2], // LSPD
      },
    ],
    platform_accounts: [
      {
        id: 205,
        platform: mockPlatforms[0], // Twitch
        handle: "CaptDrakeRP",
        url: "https://twitch.tv/CaptDrakeRP",
        is_verified: true,
      },
    ],
  },
  {
    id: 4,
    display_name: "Jax 'Grim' Callahan",
    slug: "jax-grim-callahan",
    bio: "President of Viper Motorcycle Club. Enforces desert boundaries with heavy iron and deep loyalty. A cornerstone of northern county roleplay drama.",
    avatar_url: "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=300&auto=format&fit=crop&q=80",
    status: "published",
    is_featured: false,
    categories: [mockCategories[0]], // Gang Member
    memberships: [
      {
        id: 104,
        role: "leader",
        started_on: "2024-09-01",
        ended_on: null,
        faction: mockFactions[3], // Viper MC
      },
    ],
    platform_accounts: [
      {
        id: 206,
        platform: mockPlatforms[0], // Twitch
        handle: "JaxGrimRP",
        url: "https://twitch.tv/JaxGrimRP",
        is_verified: true,
      },
      {
        id: 207,
        platform: mockPlatforms[1], // Kick
        handle: "JaxGrim",
        url: "https://kick.com/JaxGrim",
        is_verified: false,
      },
    ],
  },
  {
    id: 5,
    display_name: "Victoria 'Vee' Chen",
    slug: "victoria-vee-chen",
    bio: "Proprietor of the Velvet Room and Midnight Dynasty director. Master of high-stakes mediation, luxury corporate fronts, and insider intelligence.",
    avatar_url: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&auto=format&fit=crop&q=80",
    status: "published",
    is_featured: true,
    categories: [mockCategories[5], mockCategories[3]], // Civilian / Business, Content Creator
    memberships: [
      {
        id: 105,
        role: "leader",
        started_on: "2025-01-10",
        ended_on: null,
        faction: mockFactions[4], // Midnight Dynasty
      },
    ],
    platform_accounts: [
      {
        id: 208,
        platform: mockPlatforms[0], // Twitch
        handle: "VeeChenRP",
        url: "https://twitch.tv/VeeChenRP",
        is_verified: true,
      },
      {
        id: 209,
        platform: mockPlatforms[2], // YouTube
        handle: "VeeChenClips",
        url: "https://youtube.com/@VeeChenClips",
        is_verified: true,
      },
    ],
  },
  {
    id: 6,
    display_name: "Officer Maya Lindqvist",
    slug: "officer-maya-lindqvist",
    bio: "Traffic enforcement and pursuit interception specialist. Known for high-speed highway chases and sharp tactical radio calls.",
    avatar_url: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&auto=format&fit=crop&q=80",
    status: "published",
    is_featured: false,
    categories: [mockCategories[1], mockCategories[3]], // Law Enforcement, Content Creator
    memberships: [
      {
        id: 106,
        role: "member",
        started_on: "2025-04-01",
        ended_on: null,
        faction: mockFactions[2], // LSPD
      },
    ],
    platform_accounts: [
      {
        id: 210,
        platform: mockPlatforms[1], // Kick
        handle: "MayaL_Officer",
        url: "https://kick.com/MayaL_Officer",
        is_verified: false,
      },
    ],
  },
  {
    id: 7,
    display_name: "Dante 'Apex' Silva",
    slug: "dante-apex-silva",
    bio: "Precision getaway driver for The Syndicate. Veteran wheelman who never misses an extraction rendezvous even under 10-code helicopter pursuit.",
    avatar_url: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&auto=format&fit=crop&q=80",
    status: "published",
    is_featured: false,
    categories: [mockCategories[0], mockCategories[4]], // Gang Member, Street Racer
    memberships: [
      {
        id: 107,
        role: "member",
        started_on: "2025-02-15",
        ended_on: null,
        faction: mockFactions[0], // The Syndicate
      },
    ],
    platform_accounts: [
      {
        id: 211,
        platform: mockPlatforms[0], // Twitch
        handle: "ApexSilvaLive",
        url: "https://twitch.tv/ApexSilvaLive",
        is_verified: true,
      },
    ],
  },
  {
    id: 8,
    display_name: "Kai 'Specter' Thorne",
    slug: "kai-specter-thorne",
    bio: "Independent roleplay streamer, documentary creator, and city storyteller uncovering underground narratives and political shifting in Xlantis.",
    avatar_url: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=300&auto=format&fit=crop&q=80",
    status: "published",
    is_featured: true,
    categories: [mockCategories[3], mockCategories[5]], // Content Creator, Civilian / Business
    memberships: [],
    platform_accounts: [
      {
        id: 212,
        platform: mockPlatforms[0], // Twitch
        handle: "SpecterKai",
        url: "https://twitch.tv/SpecterKai",
        is_verified: true,
      },
      {
        id: 213,
        platform: mockPlatforms[2], // YouTube
        handle: "SpecterChronicles",
        url: "https://youtube.com/@SpecterChronicles",
        is_verified: true,
      },
    ],
  },
];

// Helper functions for mock data retrieval
export function getMockPeople() {
  return mockPeople;
}

export function getMockFeaturedPeople() {
  return mockPeople.filter((p) => p.is_featured);
}

export function getMockPersonBySlug(slug) {
  return mockPeople.find((p) => p.slug === slug) || null;
}

export function getMockFactions() {
  return mockFactions;
}

export function getMockFactionBySlug(slug) {
  return mockFactions.find((f) => f.slug === slug) || null;
}

export function getMockCategories() {
  return mockCategories;
}
