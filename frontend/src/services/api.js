import axios from "axios";
import {
  getMockCategories,
  getMockFactions,
  getMockFactionBySlug,
  getMockFeaturedPeople,
  getMockPeople,
  getMockPersonBySlug,
} from "../data/mockData";

// Read API base URL from Vite environment variable
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Directory & People Services
 * Automatically fall back to mock data while Django endpoints are in development.
 */
export async function getPeople() {
  try {
    const response = await apiClient.get("/directory/people/");
    return response.data?.results || response.data;
  } catch {
    // Backend API is not yet live or returned error; return mock data
    return getMockPeople();
  }
}

export async function getFeaturedPeople() {
  try {
    const response = await apiClient.get("/directory/people/?featured=true");
    return response.data?.results || response.data;
  } catch {
    return getMockFeaturedPeople();
  }
}

export async function getPersonBySlug(slug) {
  try {
    const response = await apiClient.get(`/directory/people/${slug}/`);
    return response.data;
  } catch {
    return getMockPersonBySlug(slug);
  }
}

/**
 * Factions Services
 */
export async function getFactions() {
  try {
    const response = await apiClient.get("/directory/factions/");
    return response.data?.results || response.data;
  } catch {
    return getMockFactions();
  }
}

export async function getFactionBySlug(slug) {
  try {
    const response = await apiClient.get(`/directory/factions/${slug}/`);
    return response.data;
  } catch {
    return getMockFactionBySlug(slug);
  }
}

/**
 * Categories Services
 */
export async function getCategories() {
  try {
    const response = await apiClient.get("/directory/categories/");
    return response.data?.results || response.data;
  } catch {
    return getMockCategories();
  }
}
