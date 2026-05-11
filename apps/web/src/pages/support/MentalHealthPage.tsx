/**
 * MAMA-LENS AI — Mental Health Support Page with Community
 */
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Smile, MessageCircle, Phone, BookOpen, Users, Send, ChevronDown, ChevronUp, Trash2, EyeOff } from "lucide-react";
import { Link } from "react-router-dom";
import { communityAPI } from "../../api/client";

// ─── Types ────────────────────────────────────────────────────────────────────

interface Reply {
  id: string;
  content: string;
  author: string;
  is_own: boolean;
  created_at: string;
}

interface Post {
  id: string;
  content: string;
  topic: string;
  author: string;
  is_own: boolean;
  reply_count: number;
  replies: Reply[];
  created_at: string;
}

const TOPICS = [
  { value: "all", label: "All" },
  { value: "general", label: "General" },
  { value: "anxiety", label: "Anxiety" },
  { value: "grief", label: "Grief" },
  { value: "postpartum", label: "Postpartum" },
  { value: "nutrition", label: "Nutrition" },
];

const TOPIC_COLORS: Record<string, string> = {
  general: "bg-purple-100 text-purple-700",
  anxiety: "bg-yellow-100 text-yellow-700",
  grief: "bg-blue-100 text-blue-700",
  postpartum: "bg-pink-100 text-pink-700",
  nutrition: "bg-green-100 text-green-700",
};

