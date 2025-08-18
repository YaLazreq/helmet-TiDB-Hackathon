"use client"

import { log } from "console";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { PlaneTakeoff, PlaneLanding } from "lucide-react";
import { UserIcon } from "@heroicons/react/24/outline";

import { PackagesCard } from "@/components/packages_card";

function PromptParameter() {
  return (
    <section className="outline-1 outline-gray-300 rounded-lg flex flex-row">
      <div className="flex items-center p-2" >
        <PlaneTakeoff className="h-5 w-5 text-gray-500 mr-2" />
        <div className="text-gray-600 font-medium">Fri. 18 Mars</div>
      </div>

      <div className="border-r-1 border-gray-300" />

      <div className="flex items-center p-2">
        <PlaneLanding className="h-5 w-5 text-gray-500 mr-2" />
        <div className="text-gray-600 font-medium">Wed. 25 Mars</div>
      </div>

      <div className="border-r-1 border-gray-300" />

      <div className="flex items-center p-2">
        <UserIcon className="h-5 w-5 text-gray-500 mr-1" />
        <div className="text-gray-600 font-medium pr-1">1</div>
      </div>
    </section>
  );
}

export default function Home() {

  const router = useRouter();

  const [value, setValue] = useState("");

  const handleChange = (e) => {
    setValue(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = e.target.value.length > 0 ? `${e.target.scrollHeight}px` : "1.8rem"; // Adjust height based on content
  };
  
  return (
    <main className="min-h-screen bg-white">
      {/* Top bar */}
      <header className="px-8 py-10 flex items-center">
        <div className="text-2xl font-semibold tracking-tight" onClick={() => router.push("/")}>Katniss</div>
        <div className="ml-auto w-10 h-10 rounded-full bg-gray-300" onClick={() => router.push("/profils")}></div>
      </header>

      <body className="mx-auto outline-3">

        {/* Search bar gpt like  */}
        <section className="mx-auto max-w-250 p-5 bg-gray-100 rounded-lg mb-25">
          <textarea
            className={`mb-15 text-lg outline-none transition-all duration-500 ease-in-out resize-none overflow-hidden ${value.length > 0 ? "w-full placeholder-transparent" : "w-64"} `}
            placeholder="What's your dream voyage ?"
            value={value}
            onChange={handleChange}
            rows={1}
          />
        <div className="flex flex-row justify-between items-center">
          <PromptParameter />
          <MagnifyingGlassIcon className="h-6 w-6 text-gray-500" onClick={() => router.push("/search")} />
        </div>
        </section>

        <section className="mx-auto max-w-300 p-5 mt-10 outline-1 outline-gray-300 rounded-lg">
          {/* pre made packages */}
          <div className="text-lg font-semibold mb-4">Pre-made packages</div>
          <section className="flex gap-4 overflow-x-auto flex-nowrap snap-x snap-mandatory [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden before:content-[''] before:flex-1 before:shrink-0 after:content-['']  after:flex-1  after:shrink-0 mb-6">
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
          </section>
          {/* community packages */}
          <div className="text-lg font-semibold mb-4">Community packages</div>
          <section className="flex gap-4 overflow-x-auto flex-nowrap snap-x snap-mandatory [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden before:content-[''] before:flex-1 before:shrink-0 after:content-['']  after:flex-1  after:shrink-0">
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
          </section>
        </section>
      </body>
    </main>
  );
}
