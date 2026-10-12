export type AuthCredentials = {
  username: string;
  password: string;
};

export type AuthenticatedUser = {
  id: string;
  username: string;
  displayName: string;
  role: string;
  permissions: string[];
  email?: string;
};

export type AuthSession = {
  user: AuthenticatedUser;
  accessToken?: string;
  expiresAt?: string;
};

export type AuthState =
  | { status: "anonymous" }
  | { status: "loading" }
  | {
      status: "authenticated";
      session: AuthSession;
    };
