"use client"
import { redirect } from "next/navigation";

export default function Home() {
  // Verify is user is connected,  if not connected > redirect to login
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';

  if (!isAuthenticated) return redirect('/login');

  return (
    <main className="flex min-h-screen">
      <div className="flex-1 bg-gray-100" />
      <div className="max-w-[48rem] w-full text-4xl">Hello, World!</div>
      <div className="flex-1 bg-gray-100" />
    </main>
  );
}
