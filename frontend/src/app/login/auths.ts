import api from "./api";

const login = async (email: string, password: string): Promise<Auth | undefined> => {
  try {
    console.log(email, password);
    const response = await api.post("/token/", { email, password });
    localStorage.setItem("accessToken", response.data.access);
    document.cookie = `refreshToken=${response.data.refresh}`;
    return response.data;
  } catch (error: any) {
    console.error(error.response.data.non_field_errors[0]);
    throw new Error(error.response.data.non_field_errors[0]);
  }
}

const requestResetPassword = async (email: string): Promise<void> => {
  try {
    await api.post("/password-reset-request/", { email });
  } catch (error) {
    console.error(error);
  }
}

const resetPassword = async (password: string, token: string): Promise<void> => {
  try {
    await api.post("/password-reset-confirm/", { password, token });
  } catch (error) {
    console.error(error);
  }
}

const requestAccess = async (form: AccessRequestForm): Promise<void> => {
  const { email, password, last_name, first_name } = form;
  try {
    await api.post("/access-requests/", { email, password, last_name, first_name, reason: 'authorization' });
  } catch (error:any) {
    console.error(error.response.data);
    throw new Error(error.response.data.email[0]);
  }
}
const fetchUser = async (): Promise<User | undefined> => {
  try {
    const response = await api.get("/current-user/");
    return response.data;
  } catch (error) {
    console.error(error);
    return undefined;
  }
}


const auths = {
  login,
  requestResetPassword,
  resetPassword,
  requestAccess,
  fetchUser,
};

export default auths;