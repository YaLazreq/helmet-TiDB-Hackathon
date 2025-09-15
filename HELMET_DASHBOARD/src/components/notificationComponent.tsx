import React from 'react';
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

// Interface pour TypeScript (optionnel)
interface NotificationProps {
  type?: 'info' | 'warning' | 'success' | 'error' | 'neutral';
  date: string;
  message: string;
  isActive?: boolean;
  className?: string;
}

// Composant Notification
const Notification = ({ 
  date,
  message,
}: NotificationProps) => {

  return (
    <article className="border-t-2 border-black/5 bg-white">
      <div className="flex items-center gap-2 mb-2 mt-4">
        <span className={`w-0.75 h-8 rounded-full flex-shrink-0`}></span>
        <div className="flex flex-col text-gray-800/50">
          <span className={`${inter.className} tracking-tighter text-xs`}>
            Summarize - {date}
          </span>
          <span className={`${inter.className} tracking-tighter text-sm font-medium`}>
            {message}
          </span>
        </div>
      </div>
    </article>
  );
};

export default Notification;