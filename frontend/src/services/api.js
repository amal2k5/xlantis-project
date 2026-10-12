import axios from "axios";

// ---------------------------------------------------------------------------
// Axios Client
// ---------------------------------------------------------------------------

/**
 * Read API base URL from Vite environment variable.
 * In development the Vite proxy forwards /api/* to Django, so the default
 * relative path works without CORS.  In production set the full URL.
 */
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ---------------------------------------------------------------------------
// Error Helpers
// ---------------------------------------------------------------------------

/**
 * Custom error class for API failures.
 * Provides a user-safe message while keeping the original error accessible.
 */
export class ApiError extends Error {
  constructor(message, status = null, originalError = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.originalError = originalError;
  }
}

/**
 * Extract a user-safe error message from an Axios error.
 * Internal details and stack traces are never exposed.
 */
function handleApiError(error) {
  if (error.response) {
    const status = error.response.status;
    if (status === 404) {
      throw new ApiError("The requested resource was not found.", status, error);
    }
    if (status === 400) {
      // DRF validation errors — surface the detail when available
      const data = error.response.data;
      const detail =
        data?.detail ||
        (typeof data === "object" ? JSON.stringify(data) : "Invalid request.");
      throw new ApiError(detail, status, error);
    }
    if (status >= 500) {
      throw new ApiError(
        "The server encountered an error. Please try again later.",
        status,
        error,
      );
    }
    throw new ApiError("An unexpected error occurred.", status, error);
  }

  if (error.request) {
    // Request was made but no response received (network error, CORS, timeout)
    throw new ApiError(
      "Unable to reach the server. Please check your connection.",
      null,
      error,
    );
  }

  throw new ApiError("An unexpected error occurred.", null, error);
}

// ---------------------------------------------------------------------------
// Helper: unwrap paginated results
// ---------------------------------------------------------------------------

/**
 * DRF's PageNumberPagination wraps results in { count, next, previous, results }.
 * This helper extracts the results array, falling back to the raw data if the
 * response is not paginated (e.g. detail endpoints).
 */
function unwrapResults(responseData) {
  if (responseData && Array.isArray(responseData.results)) {
    return responseData.results;
  }
  // Non-paginated or raw array response
  if (Array.isArray(responseData)) {
    return responseData;
  }
  return responseData;
}

// ---------------------------------------------------------------------------
// Directory & People Services
// ---------------------------------------------------------------------------

/**
 * Fetch a paginated list of published persons.
 *
 * @param {Object}  [options]            - Query parameter options.
 * @param {string}  [options.search]     - Full-text search across name & bio.
 * @param {string}  [options.category]   - Filter by category slug.
 * @param {boolean} [options.featured]   - Filter by featured flag.
 * @param {number}  [options.page]       - Page number.
 * @param {number}  [options.page_size]  - Items per page.
 * @returns {Promise<Array>} Array of person list objects.
 */
export async function getPeople(options = {}) {
  try {
    const params = {};
    if (options.search) params.search = options.search;
    if (options.category) params.category = options.category;
    if (options.featured !== undefined) params.featured = options.featured;
    if (options.page) params.page = options.page;
    if (options.page_size) params.page_size = options.page_size;

    const response = await apiClient.get("/directory/persons/", { params });
    return unwrapResults(response.data);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    handleApiError(error);
  }
}

/**
 * Fetch only featured persons (convenience wrapper).
 * @returns {Promise<Array>} Array of featured person list objects.
 */
export async function getFeaturedPeople() {
  return getPeople({ featured: true });
}

/**
 * Fetch a single person detail by slug.
 *
 * Returns the full detail payload including memberships and platform_accounts.
 * Returns `null` when the profile is not found (404).
 *
 * @param {string} slug - The person's URL slug.
 * @returns {Promise<Object|null>}
 */
export async function getPersonBySlug(slug) {
  try {
    const response = await apiClient.get(`/directory/persons/${slug}/`);
    return response.data;
  } catch (error) {
    // Surface 404 as null so the profile page can show a "not found" state
    if (error.response && error.response.status === 404) {
      return null;
    }
    if (error instanceof ApiError) throw error;
    handleApiError(error);
  }
}

// ---------------------------------------------------------------------------
// Factions Services
// ---------------------------------------------------------------------------

/**
 * Fetch a paginated list of factions.
 *
 * @param {Object}  [options]            - Query parameter options.
 * @param {string}  [options.search]     - Search by name or tag.
 * @param {string}  [options.status]     - Filter by status (active, inactive, disbanded).
 * @param {number}  [options.page]       - Page number.
 * @param {number}  [options.page_size]  - Items per page.
 * @returns {Promise<Array>} Array of faction list objects.
 */
export async function getFactions(options = {}) {
  try {
    const params = {};
    if (options.search) params.search = options.search;
    if (options.status) params.status = options.status;
    if (options.page) params.page = options.page;
    if (options.page_size) params.page_size = options.page_size;

    const response = await apiClient.get("/directory/factions/", { params });
    return unwrapResults(response.data);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    handleApiError(error);
  }
}

/**
 * Fetch a single faction detail by slug.
 *
 * Returns null on 404.
 *
 * @param {string} slug - The faction's URL slug.
 * @returns {Promise<Object|null>}
 */
export async function getFactionBySlug(slug) {
  try {
    const response = await apiClient.get(`/directory/factions/${slug}/`);
    return response.data;
  } catch (error) {
    if (error.response && error.response.status === 404) {
      return null;
    }
    if (error instanceof ApiError) throw error;
    handleApiError(error);
  }
}

// ---------------------------------------------------------------------------
// Categories Services
// ---------------------------------------------------------------------------

/**
 * Fetch all active categories.
 * @returns {Promise<Array>} Array of category objects.
 */
export async function getCategories() {
  try {
    const response = await apiClient.get("/directory/categories/");
    return unwrapResults(response.data);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    handleApiError(error);
  }
}

// ---------------------------------------------------------------------------
// Platforms Services
// ---------------------------------------------------------------------------

/**
 * Fetch all active platforms.
 *
 * @param {Object}  [options]            - Query parameter options.
 * @param {number}  [options.page]       - Page number.
 * @param {number}  [options.page_size]  - Items per page.
 * @returns {Promise<Array>} Array of platform objects.
 */
export async function getPlatforms(options = {}) {
  try {
    const params = {};
    if (options.page) params.page = options.page;
    if (options.page_size) params.page_size = options.page_size;

    const response = await apiClient.get("/platforms/", { params });
    return unwrapResults(response.data);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    handleApiError(error);
  }
}

