import React from 'react';

interface LoadingSquareProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const LoadingSquare: React.FC<LoadingSquareProps> = ({ 
  size = 'md', 
  className = '' 
}) => {
  // Configuration des tailles
  const sizeConfig = {
    sm: {
      square: 'w-16 h-16',
      spinner: 'w-8 h-8',
      border: 'border-2'
    },
    md: {
      square: 'w-24 h-24',
      spinner: 'w-12 h-12',
      border: 'border-2'
    },
    lg: {
      square: 'w-32 h-32',
      spinner: 'w-16 h-16',
      border: 'border-4'
    },
    xl: {
      square: 'w-80 h-80',
      spinner: 'w-60 h-60',
      border: 'border-4'
    }
  };

  const config = sizeConfig[size];

  return (
    <div 
      className={`
        ${config.square} 
        bg-white 
        rounded-lg 
        shadow-md 
        flex 
        items-center 
        justify-center
        ${className}
      `}
    >
      <div 
        className={`
          ${config.spinner} 
          ${config.border} 
          border-gray-300 
          border-t-orange-500 
          rounded-full 
          animate-spin
        `}
      />
    </div>
  );
};

export default LoadingSquare;