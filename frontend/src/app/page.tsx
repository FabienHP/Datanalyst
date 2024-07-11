"use client"
import { redirect } from "next/navigation";

export default function Home() {
  // TODO: Remove this line after implementing authentication
  localStorage.setItem("user", JSON.stringify({ uuid: "397018a0-9f77-459d-a8e9-8f0414dd81b3", firstName: "John", lastName: "Doe", email: "johndoe@gmail.com" }));
  const user: UserType | null = localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user") as string) : null;

  if (!user) return redirect('/login');

  return (
    <main className="flex min-h-screen bg-slate-800">
      <div className="flex-1" />
      <div className="flex flex-col max-w-[48rem] w-full max-h-screen">
      <div className="bg-gray-200 flex-1 overflow-y-scroll">
        <div className="px-4 py-2">
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
          <div className="flex items-center mb-2">
            <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="User Avatar" />
            <div className="font-medium">John Doe</div>
          </div>
          <div className="bg-white rounded-lg p-2 shadow mb-2 max-w-sm">
            Hi, how can I help you?
          </div>
          <div className="flex items-center justify-end">
            <div className="bg-blue-500 text-white rounded-lg p-2 shadow mr-2 max-w-sm">
              Sure, I can help with that.
            </div>
            <img className="w-8 h-8 rounded-full" src="https://picsum.photos/50/50" alt="User Avatar" />
          </div>
        </div>
      </div>
      <div className="bg-gray-100 px-4 py-2">
        <div className="flex items-center">
          <input className="w-full border rounded-full py-2 px-4 mr-2" type="text" placeholder="Type your message..." />
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-full">
            Send
          </button>
        </div>
      </div>
      </div>
      <div className="flex-1" />
    </main>
  );
}
