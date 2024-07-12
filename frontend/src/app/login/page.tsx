"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import auths from "./auths";
import api from "./api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const router = useRouter();

  const handleLogin = async (e: any) => {
    e.preventDefault();
    try {
      const token = await auths.login(email, password);
      if (token) {
        const user = await api.get("/current-user/");
        localStorage.setItem("user", JSON.stringify(user.data));
        router.push("/");
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <main className="flex min-h-screen">
      <div className="flex-1 bg-gray-100" />
      <div className="max-w-[48rem] w-full p-8">
        <h1 className="text-4xl mb-4 text-white">Hello, World Login!</h1>
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <label htmlFor="email" className="block text-lg text-white">Email</label>
            <input
              type="email"
              id="email"
              className="w-full p-2 border border-gray-300 rounded"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="block text-lg text-white">Password</label>
            <input
              type="password"
              id="password"
              className="w-full p-2 border border-gray-300 rounded"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-red-500 mb-4">{error}</p>}
          <button
            type="submit"
            className="w-full p-2 bg-blue-500 text-white rounded"
          >
            Login
          </button>
        </form>
      </div>
      <div className="flex-1 bg-gray-100" />
    </main>
  );
}
