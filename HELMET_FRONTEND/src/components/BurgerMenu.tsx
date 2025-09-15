"use client";
import { useState } from 'react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

export default function BurgerMenu() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="md:hidden">
      {/* Burger button */}
      <button onClick={() => setIsOpen(!isOpen)} className="p-2 text-gray-700 hover:text-gray-900">
        {isOpen ? (<XMarkIcon className="h-6 w-6" />) : (<Bars3Icon className="h-6 w-6" />)}
      </button>

      {isOpen && (
        <div className="absolute left-0 right-0 bg-white shadow-lg">
          <nav className="flex flex-col justify-center px-4 py-2">
            <a href="/about" className="py-2 text-gray-700 mt-8">À propos</a>
            <a href="/contact" className="py-2 text-gray-700 mt-8">Contact</a>
          </nav>
        </div>
      )}
    </div>
  );
}