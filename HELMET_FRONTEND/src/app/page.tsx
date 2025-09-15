"use client";

import React, { useRef, useEffect } from "react";
import { useRouter } from 'next/navigation';
import { useState } from "react";

import MicrophoneButton from "../components/MicrophoneButton";
import { ArrowRightCircleIcon } from "@heroicons/react/24/solid";
import { RectangleStackIcon } from "@heroicons/react/24/solid";
import { ChevronDown, ChevronUp } from 'lucide-react';
import styles from '../css/LoadindText.module.css';

import BurgerMenu from "../components/BurgerMenu";
import TaskComponent from "../components/TaskComponent";
// import TaskCard from "../components/TaskInfoComponent";

import { Inter } from "next/font/google";
import { log } from "util";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

// import ChatComponent from "../components/ChatComponent"

export default function Home() {

  const router = useRouter();

  const [task, setTask] = useState(null);
  const [OtherUserTest, setOtherUserTest] = useState([]);

  const [userId, setUserId] = useState(1);

  const UserTestSelection = useRef<HTMLDivElement>(null);
  const TaskCardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // API call to local backend  tasks/id
    const fetchTask = async () => {
      const response = await fetch(`http://backend-helmet-lb-1240358724.us-east-1.elb.amazonaws.com/tasks/${userId}`);
      const data = await response.json();
      setTask(data.task);
      console.log(data.task);
    };

    const fetchAllUsersIDs = async () => {
      const response = await fetch('http://backend-helmet-lb-1240358724.us-east-1.elb.amazonaws.com/all_users');
      const data = await response.json();
      setOtherUserTest(data.users);
      console.log(data.users);
    };

    fetchAllUsersIDs();
    fetchTask();
    
    const Id = sessionStorage.getItem("userId");
    if (Id !== null) {
      setUserId(parseInt(Id));
    }

  }, []);

  const [isListening, setIsListening] = useState(false);

  const [displayText, setDisplayText] = useState("Appuyez sur le micro et parlez");
  const [isFading, setIsFading] = useState(false);
  const [isTaskVisible, setIsTaskVisible] = useState(true);

  const [isTestMenuOpen, setIsTestMenuOpen] = useState(false);

  // const [chatOpened, setChatOpened] = useState(false)

  useEffect(() => {
  setIsFading(true);

  const timer = setTimeout(() => {
    setDisplayText(isListening ? "Je vous écoute" : "Appuyez sur le micro et parlez");
    setIsFading(false);
  }, 300);

  const timerVisible = setTimeout(() => {
    if (isListening) {
      setIsTaskVisible(false);
    } else {
      setIsTaskVisible(true);
    }
  }, 300);

  return () => {
    clearTimeout(timer);
    clearTimeout(timerVisible);
  };
  }, [isListening]);

  const handleUserSelect = (userId : number) => {
    setUserId(userId);
    sessionStorage.setItem("userId", userId.toString());
    setIsTestMenuOpen(false);
    // Re-fetch the task for the selected user
    const fetchTask = async () => {
      const response = await fetch(`http://backend-helmet-lb-1240358724.us-east-1.elb.amazonaws.com/tasks/${userId}`);
      const data = await response.json();
      setTask(data.task);
      console.log(data.task);
    };
    fetchTask();
  }
  
  const toggleDropdown = () => {
    setIsTestMenuOpen(!isTestMenuOpen);
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (isTestMenuOpen)
      if (!UserTestSelection.current?.contains(e.target as Node)) {
        setIsTestMenuOpen(false);
      }
  };
  // if (chatOpened === true) return <ChatComponent chatOpened={chatOpened} setChatOpened={setChatOpened}/>

  return (
    <div className="flex flex-col h-screen w-screen" onClick={handleOverlayClick}>
      <div className="w-screen flex justify-between p-10 mb-24 outline-1 outline-gray-200">
        HELMET
        {/* <BurgerMenu /> */}
        <button onClick={toggleDropdown} className="inline-flex flex-col items-center justify-between w-48 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500">
        <span>Sélectionner un utilisateur</span>
        <span>CURRENT ID : {userId}</span>
        {isTestMenuOpen ? (<ChevronUp className="w-5 h-5 ml-2" />) : (<ChevronDown className="w-5 h-5 ml-2" />)}</button>
        {isTestMenuOpen && (
        <div className="absolute right-0 z-50 mt-2 w-40 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5">
          <div className="py-1" ref={UserTestSelection}>
            <div className="px-4 py-2 text-sm text-gray-500 border-b">
              Utilisateurs disponibles
            </div>

            {OtherUserTest && OtherUserTest.length > 0 ? (
              <div className="p-4">
                {/* Votre code map adapté */}
                <div className="flex flex-col gap-4 max-h-60 overflow-y-auto">
                  {OtherUserTest.map((user) => (
                    <div
                      key={user.id}
                      onClick={() => handleUserSelect(user.id)}
                      className="flex items-center gap-4 p-2 hover:bg-gray-100 rounded-md"
                      title={`${user.first_name} ${user.last_name}`}>
                      <div className="w-12 h-12 bg-amber-500/10 backdrop-blur-lg shadow-xl rounded-full flex items-center justify-center text-amber-600 font-semibold cursor-pointer hover:bg-amber-500/20 transition-colors duration-200">
                        {user.id}
                      </div>
                      <div className="text-sm text-gray-700">
                        {user.first_name} {user.last_name}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-4 text-sm text-gray-500">
                Aucun utilisateur disponible
              </div>
            )}
          </div>
        </div>
        )}
      </div>
      <div className="flex flex-col justify-center items-center">
          <TaskComponent task={task} TaskCardRef={TaskCardRef} />
          {/* {DisplayTaskInfo} */}
          <div className={`text-3xl pr-15 pl-15 break-words text-center h-10 mb-30 ${styles.textContainer} ${isFading ? styles.fadeOut : ''} ${inter.className}`}>
          {displayText}
          {!isTaskVisible ? <span className={styles.dotAnimation}></span> : <span />}
        </div>
        <MicrophoneButton isListening={isListening} onClick={() => setIsListening(!isListening)} />
      </div>
      <div className="flex justify-end items-end p-10">
        {/* <ArrowRightCircleIcon className="h-15 w-15 text-amber-500 hover:text-amber-600 cursor-pointer" onClick={() => {setChatOpened(!chatOpened)}} /> */}
        <ArrowRightCircleIcon className="h-15 w-15 text-amber-500 hover:text-amber-600 cursor-pointer" onClick={() => router.push('/chat')} />
      </div>
      
    </div>
  );
}
