import React, { useEffect, useState } from 'react';

interface StaticEmojiBackgroundProps {
  children?: React.ReactNode;
  emojis?: string[];
  opacity?: number;
  minSize?: number;
  maxSize?: number;
  density?: number; // Nombre d'emojis par 10000 pixels²
}

interface StaticEmojiItem {
  emoji: string;
  x: number;
  y: number;
  size: number;
  rotation: number;
}

export default function StaticEmojiBackground({ 
  children,
  emojis = ['🚀', '⭐', '💫'],
  opacity = 0.1,
  minSize = 20,
  maxSize = 40,
  density = 2,
}: StaticEmojiBackgroundProps) {
  
  const [emojiItems, setEmojiItems] = useState<StaticEmojiItem[]>([]);

  useEffect(() => {
    const generateStaticEmojis = () => {
      // Calculer le nombre d'emojis basé sur la taille de l'écran
      const screenArea = window.innerWidth * window.innerHeight;
      const emojiCount = Math.floor((screenArea / 10000) * density);
      
      const newEmojis: StaticEmojiItem[] = [];
      
      for (let i = 0; i < emojiCount; i++) {
        newEmojis.push({
          emoji: emojis[Math.floor(Math.random() * emojis.length)],
          x: Math.random() * 100,
          y: Math.random() * 100,
          size: Math.random() * (maxSize - minSize) + minSize,
          rotation: Math.random() * 360
        });
      }
      
      setEmojiItems(newEmojis);
    };

    generateStaticEmojis();
    
    // Régénérer si la fenêtre change de taille
    window.addEventListener('resize', generateStaticEmojis);
    return () => window.removeEventListener('resize', generateStaticEmojis);
  }, [emojis, density, minSize, maxSize]);

  return (
    <>
      {/* Background avec emojis statiques désordonnés */}
      <div className="fixed inset-0 pointer-events-none z-0">
        {emojiItems.map((item, index) => (
          <div
            key={index}
            className="absolute"
            style={{
              left: `${item.x}%`,
              top: `${item.y}%`,
              fontSize: `${item.size}px`,
              transform: `rotate(${item.rotation}deg)`,
              opacity: opacity,
            }}
          >
            {item.emoji}
          </div>
        ))}
      </div>
      
      {/* Contenu */}
      <div className="relative z-10">
        {children}
      </div>
    </>
  );
}