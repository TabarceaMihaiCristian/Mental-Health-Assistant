export function getHomePathForRole(role: string | null | undefined) {
  if (role === "admin") {
    return "/admin/dashboard";
  }

  if (role === "specialist") {
    return "/specialist/dashboard";
  }

  return "/app";
}
