"use client";

import { Html, useProgress } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { useRef, useState } from "react";

export function PerformanceMonitor() {
  const [fps, setFps] = useState(60);
  const frames = useRef(0);
  const elapsed = useRef(0);
  const { active } = useProgress();
  useFrame((_state, delta) => {
    frames.current += 1;
    elapsed.current += delta;
    if (elapsed.current >= 0.8) {
      setFps(Math.round(frames.current / elapsed.current));
      frames.current = 0;
      elapsed.current = 0;
    }
  });
  return (
    <Html position={[-90, 72, 0]}>
      <span className="fps-counter">{active ? "loading" : `${fps} fps`}</span>
    </Html>
  );
}