function timeAgo(iso: string) {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

// ─── PostCard ─────────────────────────────────────────────────────────────────

function PostCard({ post, onDelete, onReply }: {
  post: Post;
  onDelete: (id: string) => void;
  onReply: (postId: string, content: string, anonymous: boolean) => Promise<void>;
}) {
  const [showReplies, setShowReplies] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [replyAnon, setReplyAnon] = useState(false);
  const [sending, setSending] = useState(false);

  async function submitReply() {
    if (!replyText.trim()) return;
    setSending(true);
    await onReply(post.id, replyText, replyAnon);
    setReplyText("");
    setSending(false);
    setShowReplies(true);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-sm p-4 space-y-3"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 font-bold text-sm flex-shrink-0">
            {post.author[0].toUpperCase()}
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-800">{post.author}</p>
            <p className="text-xs text-gray-400">{timeAgo(post.created_at)}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TOPIC_COLORS[post.topic] || "bg-gray-100 text-gray-600"}`}>
            {post.topic}
          </span>
          {post.is_own && (
            <button onClick={() => onDelete(post.id)} className="text-gray-300 hover:text-red-400 transition-colors">
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <p className="text-gray-700 text-sm leading-relaxed">{post.content}</p>

      {/* Reply toggle */}
      <button
        onClick={() => setShowReplies(v => !v)}
        className="flex items-center gap-1 text-xs text-purple-500 font-medium"
      >
        <MessageCircle className="w-3.5 h-3.5" />
        {post.reply_count} {post.reply_count === 1 ? "reply" : "replies"}
        {showReplies ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      <AnimatePresence>
        {showReplies && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2 overflow-hidden"
          >
            {/* Existing replies */}
            {post.replies.map(r => (
              <div key={r.id} className="flex gap-2 pl-3 border-l-2 border-purple-100">
                <div className="w-6 h-6 rounded-full bg-pink-100 flex items-center justify-center text-pink-600 font-bold text-xs flex-shrink-0">
                  {r.author[0].toUpperCase()}
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-700">{r.author} <span className="font-normal text-gray-400">{timeAgo(r.created_at)}</span></p>
                  <p className="text-xs text-gray-600">{r.content}</p>
                </div>
              </div>
            ))}

            {/* Reply input */}
            <div className="flex gap-2 pt-1">
              <input
                value={replyText}
                onChange={e => setReplyText(e.target.value)}
                onKeyDown={e => e.key === "Enter" && !e.shiftKey && submitReply()}
                placeholder="Write a reply..."
                className="flex-1 text-xs border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:border-purple-400"
              />
              <button
                onClick={submitReply}
                disabled={sending || !replyText.trim()}
                className="w-8 h-8 bg-purple-500 rounded-xl flex items-center justify-center disabled:opacity-40"
              >
                <Send className="w-3.5 h-3.5 text-white" />
              </button>
            </div>
            <label className="flex items-center gap-1.5 text-xs text-gray-400 cursor-pointer">
              <input type="checkbox" checked={replyAnon} onChange={e => setReplyAnon(e.target.checked)} className="rounded" />
              <EyeOff className="w-3 h-3" /> Reply anonymously
            </label>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function MentalHealthPage() {
  const [activeTab, setActiveTab] = useState<"support" | "community">("support");
  const [activeTopic, setActiveTopic] = useState("all");
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(false);
  const [newPost, setNewPost] = useState("");
  const [newTopic, setNewTopic] = useState("general");
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (activeTab === "community") fetchPosts();
  }, [activeTab, activeTopic]);

  async function fetchPosts() {
    setLoading(true);
    setError("");
    try {
      const res = await communityAPI.getPosts(activeTopic);
      setPosts(res.data);
    } catch {
      setError("Could not load posts. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handlePost() {
    if (!newPost.trim()) return;
    setPosting(true);
    try {
      await communityAPI.createPost({ content: newPost.trim(), topic: newTopic, is_anonymous: isAnonymous });
      setNewPost("");
      await fetchPosts();
    } catch {
      setError("Failed to post. Please try again.");
    } finally {
      setPosting(false);
    }
  }

  async function handleDelete(postId: string) {
    try {
      await communityAPI.deletePost(postId);
      setPosts(prev => prev.filter(p => p.id !== postId));
    } catch {
      setError("Could not delete post.");
    }
  }

  async function handleReply(postId: string, content: string, anonymous: boolean) {
    await communityAPI.replyToPost(postId, { content, is_anonymous: anonymous });
    await fetchPosts();
  }

  return (
    <div className="min-h-screen bg-purple-50 pb-20">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-500 to-pink-500 px-6 pt-10 pb-16 text-center">
        <Smile className="w-12 h-12 text-white mx-auto mb-3" />
        <h1 className="text-white text-2xl font-bold">Mental Health Support</h1>
        <p className="text-purple-100 text-sm mt-1">Your emotional wellbeing matters as much as your physical health</p>
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-8 space-y-4">
        {/* Tab switcher */}
        <div className="bg-white rounded-2xl shadow-sm p-1 flex gap-1">
          <button
            onClick={() => setActiveTab("support")}
            className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all ${activeTab === "support" ? "bg-purple-500 text-white" : "text-gray-500"}`}
          >
            Support
          </button>
          <button
            onClick={() => setActiveTab("community")}
            className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-1.5 ${activeTab === "community" ? "bg-purple-500 text-white" : "text-gray-500"}`}
          >
            <Users className="w-4 h-4" /> Community
          </button>
        </div>

        {/* ── Support Tab ── */}
        {activeTab === "support" && (
          <>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-3xl shadow-card p-5">
              <p className="text-gray-700 text-sm leading-relaxed">
                Pregnancy and the postpartum period can bring a wide range of emotions — joy, anxiety, sadness, and everything in between. These feelings are normal and valid. You deserve support.
              </p>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-white rounded-3xl shadow-card p-5">
              <h2 className="font-bold text-gray-900 mb-4">Get Support</h2>
              <div className="space-y-3">
                {[
                  { icon: MessageCircle, title: "Talk to MAMA AI", desc: "24/7 compassionate AI support", href: "/avatar", color: "bg-purple-100 text-purple-600" },
                  { icon: Phone, title: "Crisis Helpline", desc: "+254 722 178 177", href: "tel:+254722178177", color: "bg-emergency-100 text-emergency-600", external: true },
                  { icon: BookOpen, title: "Self-Care Resources", desc: "Meditation, breathing exercises", href: "/education", color: "bg-secondary-100 text-secondary-600" },
                  { icon: Users, title: "Community", desc: "Talk to other mothers", color: "bg-pink-100 text-pink-600", action: () => setActiveTab("community") },
                ].map(({ icon: Icon, title, desc, href, color, external, action }) =>
                  action ? (
                    <button key={title} onClick={action} className="w-full flex items-center gap-4 p-4 bg-gray-50 rounded-2xl text-left">
                      <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}><Icon className="w-5 h-5" /></div>
                      <div><p className="font-semibold text-gray-900 text-sm">{title}</p><p className="text-gray-500 text-xs">{desc}</p></div>
                    </button>
                  ) : external ? (
                    <a key={title} href={href} className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl">
                      <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}><Icon className="w-5 h-5" /></div>
                      <div><p className="font-semibold text-gray-900 text-sm">{title}</p><p className="text-gray-500 text-xs">{desc}</p></div>
                    </a>
                  ) : (
                    <Link key={title} to={href!} className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl">
                      <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}><Icon className="w-5 h-5" /></div>
                      <div><p className="font-semibold text-gray-900 text-sm">{title}</p><p className="text-gray-500 text-xs">{desc}</p></div>
                    </Link>
                  )
                )}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-purple-50 border border-purple-200 rounded-3xl p-5">
              <h3 className="font-bold text-purple-800 mb-2">Signs You May Need Support</h3>
              <ul className="space-y-1 text-purple-700 text-sm">
                {["Feeling persistently sad or hopeless", "Difficulty bonding with your baby", "Excessive worry or panic attacks", "Thoughts of harming yourself", "Feeling disconnected from reality", "Unable to care for yourself or baby"].map(sign => (
                  <li key={sign} className="flex items-center gap-2"><span className="text-purple-400">•</span>{sign}</li>
                ))}
              </ul>
              <p className="text-purple-600 text-xs mt-3 font-medium">If you experience these, please reach out to your healthcare provider or call +254 722 178 177</p>
            </motion.div>
          </>
        )}

        {/* ── Community Tab ── */}
        {activeTab === "community" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
            {/* Compose */}
            <div className="bg-white rounded-2xl shadow-sm p-4 space-y-3">
              <p className="text-sm font-semibold text-gray-800">Share with the community</p>
              <textarea
                ref={textareaRef}
                value={newPost}
                onChange={e => setNewPost(e.target.value)}
                placeholder="How are you feeling today? Share your thoughts, ask a question, or offer encouragement..."
                rows={3}
                className="w-full text-sm border border-gray-200 rounded-xl px-3 py-2 resize-none focus:outline-none focus:border-purple-400"
              />
              <div className="flex items-center gap-2 flex-wrap">
                <select
                  value={newTopic}
                  onChange={e => setNewTopic(e.target.value)}
                  className="text-xs border border-gray-200 rounded-xl px-3 py-1.5 focus:outline-none focus:border-purple-400 bg-white"
                >
                  {TOPICS.filter(t => t.value !== "all").map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
                <label className="flex items-center gap-1.5 text-xs text-gray-500 cursor-pointer ml-auto">
                  <input type="checkbox" checked={isAnonymous} onChange={e => setIsAnonymous(e.target.checked)} className="rounded" />
                  <EyeOff className="w-3.5 h-3.5" /> Post anonymously
                </label>
                <button
                  onClick={handlePost}
                  disabled={posting || !newPost.trim()}
                  className="flex items-center gap-1.5 bg-purple-500 text-white text-xs font-semibold px-4 py-1.5 rounded-xl disabled:opacity-40"
                >
                  <Send className="w-3.5 h-3.5" />
                  {posting ? "Posting..." : "Post"}
                </button>
              </div>
            </div>

            {/* Topic filter */}
            <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
              {TOPICS.map(t => (
                <button
                  key={t.value}
                  onClick={() => setActiveTopic(t.value)}
                  className={`flex-shrink-0 text-xs font-semibold px-3 py-1.5 rounded-full transition-all ${activeTopic === t.value ? "bg-purple-500 text-white" : "bg-white text-gray-500 border border-gray-200"}`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Error */}
            {error && <p className="text-xs text-red-500 text-center">{error}</p>}

            {/* Posts */}
            {loading ? (
              <div className="text-center py-10 text-purple-400 text-sm">Loading posts...</div>
            ) : posts.length === 0 ? (
              <div className="text-center py-10 space-y-2">
                <Users className="w-10 h-10 text-purple-200 mx-auto" />
                <p className="text-gray-400 text-sm">No posts yet. Be the first to share!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {posts.map(post => (
                  <PostCard key={post.id} post={post} onDelete={handleDelete} onReply={handleReply} />
                ))}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
