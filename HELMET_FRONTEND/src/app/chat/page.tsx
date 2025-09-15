'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Send, ArrowLeft, Mic, Square, Play, Pause } from 'lucide-react';

import { Inter } from "next/font/google";
import { div } from 'framer-motion/m';

import StaticEmojiBackground from '../../components/EmojiBgComponent';

import ChatComponent from '../../components/ChatComponent';

export default function ChatComponentWithBg() {

	return (
		<StaticEmojiBackground children={<ChatComponent />} opacity={0.05} emojis={['🚧', '🏗️', '👷‍♂️', '🦺']} />
	);
}
