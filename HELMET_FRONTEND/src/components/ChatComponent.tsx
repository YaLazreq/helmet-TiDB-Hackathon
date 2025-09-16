'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Send, ArrowLeft, Mic, Square, Play, Pause } from 'lucide-react';

import { Inter } from "next/font/google";
import { div } from 'framer-motion/m';

import LoadingSquare from './LoadingComponent';

const inter = Inter({
	variable: "--font-inter",
	subsets: ["latin"],
});

interface Message {
	id: number;
	conversationId: number;
	text?: string;
	audioUrl?: string;
	audioDuration?: number;
	sender: 'me' | 'helmet';
	timestamp: string;
	type: 'text' | 'audio';
}

interface ChatComponentProps {
	chatOpened: boolean;
	setChatOpened: (value: boolean) => void;
}

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

export default function ChatComponent() {

	const router = useRouter();

	const { data } = useWebSocket('http://localhost:8000/ws');

	const [newMessage, setNewMessage] = useState('');
	const [isRecording, setIsRecording] = useState(false);
	const [recordingTime, setRecordingTime] = useState(0);
	const [playingAudio, setPlayingAudio] = useState<number | null>(null);

	const mediaRecorderRef = useRef<MediaRecorder | null>(null);
	const audioChunksRef = useRef<Blob[]>([]);
	const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
	const audioRefs = useRef<{ [key: number]: HTMLAudioElement }>({});

	const [messages, setMessages] = useState<Message[]>([]);

	const messagesRef = useRef<HTMLDivElement>(null);

	const [userId, setUserId] = useState(0);

	const [waitForResponse, setWaitForResponse] = useState(false);

	useEffect(() => {
		console.log("WebSocket data received:", data);
		if (data?.ding !== "message") {
			return;
		}
		console.log("New message from WebSocket:", data);
		if (userId === 0) return;

		const fetchMessages = async () => {
			const response = await fetch(`http://localhost:8000/messages/${userId}/conv_1`);
			const data = await response.json();

			console.log("for id:", userId);
			console.log(data);
			const messages = data.messages.map((msg: any) => ({
				id: msg.id,
				conversationId: msg.conversation_id,
				text: msg.text,
				audioUrl: msg.audio_url,
				audioDuration: msg.audio_duration,
				sender: msg.sender,
				timestamp: msg.timestamp,
				type: msg.type
			}));

			setMessages(messages);
		}

		fetchMessages();

		if (messages[messages.length - 1]?.sender === 'helmet') {
			setWaitForResponse(false);
		}
	}, [data]);

	useEffect(() => {
		if (messagesRef.current) {
			messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
		}

		if (messages.length > 0 && messages[messages.length - 1]?.sender === 'me') {
			setWaitForResponse(true);
		} else {
			setWaitForResponse(false);
		}
	}, [messages]);

	useEffect(() => {
		if (userId === 0) return;

		const fetchMessages = async () => {
			const response = await fetch(`http://localhost:8000/messages/${userId}/conv_1`);
			const data = await response.json();

			console.log("for id:", userId);
			console.log(data);
			const messages = data.messages.map((msg: any) => ({
				id: msg.id,
				conversationId: msg.conversation_id,
				text: msg.text,
				audioUrl: msg.audio_url,
				audioDuration: msg.audio_duration,
				sender: msg.sender,
				timestamp: msg.timestamp,
				type: msg.type
			}));

			setMessages(messages);
		}

		fetchMessages();
	}, [userId]);

	useEffect(() => {
		console.log("Fetching user ID from session storage");
		const Id = sessionStorage.getItem("userId");
		if (Id !== null) {
			setUserId(parseInt(Id));
			console.log("User ID set to:", Id);
		}
	}, []);

	const handleSendMessage = () => {
		if (messages[messages.length - 1]?.sender === 'me') {
			return;
		}

		setWaitForResponse(true);

		if (newMessage.trim()) {
			const message: Message = {
				id: Date.now(),
				conversationId: 1,
				text: newMessage,
				sender: 'me',
				timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
				type: 'text'
			};
			setMessages([...messages, message]);
			setNewMessage('');

			const apiPayload = {
				client_id: userId.toString(),
				conversation_id: "conv_1",
				text: newMessage,
				sender: 'me',
				type: 'text'
			};

			fetch('http://localhost:8000/messages', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(apiPayload)
			});

			const apiPayloadSupervisor = {
				message: "[User ID: " + userId.toString() + " - Message Date: " + " 12 septembre 2025 " + "]: " + newMessage
			};

			// alert(apiPayloadSupervisor.message);
			// return;
			fetch('http://localhost:8000/call_supervisor', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(apiPayloadSupervisor)
			});
		}
	};

	const handleKeyPress = (e: React.KeyboardEvent) => {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSendMessage();
		}
	};

	const startRecording = async () => {
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			const mediaRecorder = new MediaRecorder(stream);

			mediaRecorderRef.current = mediaRecorder;
			audioChunksRef.current = [];

			mediaRecorder.ondataavailable = (event) => {
				audioChunksRef.current.push(event.data);
			};

			mediaRecorder.onstop = () => {
				const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
				const audioUrl = URL.createObjectURL(audioBlob);

				const message: Message = {
					id: Date.now(),
					conversationId: 1,
					audioUrl,
					audioDuration: recordingTime,
					sender: 'me',
					timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
					type: 'audio'
				};

				setMessages(prev => [...prev, message]);

				// Arrêter le stream
				stream.getTracks().forEach(track => track.stop());
			};

			mediaRecorder.start();
			setIsRecording(true);
			setRecordingTime(0);

			// Commencer le timer
			recordingIntervalRef.current = setInterval(() => {
				setRecordingTime(prev => prev + 1);
			}, 1000);

		} catch (error) {
			console.error('Erreur lors de l\'accès au microphone:', error);
			alert('Impossible d\'accéder au microphone. Veuillez autoriser l\'accès.');
		}
	};

	const stopRecording = () => {
		if (mediaRecorderRef.current && isRecording) {
			mediaRecorderRef.current.stop();
			setIsRecording(false);

			if (recordingIntervalRef.current) {
				clearInterval(recordingIntervalRef.current);
			}
		}
	};

	const playAudio = (messageId: number, audioUrl: string) => {
		// Arrêter tout autre audio en cours
		Object.values(audioRefs.current).forEach(audio => {
			audio.pause();
			audio.currentTime = 0;
		});

		if (playingAudio === messageId) {
			setPlayingAudio(null);
			return;
		}

		const audio = new Audio(audioUrl);
		audioRefs.current[messageId] = audio;

		audio.onended = () => {
			setPlayingAudio(null);
		};

		audio.play();
		setPlayingAudio(messageId);
	};

	const formatTime = (seconds: number) => {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	};

	const AudioMessage = ({ message }: { message: Message }) => (
		<div className={`flex items-center space-x-3 p-3 rounded-2xl ${message.sender === 'me'
			? 'bg-orange-100 text-gray-900'
			: 'bg-white text-gray-900 shadow-sm'
			}`}>
			<button
				onClick={() => playAudio(message.id, message.audioUrl!)}
				className={`p-2 rounded-full ${message.sender === 'me' ? 'bg-orange-200' : 'bg-gray-100'
					}`}
			>
				{playingAudio === message.id ? (
					<Pause size={16} />
				) : (
					<Play size={16} />
				)}
			</button>

			<div className="flex-1">
				<div className={`h-1 rounded-full ${message.sender === 'me' ? 'bg-orange-200' : 'bg-gray-200'
					}`}>
					<div className={`h-full w-1/3 rounded-full ${message.sender === 'me' ? 'bg-orange-400' : 'bg-gray-400'
						}`}></div>
				</div>
			</div>

			<span className="text-xs text-gray-500">
				{formatTime(message.audioDuration || 0)}
			</span>
		</div>
	);

	return (
		<div className="h-screen flex flex-col max-w mx-auto">
			{/* Header */}
			{messages.length > 0 && waitForResponse &&
				<div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-150">
					<LoadingSquare size="xl" className="bg-transparent" />
				</div>
			}
			<div>
				<div className="absolute top-0 left-0 right-0 h-20 bg-white/10 backdrop-blur-2xl z-10"></div>

				<div className="w-full flex items-center justify-between p-4 bg-transparent border-b border-gray-100 absolute top-0 z-20">
					<div className="flex items-center">
						<button className="p-1 mr-3 text-gray-600" onClick={() => router.back()}>
							<ArrowLeft size={24} />
						</button>
						<div className="relative">
						</div>
						<div className="ml-3">
							<h1 className="font-semibold text-gray-900 text-lg">Helmet</h1>
							<p className="text-sm text-green-500">En ligne</p>
						</div>
					</div>
				</div>
			</div>

			{/* Messages */}
			<div ref={messagesRef} className="flex-1 pt-28 pb-28 overflow-y-auto pr-8 pl-8 pb-8 space-y-8 bg-transparent">
				{messages.map((message, index) => {
					// Vérifier si c'est un nouveau sender par rapport au message précédent
					const previousMessage = index > 0 ? messages[index - 1] : null;
					const showSenderName = !previousMessage || message.sender !== previousMessage.sender;

					return (
						<div key={message.id} className={`flex flex-col ${inter.className}`}>
							{showSenderName && (
								<p className={`flex ${message.sender === 'me' ? 'justify-end' : 'justify-start'} mb-1`}>
									<span className="text-xs text-gray-500 mr-5 ml-5">
										{message.sender === 'me' ? 'Moi' : 'Helmet'}
									</span>
								</p>
							)}
							<div className={`flex ${message.sender === 'me' ? 'justify-end' : 'justify-start'}`}>
								<div className={`max-w-[280px] shadow-md ${message.type === 'text' ? 'p-4' : 'p-2'} rounded-4xl ${message.sender === 'me' ? 'bg-white text-gray-900' : 'bg-orange-100 text-gray-900'}`}>
									{message.type === 'text' ? (
										<>
											<p className="text-md leading-relaxed">{message.text}</p>
										</>
									) : (
										<div>
											<AudioMessage message={message} />
										</div>
									)}
								</div>
							</div>
						</div>
					);
				})}
			</div>

			{/* Zone de saisie */}
			<div className="absolute bottom-0 left-0 right-0 p-4 bg-transparent backdrop-blur-xl border-t border-gray-200/50">
				<div className="flex items-end space-x-3">
					<div className="flex-1 relative">
						<textarea
							value={newMessage}
							onChange={(e) => setNewMessage(e.target.value)}
							onKeyPress={handleKeyPress}
							placeholder="Message..."
							disabled={isRecording}
							className="w-full px-4 py-3 pr-20 bg-white backdrop-blur-sm rounded-full resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white/90 border border-transparent focus:border-blue-500 text-sm disabled:opacity-50"
							rows={1}
							style={{ minHeight: '44px', maxHeight: '100px' }}
						/>
					</div>

					<button
						onClick={isRecording ? stopRecording : startRecording}
						className={`p-3 rounded-full transition-colors shadow-lg backdrop-blur-sm ${isRecording
							? 'bg-red-500/90 hover:bg-red-600/90 text-white'
							: 'text-gray-500 hover:text-gray-700 bg-gray-100/70 hover:bg-gray-200/70'
							}`}
					>
						{isRecording ? <Square size={22} /> : <Mic size={22} />}
					</button>

					<button
						onClick={handleSendMessage}
						disabled={!newMessage.trim() || isRecording}
						className="bg-orange-500/90 backdrop-blur-sm disabled:bg-transparent disabled:text-gray-300 text-white p-3 rounded-full transition-colors shadow-lg hover:bg-orange-600/90"
					>
						<Send size={18} />
					</button>
				</div>
			</div>
		</div>
	)
}
