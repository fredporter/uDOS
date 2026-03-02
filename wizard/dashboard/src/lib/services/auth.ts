/**
 * Authentication services for the Wizard dashboard
 */

/**
 * Get admin token from localStorage
 */
export function getAdminToken(): string {
  if (typeof localStorage === "undefined") return "";
  return localStorage.getItem("wizardAdminToken") || "";
}

/**
 * Set admin token in localStorage
 */
export function setAdminToken(token: string): void {
  if (typeof localStorage !== "undefined") {
    if (token) {
      localStorage.setItem("wizardAdminToken", token);
    } else {
      localStorage.removeItem("wizardAdminToken");
    }
  }
}

/**
 * Clear admin token from localStorage
 */
export function clearAdminToken(): void {
  if (typeof localStorage !== "undefined") {
    localStorage.removeItem("wizardAdminToken");
  }
}

/**
 * Build authorization headers for API requests
 */
export function buildAuthHeaders(token?: string): Record<string, string> {
  const authToken = token || getAdminToken();
  if (!authToken) return {};
  return {
    Authorization: `Bearer ${authToken}`,
  };
}

/**
 * Check if admin token is available and valid
 */
export function hasAdminToken(): boolean {
  return getAdminToken().length > 0;
}

/**
 * Token validation - check expiry and validity from server
 */
export async function validateAdminToken(token?: string): Promise<boolean> {
  const authToken = token || getAdminToken();
  if (!authToken) return false;

  try {
    const response = await fetch("/api/admin-token/validate", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${authToken}`,
        "Content-Type": "application/json",
      },
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Get token status from server
 */
export async function getTokenStatus(): Promise<{ valid: boolean; hasToken: boolean }> {
  try {
    const response = await fetch("/api/admin-token/status");
    if (response.ok) {
      const data = await response.json();
      return {
        valid: data.token_valid === true,
        hasToken: data.has_token === true,
      };
    }
  } catch {
    // Silent fail - endpoint may not be available
  }
  return { valid: false, hasToken: false };
}
