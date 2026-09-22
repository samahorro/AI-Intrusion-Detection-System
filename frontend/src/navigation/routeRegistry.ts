export type FrontendOwner = "robert" | "kevin";

export type RouteArea =
  | "authentication"
  | "account"
  | "administration"
  | "monitoring";

export type AppRouteDefinition = {
  id: string;
  path: string;
  label: string;
  owner: FrontendOwner;
  area: RouteArea;
  requiresAuth: boolean;
  showInPrimaryNavigation: boolean;
};

export const appRouteRegistry: readonly AppRouteDefinition[] = [
  {
    id: "login",
    path: "/login",
    label: "Sign in",
    owner: "robert",
    area: "authentication",
    requiresAuth: false,
    showInPrimaryNavigation: false,
  },
  {
    id: "dashboard",
    path: "/dashboard",
    label: "Dashboard",
    owner: "kevin",
    area: "monitoring",
    requiresAuth: true,
    showInPrimaryNavigation: true,
  },
  {
    id: "alerts",
    path: "/alerts",
    label: "Alerts",
    owner: "kevin",
    area: "monitoring",
    requiresAuth: true,
    showInPrimaryNavigation: true,
  },
  {
    id: "account",
    path: "/account",
    label: "Account",
    owner: "robert",
    area: "account",
    requiresAuth: true,
    showInPrimaryNavigation: true,
  },
  {
    id: "admin-users",
    path: "/admin/users",
    label: "Users",
    owner: "robert",
    area: "administration",
    requiresAuth: true,
    showInPrimaryNavigation: true,
  },
];
