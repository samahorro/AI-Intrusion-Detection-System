export type AuthCredentials = {
  email: string;
  password: string;
};

export type AuthenticatedUser = {
  id: string;
  email: string;
  displayName: string;
  role: string;
  permissions: string[];
};

export type AuthSession = {
  accessToken: string;
  expiresAt: string;
  user: AuthenticatedUser;
};

export type AuthState =
  | { status: "anonymous" }
  | { status: "loading" }
  | {
      status: "authenticated";
      session: AuthSession;
    };
