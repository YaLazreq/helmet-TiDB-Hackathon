import React from 'react';
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

// Interface pour TypeScript (optionnel)
interface TaskRowProps {
  taskName: string;
  assignee: string;
  dueDate: string;
  status: string;
  className?: string;
}

// Composant TaskRow
const TaskRow = ({ 
  taskName, 
  assignee, 
  dueDate, 
  status, 
  className = "" 
}: TaskRowProps) => {
  
  // Fonction pour déterminer la couleur du statut
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'text-green-600';
      case 'in_progress':
        return 'text-blue-600';
      case 'pending':
        return 'text-yellow-600';
      case 'cancelled':
        return 'text-red-600';
			case 'blocked':
				return 'text-gray-600';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <article 
			className={`w-full grid grid-cols-[2fr_1fr_1fr_1fr] border-t-2 p-3 border-black/5 text-gray-500 ${inter.className} tracking-tighter font-medium text-xs ${className}`}>
			<span className="text-gray-800">{taskName}</span>
			<span>{assignee}</span>
			<span>{dueDate}</span>
			<span className={getStatusColor(status)}>{status}</span>
		</article>
  );
}

export default TaskRow;