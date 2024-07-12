type Auth = {
  accessToken: string;
  refreshToken: string;
}

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
}

type  AccessRequestForm ={
  email: string;
  password: string;
  last_name: string;
  first_name: string;
}

type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
}