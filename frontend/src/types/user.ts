export type UserSummary = {
  id: string;
  email: string;
  displayName: string;
  role: string;
  status: string;
};

export type UserDetails = UserSummary & {
  createdAt?: string;
  updatedAt?: string;
  permissions: string[];
};

export type UserQuery = {
  search?: string;
  role?: string;
  status?: string;
};

export type UserUpdate = {
  displayName?: string;
  role?: string;
  status?: string;
};
