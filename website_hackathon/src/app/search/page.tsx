"use client"

import { log } from "console";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { PlaneTakeoff, PlaneLanding } from "lucide-react";
import { UserIcon } from "@heroicons/react/24/outline";

import { PackagesCard } from "@/components/packages_card";


export default function Quizz() {

  const router = useRouter();
  
  return (
    <main className="min-h-screen bg-white">
      {/* Top bar */}
      <header className="px-8 py-10 flex items-center">
        <div className="text-2xl font-semibold tracking-tight" onClick={() => router.push("/")}>Katniss</div>
        <div className="ml-auto w-10 h-10 rounded-full bg-gray-300" onClick={() => router.push("/profils")}></div>
      </header>

      <body className="mx-auto outline-3">

        <section className="mx-auto max-w-300 p-5 mt-10 outline-1 outline-gray-300 rounded-lg">
          {/* Display three images */}
          <section className="flex gap-4 overflow-x-auto flex-nowrap snap-x snap-mandatory [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden before:content-[''] before:flex-1 before:shrink-0 after:content-['']  after:flex-1  after:shrink-0 mb-6">
            <PackagesCard />
            <PackagesCard />
            <PackagesCard />
          </section>
        </section>
      </body>
    </main>
  );
}
