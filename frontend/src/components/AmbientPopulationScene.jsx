import { motion } from "framer-motion";

const figures = [
  { left: "8%", delay: 0, duration: 7, scale: 0.75 },
  { left: "19%", delay: 1.5, duration: 8, scale: 0.9 },
  { left: "32%", delay: 0.8, duration: 6.5, scale: 0.65 },
  { left: "47%", delay: 2, duration: 7.5, scale: 1 },
  { left: "61%", delay: 0.5, duration: 8.5, scale: 0.7 },
  { left: "74%", delay: 1.2, duration: 6.8, scale: 0.85 },
  { left: "87%", delay: 2.2, duration: 7.8, scale: 0.65 },
];

function Person({ scale = 1 }) {
  return (
    <div
      className="relative h-28 w-14"
      style={{ transform: `scale(${scale})` }}
    >
      {/* Head */}
      <div className="absolute left-1/2 top-0 h-5 w-5 -translate-x-1/2 rounded-full bg-cyan-300/20 shadow-[0_0_18px_rgba(34,211,238,0.18)]" />

      {/* Body */}
      <div className="absolute left-1/2 top-6 h-12 w-8 -translate-x-1/2 rounded-[45%_45%_25%_25%] bg-gradient-to-b from-cyan-300/15 to-violet-400/10" />

      {/* Legs */}
      <div className="absolute left-[19px] top-[54px] h-14 w-[5px] rotate-[3deg] rounded-full bg-cyan-300/10" />
      <div className="absolute left-[30px] top-[54px] h-14 w-[5px] -rotate-[3deg] rounded-full bg-violet-300/10" />

      {/* Arms */}
      <div className="absolute left-[13px] top-[29px] h-10 w-[4px] rotate-[20deg] rounded-full bg-cyan-300/10" />
      <div className="absolute right-[13px] top-[29px] h-10 w-[4px] -rotate-[20deg] rounded-full bg-violet-300/10" />
    </div>
  );
}

export default function AmbientPopulationScene() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* Atmospheric glow */}
      <div className="absolute left-[10%] top-[15%] h-72 w-72 rounded-full bg-cyan-400/[0.035] blur-3xl" />
      <div className="absolute right-[8%] top-[10%] h-80 w-80 rounded-full bg-violet-500/[0.035] blur-3xl" />

      {/* Perspective grid */}
      <div className="population-grid absolute inset-x-0 bottom-0 h-[55%] opacity-20" />

      {/* Floating data particles */}
      {Array.from({ length: 26 }).map((_, index) => (
        <motion.span
          key={index}
          className="absolute h-1 w-1 rounded-full bg-cyan-300/30"
          style={{
            left: `${(index * 37) % 100}%`,
            top: `${(index * 19) % 75}%`,
          }}
          animate={{
            y: [-8, 8, -8],
            opacity: [0.15, 0.65, 0.15],
          }}
          transition={{
            duration: 3 + (index % 4),
            delay: index * 0.12,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      {/* Human population silhouettes */}
      <div className="absolute inset-x-0 bottom-0 flex h-36 items-end justify-between px-[3%] opacity-70">
        {figures.map((figure, index) => (
          <motion.div
            key={index}
            className="absolute bottom-0"
            style={{ left: figure.left }}
            initial={{ opacity: 0, y: 20 }}
            animate={{
              opacity: [0.15, 0.45, 0.15],
              y: [0, -5, 0],
            }}
            transition={{
              duration: figure.duration,
              delay: figure.delay,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <Person scale={figure.scale} />
          </motion.div>
        ))}
      </div>

      {/* Scanning line */}
      <motion.div
        className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-cyan-300/20 to-transparent"
        animate={{ top: ["18%", "78%", "18%"] }}
        transition={{
          duration: 9,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </div>
  );
}