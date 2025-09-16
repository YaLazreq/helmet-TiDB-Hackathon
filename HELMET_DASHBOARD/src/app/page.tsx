"use client";

import Image from "next/image";
import React from "react";
import { useState, useEffect } from "react"
import { UserIcon, FlagIcon, NewspaperIcon } from "@heroicons/react/24/solid";
import { MapIcon, BellDot, ClipboardEdit, ClipboardCheck, ClipboardCopy, ClipboardList } from "lucide-react";
import { Inter } from "next/font/google";

import TaskRow from "../components/taskComponent";
import NewsSection from "../components/newsComponent";
import Notification from "../components/notificationComponent";

import plan from "../images/plan.png";

const inter = Inter({ subsets: ["latin"] });

export const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('WebSocket connecté');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setData(message);
    };

    ws.onclose = () => {
      console.log('WebSocket fermé');
      setSocket(null);
    };

    return () => {
      ws.close();
    };
  }, [url]);

  return { socket, data };
};

export const applyChange = (actionList: string) => {
  const apiPayload = {
    message: "[999][User ID: 1 : " + actionList + "]"
  };
  // alert(apiPayload.message);

  fetch('http://localhost:8000/call_supervisor', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(apiPayload)
  });
}

export default function Home() {
  const { data } = useWebSocket('http://localhost:8000/ws');

  type Task = {
    id: number;
    title: string;
    status: "completed" | "pending" | string;
  };

  type Notification = {
    id: number;
    message: string;
    is_triggered: boolean;
    action_list: string;
  };

  useEffect(() => {
    const fetchData = async () => {
      console.log("Received WebSocket data:", data);
      try {
        if (data?.ding === "task") {
          const res = await fetch("http://localhost:8000/tasks");
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const { tasks } = await res.json();

          setAllCompletedTasks(tasks.filter((t: Task) => t.status === "completed"));
          setAllTasks(tasks.filter((t: Task) => t.status !== "completed"));
        }

        if (data?.ding === "notification") {
          console.log("Fetching notifications due to WebSocket event");
          const res = await fetch("http://localhost:8000/notifications");
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          const { notifications } = await res.json();

          setAllTrigeredNotifications(
            notifications.filter((n: Notification) => n.is_triggered)
          );
          setAllNotifications(
            notifications.filter((n: Notification) => !n.is_triggered)
          );
        }

        // if (data?.ding === "news") {
        //   const res = await fetch("http://localhost:8000/news");
        //   if (!res.ok) throw new Error(`HTTP ${res.status}`);
        //   const { news } = await res.json();
        //   setAllNews(news);
        // }
      } catch (err) {
        console.error("Error fetching:", err);
      }
    };

    fetchData();
    console.log("WebSocket data changed:", data);
  }, [data]);


  const [SiteName, setSiteName] = useState("Hoverville Retail Park");
  const [LocalisationSite, setLocalisationSite] = useState("California, USA");
  const [MonitorName, setMonitorName] = useState("Monitor 1");

  const [allTasks, setAllTasks] = useState<any[]>([]);
  const [allCompletedTasks, setAllCompletedTasks] = useState<any[]>([]);
  const [allNotifications, setAllNotifications] = useState<any[]>([]);
  const [allTrigeredNotifications, setAllTrigeredNotifications] = useState<any[]>([]);

  useEffect(() => {
    async function fetchTasks() {
      try {
        const response = await fetch('http://localhost:8000/tasks');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        for (const task of data.tasks) {
          if (task.status === 'completed') {
            setAllCompletedTasks(prev => [...prev, task]);
          } else {
            setAllTasks(prev => [...prev, task]);
          }
        }
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    }

    async function fetchNotifications() {
      try {
        const response = await fetch('http://localhost:8000/notifications');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log(data);
        for (const notification of data.notifications) {
          if (notification.is_triggered) {
            setAllTrigeredNotifications(prev => [...prev, notification]);
          } else {
            setAllNotifications(prev => [...prev, notification]);
          }
        }

      } catch (error) {
        console.error('Error fetching notifications:', error);
      }
    }

    fetchNotifications();
    fetchTasks();
  }, []);

  return (
    // MAIN CONTAINER
    <main className="flex min-h-screen flex-col bg-white items-center justify-between px-12 pt-12">
      {/* PAGE HEADER */}
      <header className="">
        <section className={`flex flex-col w-full items-center justify-center ${inter.className} tracking-tighter text-3xl font-medium mb-3`}>
          <span>
            Welcome to
          </span>
          <span>
            {SiteName} Project
          </span>
        </section>
        <section className={`flex w-full items-center justify-center text-black text-xs gap-2 ${inter.className} tracking-tighter font-medium mb-10`}>
          <span className="outline-1 outline-black/5 rounded-2xl p-1 pr-2">
            <FlagIcon className="h-3 w-3 inline-block ml-1 mr-1 mb-0.5" />
            {LocalisationSite}
          </span>
          <span className="outline-1 outline-black/5 rounded-2xl p-1 pr-2">
            <UserIcon className="h-3 w-3 inline-block mr-1 mb-0.5" />
            {MonitorName}
          </span>
        </section>
      </header>

      {/* CONTENT LAYOUT */}
      <section className="flex mb-32 justify-between w-full">
        {/* LEFT PANEL - TASKS SECTION */}
        <section className="flex flex-col gap-7 w-1/2">
          {/* SECTION TITLE */}
          <header className={`flex outline-2 rounded-lg p-4 outline-black/5 ${inter.className} tracking-tighter font-medium text-lg`}>
            <ClipboardList className="h-5 w-5 mr-2 text-black mt-0.75" />
            Construction Site Tasks
          </header>

          {/* TASKS TABLE HEADER */}
          <article className="outline-2 rounded-lg outline-black/5">
            <header className={`grid grid-cols-[2fr_1fr_1fr_1fr] p-3 text-gray-500 ${inter.className} tracking-tighter font-medium text-sm`}>
              <span>Tasks</span>
              <span>Assignee</span>
              <span>Due Date</span>
              <span>Status</span>
            </header>
            {/* LIST OF TASKS */}
            <div className="">
              {allTasks.length > 0 ? (
                allTasks.map((task: any) => (
                  <TaskRow
                    key={task.id}
                    taskName={task.title}
                    assignee={task.assigned_workers}
                    dueDate={new Date(task.due_date).toLocaleDateString()}
                    status={task.status}
                    className={
                      task.status.toLowerCase() === 'completed'
                        ? 'bg-green-100/50'
                        : task.status.toLowerCase() === 'in_progress'
                          ? 'bg-blue-100/50'
                          : task.status.toLowerCase() === 'cancelled'
                            ? 'bg-red-100/50'
                            : task.status.toLowerCase() === 'pending'
                              ? 'bg-yellow-100/50'
                              : task.status.toLowerCase() === 'blocked'
                                ? 'bg-black/20'
                                : ''
                    } />
                ))
              ) : (
                <p className="p-3 text-gray-500 border-t-2 border-black/5"> No tasks available.</p>
              )}
            </div>
          </article>

          {/* COMPLETED TASKS */}
          <article className="outline-2 rounded-lg outline-black/5">
            <header className={`grid grid-cols-[2fr_1fr_1fr_1fr] p-3 text-gray-500 ${inter.className} tracking-tighter font-medium text-sm`}>
              <span>Tasks</span>
              <span>Assignee</span>
              <span>Due Date</span>
              <span>Status</span>
            </header>
            {/* LIST OF TASKS */}
            <div className="">
              {allCompletedTasks.length > 0 ? (
                allCompletedTasks.map((task: any) => (
                  <TaskRow
                    key={task.id}
                    taskName={task.title}
                    assignee={task.assigned_workers}
                    dueDate={new Date(task.due_date).toLocaleDateString()}
                    status={task.status}
                    className={
                      task.status.toLowerCase() === 'completed'
                        ? 'bg-green-100/50'
                        : task.status.toLowerCase() === 'in_progress'
                          ? 'bg-blue-100/50'
                          : task.status.toLowerCase() === 'cancelled'
                            ? 'bg-red-100/50'
                            : task.status.toLowerCase() === 'pending'
                              ? 'bg-yellow-100/50'
                              : task.status.toLowerCase() === 'blocked'
                                ? 'bg-black/20'
                                : ''
                    } />
                ))
              ) : (
                <p className="p-3 text-gray-500 border-t-2 border-black/5"> No tasks available.</p>
              )}
            </div>
          </article>
        </section>

        {/* RIGHT PANEL */}
        <aside className="flex flex-col gap-7 w-1/2 pl-8">
          {/* TITLE */}
          <section className={`flex flex-col outline-2 rounded-lg p-3 outline-black/5 ${inter.className} tracking-tighter`}>
            <span className="font-semibold text-xl">
              <BellDot className="h-5 w-5 inline-block mr-2 mb-1" />
              News
            </span>
            {/* NEWS */}
            <section className="flex flex-col">
              {/* TITLE */}
              <article className="flex bg-white">
                <section className="w-[700]">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex flex-col items-center gap-2">
                      <span className={`${inter.className} tracking-tighter font-bold text-xs`}>
                        Deportation Request
                      </span>
                    </div>
                  </div>

                  {/* LISTE OF NEWS */}
                  {allNotifications.length > 0 ? (
                    allNotifications.map((news: any) => (
                      <div className="flex" key={news.id}>
                        <span className="w-1 mb-4 h-auto mr-4 bg-blue-600 rounded-full"></span>
                        <NewsSection
                          // key={news.id}
                          title={news.title}
                          subtitle={news.what_we_can_trigger}
                          description={news.what_you_need_to_know}
                        />
                        <section className="flex justify-end items-end w-58 ml-4y">
                          <button className="w-30 h-8 mb-4 bg-blue-600 hover:bg-blue-700 text-white/90 px-4 py-2 rounded-tl-2xl rounded-bl-2xl text-xs font-medium transition-colors" onClick={() => applyChange(news.action_list)}>
                            Apply Change
                          </button>
                          <button className="w-14 h-8 ml-0.5 pr-12 mr-2 mb-4 bg-gray-400 hover:bg-gray-500 text-white/90 px-4 py-2 rounded-tr-2xl rounded-br-2xl text-xs font-medium transition-colors">
                            Cancel
                          </button>
                        </section>
                      </div>
                    ))
                  ) : (
                    <p className="p-3 text-gray-500 border-t-2 border-black/5"> No news yet.</p>
                  )}

                </section>
                {/* BUTTON */}
              </article>

              {/* Notifications */}
              {allTrigeredNotifications.length > 0 ? (
                allTrigeredNotifications.map((notification: any) => (
                  <Notification
                    key={notification.id}
                    type={notification.type}
                    date={new Date(notification.date).toLocaleDateString()}
                    message={notification.title}
                    isActive={notification.is_active}
                  />
                ))
              ) : (
                <p className="p-3 text-gray-500 border-t-2 border-black/5"> No notifications yet.</p>
              )}

            </section>
          </section>


          {/* PROJECT MAP */}
          <section className="rounded-lg overflow-hidden bg-gray-400">
            <div className="relative">
              {/* Map placeholder - you can replace this with an actual map component */}
              <div className="h-48 relative overflow-hidden">
                {/* Background image */}
                <Image src={plan} alt="Project Plan" fill style={{ objectFit: "cover" }} className="absolute inset-0 z-0" priority />
                {/* Map controls overlay */}
                <button className="absolute bottom-4 left-4 flex items-center gap-2 bg-black/50 text-white px-3 py-2 rounded-lg z-10 hover:bg-black/70 transition-colors">
                  <MapIcon className="h-4 w-4" />
                  <span className={`${inter.className} tracking-tighter font-medium text-xs`}>
                    See the project plan
                  </span>
                </button>
              </div>
            </div>
          </section>
        </aside>
      </section>
    </main>
  );
}