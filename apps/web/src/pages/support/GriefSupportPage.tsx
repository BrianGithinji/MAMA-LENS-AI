import { motion } from "framer-motion";
import { Heart, MessageCircle, Phone, BookOpen } from "lucide-react";
import { Link } from "react-router-dom";
import Logo from "../../components/brand/Logo";
import { useTranslation } from "react-i18next";

export default function GriefSupportPage() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-rose-50 pb-20">
      <div className="bg-gradient-to-br from-rose-400 to-pink-500 px-6 pt-10 pb-16 text-center">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="bg-white/90 rounded-3xl px-6 py-4 inline-block mb-4">
            <Logo variant="full" width={130} />
          </div>
          <h1 className="text-white text-2xl font-bold">{t("grief_title")}</h1>
          <p className="text-rose-100 text-sm mt-2 max-w-xs mx-auto">{t("grief_subtitle")}</p>
        </motion.div>
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-8 space-y-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-3xl shadow-card p-6">
          <p className="text-gray-700 text-sm leading-relaxed">
            Losing a baby — whether through miscarriage, stillbirth, or neonatal loss — is one of the most painful experiences a mother can go through. There is no right or wrong way to grieve. Your feelings are completely valid.
          </p>
          <p className="text-gray-700 text-sm leading-relaxed mt-3">
            MAMA-LENS AI is here to walk alongside you during this difficult time. You deserve care, compassion, and support.
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-white rounded-3xl shadow-card p-5">
          <h2 className="font-bold text-gray-900 mb-4">Support Available to You</h2>
          <div className="space-y-3">
            {[
              { icon: MessageCircle, title: "Talk to MAMA AI", description: "Share your feelings with our compassionate AI assistant, available 24/7", href: "/avatar", color: "bg-rose-100 text-rose-600" },
              { icon: Phone, title: "Crisis Support Line", description: "Africa Mental Health Foundation: +254 722 178 177", href: "tel:+254722178177", color: "bg-calm-100 text-calm-600", external: true },
              { icon: BookOpen, title: "Grief Resources", description: "Articles and guides on healing after pregnancy loss", href: "/education", color: "bg-warm-100 text-warm-600" },
            ].map(({ icon: Icon, title, description, href, color, external }) => (
              external ? (
                <a key={title} href={href} className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl active:scale-95 transition-all">
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}><Icon className="w-5 h-5" /></div>
                  <div><p className="font-semibold text-gray-900 text-sm">{title}</p><p className="text-gray-500 text-xs">{description}</p></div>
                </a>
              ) : (
                <Link key={title} to={href} className="flex items-center gap-4 p-4 bg-gray-50 rounded-2xl active:scale-95 transition-all">
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}><Icon className="w-5 h-5" /></div>
                  <div><p className="font-semibold text-gray-900 text-sm">{title}</p><p className="text-gray-500 text-xs">{description}</p></div>
                </Link>
              )
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-rose-50 to-pink-50 border border-rose-100 rounded-3xl p-5">
          <h3 className="font-bold text-rose-800 mb-3">Remember</h3>
          <ul className="space-y-2 text-rose-700 text-sm">
            {[
              "Your baby was real, and your love for them is real.",
              "Grief has no timeline — heal at your own pace.",
              "Seeking help is a sign of strength, not weakness.",
              "You are still a mother, and always will be.",
              "It is okay to have good days and hard days.",
            ].map((affirmation) => (
              <li key={affirmation} className="flex items-start gap-2">
                <Heart className="w-3 h-3 text-rose-400 flex-shrink-0 mt-1" fill="currentColor" />
                {affirmation}
              </li>
            ))}
          </ul>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-white rounded-3xl shadow-card p-5">
          <p className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-2">Kwa Kiswahili</p>
          <p className="text-gray-700 text-sm leading-relaxed">
            Pole sana kwa msiba wako. Kupoteza mtoto ni moja ya matukio ya uchungu zaidi ambayo mama anaweza kupitia. Huzuni yako ni halali kabisa. Tafadhali jua kwamba huko peke yako, na msaada unapatikana.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
