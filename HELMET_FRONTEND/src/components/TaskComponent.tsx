import { RectangleStackIcon } from "@heroicons/react/24/outline";
import React from "react";
import { useState, useRef } from "react";
import { Inter } from "next/font/google";

// import TaskCard from "./TaskInfoComponent";

import { XCircleIcon } from "@heroicons/react/24/solid";

const inter = Inter({ subsets: ["latin"] });

interface Task {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'todo' | 'in-progress' | 'completed' | 'overdue';
  dueDate?: string;
  estimatedTime?: string;
  assignee?: string;
  tags?: string[];
  progress?: number;
}

export default function TaskComponent({ task, TaskCardRef }: { task: Task | null, TaskCardRef: React.RefObject<HTMLDivElement | null> }) {
	const getStringDate = (dateString?: string) => {
		if (!dateString) return null;
		const date = new Date(dateString);
		return date.toLocaleDateString('fr-FR', {
			day: 'numeric', 
			month: 'short'
		});
	}
	
	const task1 : Task = {
		id: '1',
		title: 'Préparer la présentation',
		description: 'Créer des diapositives et des notes pour la réunion avec le client.',
		priority: 'high',
		status: 'in-progress',
		dueDate: '2023-10-15',
		estimatedTime: '2h',
		assignee: 'Alice',
		tags: ['presentation', 'client'],
		progress: 75
	};

	const [DisplayTaskInfo, setDisplayTaskInfo] = useState(false);

	const handleOverlayClick = (e: React.MouseEvent) => {
		if (DisplayTaskInfo)
			if (!TaskCardRef.current?.contains(e.target as Node)) {
				setDisplayTaskInfo(false);
			}
		};

	return (
		<>
			{/* Le bouton reste toujours affiché */}
			<button className="relative flex flex-col items-center mb-10" onClick={() => setDisplayTaskInfo(!DisplayTaskInfo)}>
				{/* Gradient background */}
				<div className="absolute inset-0"></div>
				<div className="relative z-10 flex flex-col items-center">
					<div className="p-4 bg-amber-500/10 mb-4 backdrop-blur-lg shadow-xl active:scale-95 transition-transform duration-100 rounded-2xl">
						<RectangleStackIcon className="h-12 w-12 text-amber-600" />
					</div>
					<span className="text-base font-semibold text-amber-600">Tâches</span>
				</div>
			</button>

			{/* L'overlay s'affiche EN PLUS du bouton */}
			{DisplayTaskInfo && (
				// <TaskCard task={task1}  />
				<div className="fixed inset-0 backdrop-blur-lg p-6 flex flex-col items-center justify-center text-center z-50 bg-black/5" onClick={handleOverlayClick}>
					<div className={`drop-shadow-2xl bg-white w-80 max-w-[90vw] h-128 max-h-[80vh] overflow-auto p-6 rounded-2xl ${inter.className}`}  ref={TaskCardRef}>
						<h2 className="text-xl font-bold mb-4 text-gray-800">Détails de la tâche</h2>
						<div className="text-left text-gray-700 space-y-3">
							<p className="text-gray-600">Progression</p>
							<div className="w-full bg-gray-200 rounded-full h-4 mb-4">
								<div className="bg-amber-500 h-4 rounded-full" style={{ width: `${task?.progress}%` }}></div>
							</div>
							<p className="text-gray-600">Priorité : <span className={`px-2 py-1 rounded-full text-white ${task?.priority === 'urgent' ? 'bg-red-500' : task1.priority === 'high' ? 'bg-orange-500' : task1.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'}`}>{task1.priority}</span></p>
							<p className="text-gray-600">Statut : <span className={`px-2 py-1 rounded-full ${task?.status === 'completed' ? 'text-green-600 bg-green-100' : task1.status === 'in-progress' ? 'text-blue-600 bg-blue-100' : task1.status === 'overdue' ? 'text-red-600 bg-red-100' : 'text-gray-600 bg-gray-100'}`}>{task1.status}</span></p>
							<p className="text-gray-600">Date d'échéance : {getStringDate(task?.dueDate)}</p>
							<br />
							<p className="text-gray-600">Description de la tâche :</p>
							<p className="text-gray-800">{task?.description}</p>
						</div>
						
					</div>
					<XCircleIcon className="mt-8 h-14 w-14 text-white hover:text-gray-300 cursor-pointer transition-colors" />
				</div>
			)}
		</>
	);
}