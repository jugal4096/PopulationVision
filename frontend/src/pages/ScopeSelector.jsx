import { motion } from "framer-motion";
import {
  ArrowRight,
  Building2,
  Globe2,
  LockKeyhole,
  Map,
  MapPin,
  Sparkles,
  Users,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

const scopes = [
  {
    id: "international",
    title: "International",
    subtitle: "Global demographic intelligence",
    icon: Globe2,
    status: "Coming Soon",
    path: "/international",
  },
  {
    id: "national",
    title: "National",
    subtitle: "India demographic intelligence",
    icon: Globe2,
    status: "Available",
    path: "/national",
    active: true,
  },
  {
    id: "state",
    title: "State",
    subtitle: "Regional demographic analytics",
    icon: Map,
    status: "Coming Soon",
    path: "/state",
  },
  {
    id: "district",
    title: "District",
    subtitle: "District-level population intelligence",
    icon: MapPin,
    status: "Coming Soon",
    path: "/district",
  },
  {
    id: "city",
    title: "City",
    subtitle: "Urban demographic intelligence",
    icon: Building2,
    status: "Coming Soon",
    path: "/city",
  },
  {
    id: "village",
    title: "Village",
    subtitle: "Hyper-local demographic intelligence",
    icon: Users,
    status: "Coming Soon",
    path: "/village",
  },
];

function BackgroundCharacter({ type, className }) {
  return (
    <motion.div
      className={`scope-character ${className}`}
      animate={{
        y: [-8, 8, -8],
        rotate: [-1, 1, -1],
      }}
      transition={{
        duration: 6,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      <div className={`character character-${type}`}>
        <div className="character-head" />
        <div className="character-body" />
        <div className="character-arm character-arm-left" />
        <div className="character-arm character-arm-right" />
        <div className="character-leg character-leg-left" />
        <div className="character-leg character-leg-right" />

        {type === "saree" && <div className="character-saree" />}
        {type === "scientist" && (
          <>
            <div className="scientist-hair" />
            <div className="scientist-glasses" />
          </>
        )}
      </div>
    </motion.div>
  );
}

function Planet({ className, type = "planet" }) {
  return (
    <motion.div
      className={`scope-planet ${className}`}
      animate={{
        y: [-12, 12, -12],
        rotate: [0, 12, 0],
      }}
      transition={{
        duration: 9,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      {type === "saturn" && <div className="saturn-ring" />}
      <div className={`planet-body ${type}`} />
    </motion.div>
  );
}

export default function ScopeSelector({ lockedScope }) {
  const navigate = useNavigate();

  if (lockedScope) {
    const selected = scopes.find(
      (scope) => scope.title.toLowerCase() === lockedScope.toLowerCase(),
    );

    return (
      <main className="locked-screen">
        <div className="locked-stars" />

        <motion.div
          className="locked-card"
          initial={{ opacity: 0, scale: 0.94, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
        >
          <div className="locked-icon">
            <LockKeyhole size={28} />
          </div>

          <span className="scope-badge">COMING SOON</span>

          <h1>{lockedScope} Intelligence</h1>

          <p>
            This geographic intelligence layer is planned for a future
            release. The current platform deliberately focuses on validated
            national-level India data.
          </p>

          <div className="locked-points">
            <span>Dedicated data pipeline</span>
            <span>Validated analytics</span>
            <span>Geographic modelling</span>
          </div>

          <button onClick={() => navigate("/explore")}>
            Back to exploration
            <ArrowRight size={16} />
          </button>
        </motion.div>
      </main>
    );
  }

  return (
    <main className="scope-screen">
      <div className="scope-grid" />

      <div className="scope-glow scope-glow-one" />
      <div className="scope-glow scope-glow-two" />

      <Stars />

      <Planet className="planet-one" />
      <Planet className="planet-two" type="saturn" />

      <BackgroundCharacter type="astronaut" className="character-left" />
      <BackgroundCharacter type="saree" className="character-right" />
      <BackgroundCharacter type="scientist" className="character-scientist" />

      <div className="scope-floating-data data-one">
        1,450,935,791
      </div>

      <div className="scope-floating-data data-two">
        +0.83%
      </div>

      <div className="scope-floating-data data-three">
        ML / 2050
      </div>

      <div className="scope-main">
        <motion.div
          className="scope-top-badge"
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Sparkles size={13} />
          DEMOGRAPHIC INTELLIGENCE PLATFORM
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          Explore the
          <span>population.</span>
        </motion.h1>

        <motion.p
          className="scope-description"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.25 }}
        >
          Choose a geographic intelligence layer to begin your research.
          National India intelligence is available now.
        </motion.p>

        <motion.div
          className="scope-selector"
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
        >
          {scopes.map((scope, index) => {
            const Icon = scope.icon;

            return (
              <motion.button
                key={scope.id}
                className={`scope-option ${
                  scope.active ? "scope-option-active" : ""
                }`}
                onClick={() =>
                  scope.active
                    ? navigate(scope.path)
                    : navigate(scope.path)
                }
                whileHover={{ y: -5, scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                transition={{
                  delay: index * 0.04,
                }}
              >
                <div className="scope-option-icon">
                  <Icon size={20} />
                </div>

                <div className="scope-option-copy">
                  <div className="scope-option-title">
                    {scope.title}
                  </div>

                  <div className="scope-option-subtitle">
                    {scope.subtitle}
                  </div>
                </div>

                <div
                  className={`scope-option-status ${
                    scope.active ? "available" : ""
                  }`}
                >
                  {scope.active ? (
                    <>
                      <span className="available-dot" />
                      Available
                    </>
                  ) : (
                    <>
                      <LockKeyhole size={11} />
                      Soon
                    </>
                  )}
                </div>

                <ArrowRight
                  size={16}
                  className="scope-arrow"
                />
              </motion.button>
            );
          })}
        </motion.div>

        <motion.div
          className="scope-footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
        >
          <span>
            Current coverage
          </span>

          <strong>India · 1960–2050</strong>

          <span className="scope-footer-divider" />

          <span>
            Historical + Estimated + ML Forecast
          </span>
        </motion.div>
      </div>
    </main>
  );
}

function Stars() {
  return (
    <div className="scope-stars">
      {Array.from({ length: 55 }).map((_, index) => (
        <motion.span
          key={index}
          style={{
            left: `${(index * 43) % 100}%`,
            top: `${(index * 71) % 100}%`,
          }}
          animate={{
            opacity: [0.1, 0.65, 0.1],
          }}
          transition={{
            duration: 3 + (index % 4),
            delay: index * 0.05,
            repeat: Infinity,
          }}
        />
      ))}
    </div>
  );
}