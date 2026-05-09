/**
 * MAMA-LENS AI — Mental Health Support Page
 */
import { motion } from "framer-motion";
import { Smile, MessageCircle, Phone, BookOpen } from "lucide-react";
import { Link } from "react-router-dom";

export default function MentalHealthPage() {
  return (
    <div className="min-h-screen bg-purple-50 pb-20">
      <div className="bg-gradient-to-br from-purple-500 to-pink-500 px-6 pt-10 pb-16 text-center">
        <Smile className="w-12 h-12 text-white mx-auto mb-3" />
        <h1 className="text-white text-2xl font-bold">Mental Health Support</h1>
        <p className="text-purple-100 text-sm mt-1">Your emotional wellbeing matters as much as your physical health</p>
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-8 space-y-4">
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
            ].map(({ icon: Icon, title, desc, href, color, external }) => (
              external ? (
                <a key={title} href={href} className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl">
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}><Icon className="w-5 h-5" /></div>
                  <div><p className="font-semibold text-gray-900 text-sm">{title}</p><p className="text-gray-500 text-xs">{desc}</p></div>
                </a>
              ) : (
                <Link key={title} to={href} className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl">
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}><Icon className="w-5 h-5" /></div>
                  <div><p className="font-semibold text-gray-900 text-sm">{title}</p><p className="text-gray-500 text-xs">{desc}</p></div>
                </Link>
              )
            ))}
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
      </div>
    </div>
  );
}
