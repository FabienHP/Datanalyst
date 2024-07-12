"use client";
import { redirect, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import api from "./login/api";
import { deleteTokens } from "./utils/tokens";

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [messages, setMessages] = useState<{ sender: string; text: string; }[]>([]);
  const [input, setInput] = useState("");
  const router = useRouter();

  useEffect(() => {
    const storedUser = localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user") as string) : null;
    if (storedUser) {
      setUser(storedUser);
    } else {
      redirect('/login');
    }
  }, []);

  if (!user) return null;

  const handleSend = async () => {
    if (input.trim() === "") return;

    const newMessage = { sender: "user", text: input };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput("");
    const response = await ask(input);
    if (!response) return;
    const botResponse = { sender: "bot", text: response };
    setMessages((prevMessages) => [...prevMessages, botResponse]);

    setInput("");
  };

  const handleKeyPress = (e: any) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  const ask = async (text: string) => {
    try {
      const conversionId = sessionStorage.getItem('conversionId');
      if (!conversionId) {
        const response = await api.post('/conversations/');
        sessionStorage.setItem('conversionId', response.data.id);
        return askQuestion(text, response.data.id);
      } else {
        return askQuestion(text, conversionId);
      }
    } catch (error) {
      console.error(error);
      return null;
    }
  };
  
  const askQuestion = async (text: string, conversionId: any) => {
    try {
      const response = await api.post('/ask/', { question: text, conversation_id: conversionId});
      return response.data.ai_response;
    } catch (error) {
      console.error(error);
      return null;
    }
  };



  return (
    <main className="flex min-h-screen bg-slate-800">
      <div className="flex-1" />
      <div className="flex flex-col max-w-[48rem] w-full max-h-screen">
        <div className="bg-gray-200 flex-1 overflow-y-scroll">
          <div className="px-4 py-2">
            <div className="mb-4 text-xl flex justify-between">
              <span>Welcome, {user.first_name} {user.last_name}!</span>
              {/* create a logout btn */}
              <button
                className="bg-red-500 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-full ml-2"
                onClick={() => {
                  localStorage.removeItem("user");
                  deleteTokens();
                  router.push("/login");
                }}
              >Logout</button>
            </div>
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"} mb-2`}>
                {message.sender === "bot" && (
                  <img className="w-8 h-8 rounded-full mr-2" src="https://picsum.photos/50/50" alt="Bot Avatar" />
                )}
                <div className={`${message.sender === "user" ? "bg-blue-500 text-white" : "bg-white"} rounded-lg p-2 shadow max-w-sm`}>
                  {message.text}
                </div>
                {message.sender === "user" && (
                  <img className="w-8 h-8 rounded-full ml-2" src="https://picsum.photos/50/50" alt="User Avatar" />
                )}
              </div>
            ))}
          </div>
        </div>
        <div className="bg-gray-100 px-4 py-2">
          <div className="flex items-center">
            <input
              className="w-full border rounded-full py-2 px-4 mr-2"
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-full"
              onClick={handleSend}
            >
              Send
            </button>
          </div>
        </div>
      </div>
      <div className="flex-1" />
    </main>
  );
}
