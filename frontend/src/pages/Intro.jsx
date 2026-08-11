import { motion } from "framer-motion";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Stars() {
  return (
    <div className="intro-stars">
      {Array.from({ length: 70 }).map((_, index) => (
        <motion.span
          key={index}
          className="intro-star"
          style={{
            left: `${(index * 37) % 100}%`,
            top: `${(index * 61) % 100}%`,
          }}
          animate={{
            opacity: [0.15, 0.8, 0.15],
            scale: [0.7, 1.2, 0.7],
          }}
          transition={{
            duration: 2 + (index % 4),
            delay: index * 0.04,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

function Earth() {
  return (
    <motion.div
      className="intro-earth"
      initial={{ scale: 0.7, opacity: 0 }}
      animate={{
        scale: [0.7, 1, 1],
        opacity: [0, 1, 1],
      }}
      transition={{
        duration: 2.2,
        ease: "easeOut",
      }}
    >
      <div className="earth-glow" />

      <div className="earth">
        <div className="earth-grid earth-grid-one" />
        <div className="earth-grid earth-grid-two" />

        <div className="earth-land land-one" />
        <div className="earth-land land-two" />
        <div className="earth-land land-three" />
      </div>

      <div className="earth-orbit orbit-one" />
      <div className="earth-orbit orbit-two" />
    </motion.div>
  );
}

export default function Intro() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate("/explore", { replace: true });
    }, 6000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <main className="intro-screen">
      <Stars />

      <div className="intro-ambient intro-ambient-one" />
      <div className="intro-ambient intro-ambient-two" />

      <div className="intro-content">
        <Earth />

        <motion.div
          className="intro-india-line"
          initial={{
            opacity: 0,
            scaleX: 0,
            transformOrigin: "left",
          }}
          animate={{
            opacity: [0, 1, 1, 0],
            scaleX: [0, 0, 1, 1],
          }}
          transition={{
            delay: 2.2,
            duration: 2.2,
            times: [0, 0.25, 0.75, 1],
          }}
        />

        <motion.div
          className="intro-india"
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{
            opacity: [0, 1, 1, 0],
            scale: [0.5, 1, 1, 1.2],
          }}
          transition={{
            delay: 2.9,
            duration: 1.7,
          }}
        >
          INDIA
        </motion.div>

        <motion.div
          className="intro-text"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 3.6, duration: 0.7 }}
        >
          <div className="intro-eyebrow">
            NATIONAL DEMOGRAPHIC INTELLIGENCE
          </div>

          <h1>
            Population
            <span>Decoded.</span>
          </h1>

          <p>
            Connecting demographic data, machine learning and research
            intelligence.
          </p>
        </motion.div>

        <motion.div
          className="intro-status"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 4.4 }}
        >
          <span className="status-dot" />
          SYSTEM INITIALIZED
        </motion.div>
      </div>

      <motion.button
        className="intro-skip"
        onClick={() => navigate("/explore")}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2 }}
      >
        Skip intro
      </motion.button>
    </main>
  );
}