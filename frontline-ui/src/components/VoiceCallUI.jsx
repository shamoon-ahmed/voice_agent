import { useState } from "react";
import { PhoneOff, MessageSquare, Mic } from "lucide-react";

export default function VoiceCallUI() {
  const [isListening, setIsListening] = useState(false);

  const handleListen = () => {
    setIsListening(!isListening);
    // you'll add your listening logic here later
  };

  return (
    <div className="flex flex-col justify-between items-center min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-6">
      
      {/* Header */}
      <h1 className="text-2xl font-bold mt-6 tracking-wide text-gray-200">
        FrontLine Agent Worker
      </h1>

      {/* Center Button */}
      <div className="flex flex-col items-center justify-center flex-1">
        <button
          onClick={handleListen}
          className={`w-36 h-36 rounded-full flex items-center justify-center transition-all duration-300 shadow-2xl ${
            isListening
              ? "bg-green-400 scale-110 shadow-green-500/60"
              : "bg-white hover:scale-105"
          }`}
        >
          <Mic
            size={56}
            className={`${
              isListening ? "text-green-800" : "text-gray-800"
            } transition-colors`}
          />
        </button>

        <p className="mt-6 text-lg text-gray-300">
          {isListening ? "Listening..." : "Tap to Start Listening"}
        </p>
      </div>

      {/* Bottom Buttons */}
      <div className="flex justify-center gap-6 mb-10">
        <button className="flex items-center gap-2 bg-red-600 hover:bg-red-700 px-6 py-3 rounded-full transition-all text-white font-semibold">
          <PhoneOff size={20} />
          Drop Call
        </button>

        <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-full transition-all text-white font-semibold">
          <MessageSquare size={20} />
          Switch to Chat
        </button>
      </div>
    </div>
  );
}
