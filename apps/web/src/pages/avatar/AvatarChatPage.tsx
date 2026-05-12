import { useState, useRef, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, MicOff, Send } from "lucide-react";
import { avatarAPI } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import { LANGUAGES } from "../../i18n";
import Logo from "../../components/brand/Logo";
import { useTranslation } from "react-i18next";

interface Message { role: "user" | "assistant"; content: string; emotion?: string; }

export default function AvatarChatPage() {
  const { user, language } = useAuthStore();
  const { t } = useTranslation();
  const activeLang = LANGUAGES.find(l => l.code === language);
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: t("chat_greeting").replace("{name}", user?.first_name || "") }
  ]);
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef(`session_${Date.now()}`);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const chatMutation = useMutation({
    mutationFn: (message: string) => avatarAPI.chat({
      message,
      language: language || user?.preferred_language || "en",
      session_id: sessionId.current,
      voice_response: false,
    }),
    onSuccess: (response) => {
      const data = response.data;
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.text_response,
        emotion: data.emotion_detected,
      }]);
      if (data.is_emergency) {
        setMessages(prev => [...prev, {
          role: "assistant",
          content: "Please call emergency services (999/112) or go to the nearest hospital immediately.",
        }]);
      }
    },
  });

  const sendMessage = () => {
    if (!input.trim()) return;
    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    chatMutation.mutate(userMessage);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-primary-50 to-warm-50">
      <div className="bg-white border-b border-gray-100 px-4 py-4">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-primary-50 border border-primary-100 flex items-center justify-center overflow-hidden">
            <Logo variant="icon" width={28} />
          </div>
          <div>
            <h1 className="font-bold text-gray-900">MAMA AI</h1>
            <p className="text-secondary-500 text-xs flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-secondary-500 rounded-full animate-pulse" />
              {t("always_here")}
            </p>
          </div>
          {activeLang && (
            <span className="ml-auto text-xs bg-primary-50 text-primary-600 font-medium px-2.5 py-1 rounded-full">
              {activeLang.flag} {activeLang.nativeLabel}
            </span>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 max-w-lg mx-auto w-full">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="w-7 h-7 rounded-xl bg-primary-50 border border-primary-100 flex items-center justify-center mr-2 flex-shrink-0 mt-1 overflow-hidden">
                  <Logo variant="icon" width={20} />
                </div>
              )}
              <div className={`max-w-[80%] px-4 py-3 rounded-3xl text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-primary-500 text-white rounded-br-lg"
                  : "bg-white text-gray-800 shadow-soft rounded-bl-lg"
              }`}>
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {chatMutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-white rounded-3xl rounded-bl-lg px-4 py-3 shadow-soft">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <div key={i} className="w-2 h-2 bg-primary-300 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="bg-white border-t border-gray-100 px-4 py-4 safe-area-pb">
        <div className="max-w-lg mx-auto flex items-center gap-2">
          <button onClick={() => setIsRecording(!isRecording)}
            className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 transition-all ${
              isRecording ? "bg-emergency-500 text-white" : "bg-gray-100 text-gray-500"
            }`}>
            {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder={t("chat_placeholder")}
            className="flex-1 bg-gray-50 rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
          />
          <button onClick={sendMessage} disabled={!input.trim() || chatMutation.isPending}
            className="w-10 h-10 rounded-2xl bg-primary-500 text-white flex items-center justify-center flex-shrink-0 disabled:opacity-50">
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-center text-gray-400 text-xs mt-2">{t("chat_disclaimer")}</p>
      </div>
    </div>
  );
}
