"use client"
import { redirect } from "next/navigation";

export default function Login() {
  const user = localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user") as string) : null;

  if (user) return redirect('/');

  return (
    <main className="flex min-h-screen">
      <div className="flex-1 bg-gray-100" />
      <div className="max-w-[48rem] w-full text-4xl">Hello, World Login!</div>
      <div className="flex-1 bg-gray-100" />
    </main>
  );
}
