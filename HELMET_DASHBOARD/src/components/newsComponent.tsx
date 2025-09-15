import React from 'react';
import { Inter } from "next/font/google";

import { ZapIcon } from 'lucide-react';

const inter = Inter({ subsets: ["latin"] });

interface NewsSectionProps {
  title: string;
  subtitle: string;
  description: string;
  titleClassName?: string;
  descriptionClassName?: string;
  containerClassName?: string;
}

const NewsSection = ({ 
  title,
  subtitle,
  description,
  titleClassName = "",
  descriptionClassName = "",
  containerClassName = ""
}: NewsSectionProps) => {
  return (
    <div className={`mb-4 ${containerClassName}`}>
      <h4 className={`mt-1 ${inter.className} tracking-tighter font-semibold text-sm ${titleClassName}`}>
        {title}
      </h4>
      <h5 className={`${inter.className} tracking-tighter text-xs text-black/70 italic mb-2`}>
        {description}
      </h5>
      <div className="flex">
        <ZapIcon className="h-4 w-4 inline-block mr-1 mb-0.5 text-blue-500" />
        <p className={`mb-1 ${inter.className} tracking-tighter text-xs text-blue-500 font-semibold ${descriptionClassName}`}>
          {subtitle}
        </p>
      </div>
    </div>
  );
};

export default NewsSection;