import { MicrophoneIcon } from "@heroicons/react/24/solid";

interface MicrophoneButtonProps {
  isListening: boolean;
  onClick: () => void;
}

export default function MicrophoneButton({ isListening, onClick }: MicrophoneButtonProps) {
  return (
    <div onClick={onClick} className={`relative flex items-center justify-center p-20 rounded-full transition-all duration-300 ${isListening ? "bg-gradient-to-br from-amber-500 via-amber-400 to-orange-400/20 text-transparent animate-pulse" : "bg-gray-100 text-gray-800"}`}style={{animation: isListening ? 'pulse 1.5s ease-in-out infinite, breathe 2s ease-in-out infinite' : 'none'}}>
      {/* Icône micro */}
      <MicrophoneIcon className={`h-20 w-20 z-10 relative`} />
      
      <style jsx>{`
        @keyframes breathe {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
      `}</style>
    </div>
  );
}