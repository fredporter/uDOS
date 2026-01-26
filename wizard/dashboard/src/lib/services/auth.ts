export function getAdminToken(): string {
  if (typeof localStorage === "undefined") {
    return "";
  }
  return localStorage.getItem("wizardAdminToken") || "";
}

export function setAdminToken(token: string): void {
  if (typeof localStorage === "undefined") {
    return;
  }
  if (!token) {
    localStorage.removeItem("wizardAdminToken");
    return;
  }
  localStorage.setItem("wizardAdminToken", token);
}

export function buildAuthHeaders(token?: string): Record<string, string> {
  const resolved = token && token.trim() ? token.trim() : getAdminToken();
  return resolved ? { Authorization: `Bearer ${resolved}` } : {};
}
