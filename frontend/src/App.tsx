import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import {
  Video,
  FileText,
  Music,
  Image as ImageIcon,
  Send,
  Sparkles,
  Bot,
  User,
  Play,
  Clock,
  Layers,
  RefreshCw,
  Trash2,
  ChevronRight,
  Sliders,
  Film,
  Zap,
  Sun,
  Moon
} from 'lucide-react';

interface Scene {
  seconds: number;
  timestamp: string;
  title: string;
  tag: string;
  score: number;
}

interface UploadDetails {
  video?: { filename: string; size_mb: number; url: string; scenes: Scene[] };
  pdf?: { filename: string; pages: number; preview: string; char_count: number };
  audio?: { filename: string; duration_sec?: number; size_mb?: number; format?: string; sample_rate?: number };
  image?: { filename: string; dimensions: string; format: string; mode: string };
}

interface TimestampRef {
  time: string;
  seconds: number;
  label: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamps?: TimestampRef[];
  weights?: { video: number; pdf: number; audio: number; image: number };
  time: string;
}

const BACKEND_URL = 'http://localhost:8000';

export default function App() {
  // Modal asset files
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string>('');
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);

  // Video player ref and active time
  const videoPlayerRef = useRef<HTMLVideoElement | null>(null);
  const [videoCurrentTime, setVideoCurrentTime] = useState<number>(0);
  const [isVideoPlaying, setIsVideoPlaying] = useState<boolean>(false);

  // Processing & State
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadResult, setUploadResult] = useState<{ uploaded: string[]; details: UploadDetails } | null>(null);
  const [activeTab, setActiveTab] = useState<'video-sync' | 'chat' | 'knowledge'>('video-sync');
  const [serverOnline, setServerOnline] = useState<boolean | null>(null);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

  // Active Cross-Modal Attention Weights
  const [attentionWeights, setAttentionWeights] = useState({
    video: 40,
    pdf: 30,
    audio: 15,
    image: 15,
  });

  // Chat State
  const [inputQuery, setInputQuery] = useState('');
  const [isChatting, setIsChatting] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init-1',
      role: 'assistant',
      content: '⚡ **Multimodal Video RAG Engine Ready.**\n\nUpload a **Video file** to unlock synchronized keyframe scrubbing, temporal scene timestamps, and cross-modal reasoning combined with documents, audio, and visual frames.',
      sources: ['Temporal Core', 'Multi-Modality Vector'],
      timestamps: [
        { time: '00:12', seconds: 12, label: 'Executive Summary' },
        { time: '01:38', seconds: 98, label: 'Visual Benchmarks' },
      ],
      weights: { video: 50, pdf: 25, audio: 15, image: 10 },
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Check backend server status
  const checkServerStatus = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/status`, { signal: AbortSignal.timeout(3000) });
      setServerOnline(res.ok);
    } catch {
      setServerOnline(false);
    }
  };

  useEffect(() => {
    checkServerStatus();
    const interval = setInterval(checkServerStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Video file selection handler
  const handleVideoSelect = (file: File | null) => {
    setVideoFile(file);
    if (file) {
      const localUrl = URL.createObjectURL(file);
      setVideoPreviewUrl(localUrl);
    } else {
      setVideoPreviewUrl('');
    }
  };

  // Seek video to exact second
  const seekVideo = (seconds: number) => {
    if (videoPlayerRef.current) {
      videoPlayerRef.current.currentTime = seconds;
      videoPlayerRef.current.play().catch(() => {});
      setIsVideoPlaying(true);
    }
  };

  // Load sample demo video & data for instant WOW testing
  const loadDemoSample = async () => {
    try {
      await fetch(`${BACKEND_URL}/demo`, { method: 'POST' });
    } catch (e) {
      console.warn('Backend demo sync error:', e);
    }
    // High quality tech demo video MP4 stream
    const demoVideoUrl = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4';
    setVideoPreviewUrl(demoVideoUrl);
    setUploadResult({
      uploaded: ['multimodal_overview_presentation.mp4', 'q3_earnings_financials.pdf'],
      details: {
        video: {
          filename: 'multimodal_overview_presentation.mp4',
          size_mb: 28.4,
          url: demoVideoUrl,
          scenes: [
            { seconds: 12, timestamp: '00:12', title: 'Opening & Executive Summary', tag: 'Intro', score: 0.98 },
            { seconds: 35, timestamp: '00:35', title: 'System Architecture & Vector DB', tag: 'Architecture', score: 0.94 },
            { seconds: 60, timestamp: '01:00', title: 'Live Benchmarks & Results', tag: 'Metrics', score: 0.96 },
            { seconds: 90, timestamp: '01:30', title: 'Feature Walkthrough & Conclusion', tag: 'Demo', score: 0.91 },
          ],
        },
        pdf: {
          filename: 'q3_earnings_financials.pdf',
          pages: 14,
          preview: 'Executive Summary: Overall system throughput increased by 42% with multimodal vector indexing...',
          char_count: 18450,
        },
      },
    });

    setMessages((prev) => [
      ...prev,
      {
        id: String(Date.now()),
        role: 'assistant',
        content: '🎬 **Sample Video & Financial PDF Indexed!**\nClick any timestamp below (e.g. `00:12` or `01:00`) to jump directly into the video timeline.',
        sources: ['Video Stream', 'PDF Document'],
        timestamps: [
          { time: '00:12', seconds: 12, label: 'Opening Scene' },
          { time: '00:35', seconds: 35, label: 'Architecture' },
          { time: '01:00', seconds: 60, label: 'Benchmarks' },
        ],
        weights: { video: 55, pdf: 30, audio: 10, image: 5 },
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  // Upload and process files
  const handleProcessAssets = async () => {
    if (!videoFile && !pdfFile && !audioFile && !imageFile) {
      alert('Please select at least one multimodal file (Video, PDF, Audio, or Image).');
      return;
    }

    setIsProcessing(true);
    const formData = new FormData();
    if (videoFile) formData.append('video', videoFile);
    if (pdfFile) formData.append('pdf', pdfFile);
    if (audioFile) formData.append('audio', audioFile);
    if (imageFile) formData.append('image', imageFile);

    try {
      const res = await fetch(`${BACKEND_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Upload error');
      const data = await res.json();
      setUploadResult(data);

      if (data.details?.video?.url && !videoPreviewUrl) {
        setVideoPreviewUrl(data.details.video.url);
      }

      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now()),
          role: 'assistant',
          content: `🚀 **Indexed ${data.uploaded.length} Multimodal Modalities!**\nVideo keyframes and scene boundaries have been synthesized into vector coordinates.`,
          sources: data.uploaded,
          timestamps: data.details?.video?.scenes?.map((s: Scene) => ({
            time: s.timestamp,
            seconds: s.seconds,
            label: s.title,
          })) || [],
          weights: {
            video: videoFile ? 50 : 0,
            pdf: pdfFile ? 30 : 0,
            audio: audioFile ? 15 : 0,
            image: imageFile ? 15 : 0,
          },
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err: any) {
      alert(`Backend issue: ${err.message}. Ensure FastAPI is running on port 8000.`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Send Chat Query
  const handleSendMessage = async (queryToSend?: string) => {
    const q = (queryToSend || inputQuery).trim();
    if (!q || isChatting) return;

    const userMsg: Message = {
      id: String(Date.now()),
      role: 'user',
      content: q,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsChatting(true);
    setActiveTab('chat');

    try {
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: q }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();

      if (data.weights) {
        setAttentionWeights(data.weights);
      }

      const assistantMsg: Message = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: data.reply,
        sources: data.sources,
        timestamps: data.timestamps,
        weights: data.weights,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now() + 1),
          role: 'assistant',
          content: `⚠️ Response error: ${err?.message || 'Server error'}. Please make sure FastAPI backend is running.`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsChatting(false);
    }
  };

  const activeScenes: Scene[] = uploadResult?.details?.video?.scenes || [
    { seconds: 12, timestamp: '00:12', title: 'Intro & Key Problem', tag: 'Intro', score: 0.95 },
    { seconds: 45, timestamp: '00:45', title: 'Architecture Flow', tag: 'Deep Dive', score: 0.91 },
    { seconds: 98, timestamp: '01:38', title: 'Benchmark Comparisons', tag: 'Analytics', score: 0.98 },
    { seconds: 160, timestamp: '02:40', title: 'Live Execution & Output', tag: 'Execution', score: 0.88 },
  ];

  return (
    <div className={`flex flex-col h-screen antialiased overflow-hidden font-sans ${
      isDarkMode
        ? 'bg-[#070a13] text-slate-100 selection:bg-cyan-500 selection:text-black'
        : 'bg-[#f8fafc] text-slate-800 selection:bg-indigo-500 selection:text-white'
    }`}>
      {/* Top Header */}
      <header className={`h-16 border-b px-6 flex items-center justify-between shrink-0 z-30 transition-colors ${
        isDarkMode
          ? 'border-cyan-950/60 bg-[#090e1c]/90 backdrop-blur-xl'
          : 'border-slate-200/80 bg-white/95 backdrop-blur-xl shadow-xs'
      }`}>
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
              isDarkMode
                ? 'bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 shadow-[0_0_20px_rgba(6,182,212,0.35)] border-cyan-400/30'
                : 'bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 shadow-md shadow-indigo-500/20 border-indigo-200'
            }`}>
              <Film className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div className={`absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full border-2 flex items-center justify-center ${
              isDarkMode ? 'bg-cyan-400 border-[#090e1c]' : 'bg-emerald-500 border-white'
            }`}>
              <Zap className={`w-2 h-2 ${isDarkMode ? 'text-black' : 'text-white'}`} />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className={`font-extrabold text-base tracking-tight flex items-center gap-1.5 ${
                isDarkMode ? 'text-white' : 'text-slate-900'
              }`}>
                <span>HYPER-MODAL</span>
                <span className={`bg-gradient-to-r bg-clip-text text-transparent ${
                  isDarkMode ? 'from-cyan-400 to-indigo-400' : 'from-indigo-600 via-purple-600 to-pink-600'
                }`}>
                  VIDEO RAG
                </span>
              </h1>
              <span className={`text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full border ${
                isDarkMode
                  ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                  : 'bg-indigo-50 text-indigo-600 border-indigo-200'
              }`}>
                Synchronized Vision
              </span>
            </div>
            <p className={`text-[11px] flex items-center gap-1 ${
              isDarkMode ? 'text-slate-400' : 'text-slate-500'
            }`}>
              <span>Temporal Video</span> • <span>PDF Text</span> • <span>Acoustic Audio</span> • <span>Frame VQA</span>
            </p>
          </div>
        </div>

        {/* Action Center & Backend Status */}
        <div className="flex items-center gap-2.5">
          {/* Light / Dark Mode Toggle */}
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition cursor-pointer ${
              isDarkMode
                ? 'bg-slate-800/80 border-slate-700 text-amber-300 hover:bg-slate-700 hover:text-amber-200'
                : 'bg-slate-100 hover:bg-slate-200/80 border-slate-200 text-slate-700 shadow-2xs'
            }`}
            title={isDarkMode ? 'Switch to Bright Light Theme' : 'Switch to Dark Theme'}
          >
            {isDarkMode ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5 text-indigo-600" />}
            <span>{isDarkMode ? 'Light Theme' : 'Dark Theme'}</span>
          </button>

          <button
            onClick={loadDemoSample}
            className={`hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition cursor-pointer ${
              isDarkMode
                ? 'bg-gradient-to-r from-indigo-900/60 to-purple-900/60 hover:from-indigo-800/80 hover:to-purple-800/80 border-indigo-500/40 text-indigo-200 hover:text-white shadow-sm shadow-indigo-900/30'
                : 'bg-indigo-50 hover:bg-indigo-100/80 border-indigo-200/80 text-indigo-700 shadow-2xs'
            }`}
          >
            <Sparkles className={`w-3.5 h-3.5 ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`} />
            <span>Load Demo Video & Data</span>
          </button>

          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs ${
            isDarkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200 shadow-2xs'
          }`}>
            <div
              className={`w-2 h-2 rounded-full ${
                serverOnline === true
                  ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.7)]'
                  : serverOnline === false
                  ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.7)]'
                  : 'bg-amber-400 animate-pulse'
              }`}
            />
            <span className={`font-medium ${isDarkMode ? 'text-slate-300' : 'text-slate-700'}`}>
              {serverOnline === true ? 'FastAPI :8000' : serverOnline === false ? 'Offline' : 'Connecting'}
            </span>
            <button onClick={checkServerStatus} className={`transition ${
              isDarkMode ? 'text-slate-500 hover:text-slate-200' : 'text-slate-400 hover:text-slate-600'
            }`}>
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Drawer: Multimodal Ingestion Rack */}
        <aside className={`w-80 lg:w-88 border-r flex flex-col shrink-0 overflow-y-auto transition-colors ${
          isDarkMode
            ? 'border-slate-800/80 bg-[#090d19]/80 backdrop-blur-md'
            : 'border-slate-200/90 bg-white/90 backdrop-blur-md shadow-xs'
        }`}>
          <div className={`p-4 border-b flex items-center justify-between ${
            isDarkMode ? 'border-slate-800/60' : 'border-slate-100'
          }`}>
            <div>
              <span className={`text-[11px] font-bold uppercase tracking-wider flex items-center gap-1 ${
                isDarkMode ? 'text-cyan-400' : 'text-indigo-600'
              }`}>
                <Layers className="w-3 h-3" />
                Modality Matrix
              </span>
              <h2 className={`text-sm font-semibold mt-0.5 ${
                isDarkMode ? 'text-slate-100' : 'text-slate-800'
              }`}>Ingest Multimodal Assets</h2>
            </div>
            <span className={`text-[11px] px-2 py-0.5 rounded font-medium ${
              isDarkMode ? 'bg-slate-800 text-slate-400' : 'bg-slate-100 text-slate-600'
            }`}>4 Slots</span>
          </div>

          <div className="p-4 space-y-3 flex-1 text-xs">
            {/* Slot 1: 🎥 VIDEO (Hero Modality) */}
            <div className={`p-3 rounded-xl border transition group ${
              isDarkMode
                ? 'border-cyan-500/30 bg-cyan-950/20 hover:border-cyan-500/60 shadow-sm shadow-cyan-950/30'
                : 'border-indigo-200 bg-indigo-50/40 hover:border-indigo-300 shadow-2xs'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`p-1.5 rounded-lg border ${
                    isDarkMode
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                      : 'bg-indigo-100 text-indigo-700 border-indigo-200'
                  }`}>
                    <Video className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className={`font-semibold flex items-center gap-1 ${
                      isDarkMode ? 'text-slate-100' : 'text-slate-800'
                    }`}>
                      <span>Video Recording</span>
                      <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono font-bold ${
                        isDarkMode ? 'bg-cyan-400/20 text-cyan-300' : 'bg-indigo-100 text-indigo-700'
                      }`}>HERO</span>
                    </h3>
                    <p className={`text-[10px] ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>MP4, WEBM with Keyframes</p>
                  </div>
                </div>
                {videoFile && (
                  <button onClick={() => handleVideoSelect(null)} className="text-slate-400 hover:text-rose-500">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
              <label className={`flex flex-col items-center justify-center border border-dashed rounded-lg p-2.5 cursor-pointer transition text-center ${
                isDarkMode
                  ? 'border-cyan-700/50 hover:border-cyan-400 bg-slate-900/60'
                  : 'border-indigo-200 hover:border-indigo-400 bg-white hover:bg-indigo-50/50 shadow-2xs'
              }`}>
                <input
                  type="file"
                  accept="video/mp4,video/webm,video/quicktime"
                  className="hidden"
                  onChange={(e) => handleVideoSelect(e.target.files?.[0] || null)}
                />
                <Film className={`w-4 h-4 mb-1 ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`} />
                <span className={`font-medium truncate max-w-[200px] ${isDarkMode ? 'text-slate-200' : 'text-slate-700'}`}>
                  {videoFile ? videoFile.name : 'Select Video File'}
                </span>
                <span className={`text-[10px] mt-0.5 ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                  {videoFile ? `${(videoFile.size / (1024 * 1024)).toFixed(1)} MB` : 'Enables synchronized playback'}
                </span>
              </label>
            </div>

            {/* Slot 2: 📄 PDF Document */}
            <div className={`p-3 rounded-xl border transition ${
              isDarkMode
                ? 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
                : 'border-slate-200 bg-white hover:border-slate-300 shadow-2xs'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-red-500/10 text-red-600 border border-red-500/20">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className={`font-semibold ${isDarkMode ? 'text-slate-200' : 'text-slate-800'}`}>PDF Document</h3>
                    <p className={`text-[10px] ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>Structured Text & Tables</p>
                  </div>
                </div>
                {pdfFile && (
                  <button onClick={() => setPdfFile(null)} className="text-slate-400 hover:text-rose-500">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
              <label className={`flex flex-col items-center justify-center border border-dashed rounded-lg p-2.5 cursor-pointer transition text-center ${
                isDarkMode
                  ? 'border-slate-700 hover:border-indigo-400 bg-slate-900/60'
                  : 'border-slate-200 hover:border-indigo-400 bg-slate-50/70 hover:bg-slate-100/70 shadow-2xs'
              }`}>
                <input
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  onChange={(e) => setPdfFile(e.target.files?.[0] || null)}
                />
                <span className={`font-medium truncate max-w-[200px] ${isDarkMode ? 'text-slate-200' : 'text-slate-700'}`}>
                  {pdfFile ? pdfFile.name : 'Select PDF'}
                </span>
              </label>
            </div>

            {/* Slot 3: 🎙️ Audio Track */}
            <div className={`p-3 rounded-xl border transition ${
              isDarkMode
                ? 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
                : 'border-slate-200 bg-white hover:border-slate-300 shadow-2xs'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
                    <Music className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className={`font-semibold ${isDarkMode ? 'text-slate-200' : 'text-slate-800'}`}>Audio Track</h3>
                    <p className={`text-[10px] ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>WAV, MP3 Voice Notes</p>
                  </div>
                </div>
                {audioFile && (
                  <button onClick={() => setAudioFile(null)} className="text-slate-400 hover:text-rose-500">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
              <label className={`flex flex-col items-center justify-center border border-dashed rounded-lg p-2.5 cursor-pointer transition text-center ${
                isDarkMode
                  ? 'border-slate-700 hover:border-emerald-400 bg-slate-900/60'
                  : 'border-slate-200 hover:border-emerald-500 bg-slate-50/70 hover:bg-slate-100/70 shadow-2xs'
              }`}>
                <input
                  type="file"
                  accept="audio/*,.wav,.mp3"
                  className="hidden"
                  onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                />
                <span className={`font-medium truncate max-w-[200px] ${isDarkMode ? 'text-slate-200' : 'text-slate-700'}`}>
                  {audioFile ? audioFile.name : 'Select Audio'}
                </span>
              </label>
            </div>

            {/* Slot 4: 🖼️ Image / Frame */}
            <div className={`p-3 rounded-xl border transition ${
              isDarkMode
                ? 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
                : 'border-slate-200 bg-white hover:border-slate-300 shadow-2xs'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-purple-500/10 text-purple-600 border border-purple-500/20">
                    <ImageIcon className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className={`font-semibold ${isDarkMode ? 'text-slate-200' : 'text-slate-800'}`}>Visual Frame</h3>
                    <p className={`text-[10px] ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>PNG, JPG Visual Evidence</p>
                  </div>
                </div>
                {imageFile && (
                  <button onClick={() => setImageFile(null)} className="text-slate-400 hover:text-rose-500">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
              <label className={`flex flex-col items-center justify-center border border-dashed rounded-lg p-2.5 cursor-pointer transition text-center ${
                isDarkMode
                  ? 'border-slate-700 hover:border-purple-400 bg-slate-900/60'
                  : 'border-slate-200 hover:border-purple-500 bg-slate-50/70 hover:bg-slate-100/70 shadow-2xs'
              }`}>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                />
                <span className={`font-medium truncate max-w-[200px] ${isDarkMode ? 'text-slate-200' : 'text-slate-700'}`}>
                  {imageFile ? imageFile.name : 'Select Image'}
                </span>
              </label>
            </div>

            {/* Indexing Trigger Button */}
            <button
              onClick={handleProcessAssets}
              disabled={isProcessing || (!videoFile && !pdfFile && !audioFile && !imageFile && !videoPreviewUrl)}
              className={`w-full py-3 px-4 rounded-xl font-semibold text-sm transition flex items-center justify-center gap-2 cursor-pointer mt-2 disabled:opacity-40 disabled:cursor-not-allowed ${
                isDarkMode
                  ? 'text-black bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400 hover:opacity-90 shadow-[0_0_20px_rgba(6,182,212,0.3)]'
                  : 'text-white bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 hover:opacity-95 shadow-md shadow-indigo-500/25'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>{isProcessing ? 'Vectorizing Coordinates...' : 'Index Multi-Modal Context'}</span>
            </button>

            {/* Cross-Modal Attention Distribution Widget */}
            <div className={`mt-4 p-3 rounded-xl border space-y-2 ${
              isDarkMode ? 'border-slate-800 bg-slate-900/70' : 'border-slate-200/90 bg-slate-50/80 shadow-2xs'
            }`}>
              <div className="flex items-center justify-between text-[11px] font-semibold">
                <span className={`flex items-center gap-1.5 ${isDarkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                  <Sliders className={`w-3.5 h-3.5 ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`} />
                  Attention Heatmap
                </span>
                <span className={`text-[10px] font-mono ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`}>Dynamic Weights</span>
              </div>
              <div className="space-y-1.5">
                <div>
                  <div className={`flex justify-between text-[10px] mb-0.5 ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                    <span>🎥 Video Timeline</span>
                    <span className={`font-mono font-semibold ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`}>{attentionWeights.video}%</span>
                  </div>
                  <div className={`w-full h-1.5 rounded-full overflow-hidden ${isDarkMode ? 'bg-slate-800' : 'bg-slate-200'}`}>
                    <div className="h-full bg-indigo-500 transition-all duration-500" style={{ width: `${attentionWeights.video}%` }} />
                  </div>
                </div>
                <div>
                  <div className={`flex justify-between text-[10px] mb-0.5 ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                    <span>📄 PDF Document</span>
                    <span className={`font-mono font-semibold ${isDarkMode ? 'text-indigo-400' : 'text-purple-600'}`}>{attentionWeights.pdf}%</span>
                  </div>
                  <div className={`w-full h-1.5 rounded-full overflow-hidden ${isDarkMode ? 'bg-slate-800' : 'bg-slate-200'}`}>
                    <div className="h-full bg-purple-500 transition-all duration-500" style={{ width: `${attentionWeights.pdf}%` }} />
                  </div>
                </div>
                <div>
                  <div className={`flex justify-between text-[10px] mb-0.5 ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                    <span>🎙️ Acoustic Audio</span>
                    <span className={`font-mono font-semibold ${isDarkMode ? 'text-emerald-400' : 'text-emerald-600'}`}>{attentionWeights.audio}%</span>
                  </div>
                  <div className={`w-full h-1.5 rounded-full overflow-hidden ${isDarkMode ? 'bg-slate-800' : 'bg-slate-200'}`}>
                    <div className="h-full bg-emerald-500 transition-all duration-500" style={{ width: `${attentionWeights.audio}%` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Center Canvas: Interactive Video Studio & Timeline */}
        <main className={`flex-1 flex flex-col overflow-hidden transition-colors ${
          isDarkMode ? 'bg-[#070a13]' : 'bg-[#f8fafc]'
        }`}>
          {/* Top Mode Tabs */}
          <div className={`h-11 border-b px-6 flex items-center justify-between shrink-0 ${
            isDarkMode ? 'border-slate-800/80 bg-slate-900/60' : 'border-slate-200/80 bg-white/90 shadow-2xs'
          }`}>
            <div className="flex items-center gap-1.5 text-xs">
              <button
                onClick={() => setActiveTab('video-sync')}
                className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'video-sync'
                    ? isDarkMode
                      ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm'
                      : 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold shadow-2xs'
                    : isDarkMode
                      ? 'text-slate-400 hover:text-white'
                      : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Film className="w-3.5 h-3.5" />
                <span>Video Studio & Timeline</span>
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-3 py-1.5 rounded-lg font-medium transition cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'chat'
                    ? isDarkMode
                      ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                      : 'bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold shadow-2xs'
                    : isDarkMode
                      ? 'text-slate-400 hover:text-white'
                      : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Bot className="w-3.5 h-3.5" />
                <span>Conversational RAG</span>
              </button>
            </div>

            <div className={`text-[11px] flex items-center gap-2 ${
              isDarkMode ? 'text-slate-400' : 'text-slate-500'
            }`}>
              <Clock className={`w-3.5 h-3.5 ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`} />
              <span>Current Time: <strong className={`font-mono ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>{Math.floor(videoCurrentTime)}s</strong></span>
              {isVideoPlaying && (
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wider ${
                  isDarkMode ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'bg-indigo-100 text-indigo-700 border border-indigo-200'
                }`}>
                  Live Scrub
                </span>
              )}
            </div>
          </div>

          {/* Main Dual-View Body */}
          <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
            {/* Left Portion of Center: Video Player & Keyframe Track */}
            <div className={`flex-1 flex-col border-b lg:border-b-0 lg:border-r overflow-y-auto p-5 space-y-4 ${
              activeTab === 'chat' ? 'hidden lg:flex' : 'flex'
            } ${
              isDarkMode ? 'border-slate-800/80' : 'border-slate-200/80'
            }`}>
              {/* Synchronized Video Screen */}
              <div className={`relative rounded-2xl overflow-hidden border aspect-video flex items-center justify-center group ${
                isDarkMode ? 'border-slate-800 bg-black shadow-2xl' : 'border-slate-300 bg-slate-950 shadow-lg'
              }`}>
                {videoPreviewUrl ? (
                  <video
                    ref={videoPlayerRef}
                    src={videoPreviewUrl}
                    controls
                    onTimeUpdate={(e) => setVideoCurrentTime((e.target as HTMLVideoElement).currentTime)}
                    onPlay={() => setIsVideoPlaying(true)}
                    onPause={() => setIsVideoPlaying(false)}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-center p-6 space-y-3">
                    <div className={`w-16 h-16 rounded-2xl border mx-auto flex items-center justify-center ${
                      isDarkMode
                        ? 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'
                        : 'bg-indigo-500/20 border-indigo-400/30 text-indigo-300'
                    }`}>
                      <Film className="w-8 h-8 opacity-80" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-slate-200">No Video Ingested</h4>
                      <p className="text-xs text-slate-400 max-w-sm mt-1">
                        Upload an MP4 video or click "Load Demo Video & Data" in the top bar to inspect synchronized keyframe scrubbing.
                      </p>
                    </div>
                    <button
                      onClick={loadDemoSample}
                      className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition cursor-pointer shadow-md shadow-indigo-900/40"
                    >
                      Load Demo Video
                    </button>
                  </div>
                )}
              </div>

              {/* Synchronized Keyframe Timeline Track */}
              <div className={`p-4 rounded-2xl border space-y-3 ${
                isDarkMode ? 'border-slate-800 bg-slate-900/60' : 'border-slate-200/90 bg-white shadow-xs'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className={`w-4 h-4 ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`} />
                    <h3 className={`text-xs font-bold uppercase tracking-wider ${isDarkMode ? 'text-slate-200' : 'text-slate-800'}`}>
                      Synchronized Keyframe Timeline
                    </h3>
                  </div>
                  <span className={`text-[10px] ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>Click a bookmark to seek video</span>
                </div>

                {/* Keyframe Scene Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {activeScenes.map((sc, idx) => (
                    <button
                      key={idx}
                      onClick={() => seekVideo(sc.seconds)}
                      className={`p-2.5 rounded-xl border text-left transition group cursor-pointer flex items-start gap-2.5 ${
                        isDarkMode
                          ? 'border-slate-800 hover:border-cyan-500/50 bg-slate-950/60 hover:bg-cyan-950/20 text-slate-200'
                          : 'border-slate-200/90 hover:border-indigo-400 bg-slate-50/70 hover:bg-indigo-50/60 text-slate-800 shadow-2xs'
                      }`}
                    >
                      <div className={`p-1.5 rounded-lg shrink-0 group-hover:scale-105 transition border ${
                        isDarkMode
                          ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                          : 'bg-indigo-100 text-indigo-700 border-indigo-200'
                      }`}>
                        <Play className="w-3.5 h-3.5" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                          <span className={`font-mono text-[11px] font-bold ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`}>{sc.timestamp}</span>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded font-medium ${
                            isDarkMode ? 'bg-slate-800 text-slate-300' : 'bg-slate-200 text-slate-600'
                          }`}>{sc.tag}</span>
                        </div>
                        <h4 className={`text-xs font-medium truncate mt-0.5 ${
                          isDarkMode ? 'text-slate-200 group-hover:text-cyan-200' : 'text-slate-700 group-hover:text-indigo-700'
                        }`}>
                          {sc.title}
                        </h4>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Portion: Interactive Multimodal Reasoning Stream */}
            <div className={`flex-1 flex-col overflow-hidden transition-colors ${
              activeTab === 'video-sync' ? 'hidden lg:flex' : 'flex'
            } ${
              isDarkMode ? 'bg-[#080c18]' : 'bg-[#fcfdfd]'
            }`}>
              <div className={`p-3 px-5 border-b flex items-center justify-between ${
                isDarkMode ? 'border-slate-800/60 bg-slate-900/40' : 'border-slate-200/80 bg-white shadow-2xs'
              }`}>
                <div className="flex items-center gap-2">
                  <Bot className={`w-4 h-4 ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`} />
                  <span className={`text-xs font-bold uppercase tracking-wider ${isDarkMode ? 'text-slate-200' : 'text-slate-800'}`}>
                    Temporal Intelligence Stream
                  </span>
                </div>
                <span className={`text-[10px] ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>Grounded with Citations</span>
              </div>

              {/* Message List */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 max-w-2xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
                  >
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 border ${
                        msg.role === 'user'
                          ? isDarkMode
                            ? 'bg-cyan-500/20 border-cyan-500/30 text-cyan-300'
                            : 'bg-indigo-600 border-indigo-600 text-white shadow-2xs'
                          : isDarkMode
                            ? 'bg-slate-800 border-slate-700 text-purple-300 shadow-md'
                            : 'bg-white border-slate-200 text-indigo-600 shadow-2xs'
                      }`}
                    >
                      {msg.role === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                    </div>

                    <div className="space-y-1 max-w-[88%] text-xs leading-relaxed">
                      <div className={`flex items-center gap-2 text-[10px] px-1 ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                        <span className={`font-semibold ${isDarkMode ? 'text-slate-300' : 'text-slate-700'}`}>{msg.role === 'user' ? 'You' : 'Hyper-RAG'}</span>
                        <span>•</span>
                        <span>{msg.time}</span>
                      </div>

                      <div
                        className={`p-3.5 rounded-2xl border ${
                          msg.role === 'user'
                            ? isDarkMode
                              ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white border-cyan-400/30 shadow-lg shadow-cyan-900/20'
                              : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-transparent shadow-md shadow-indigo-500/20'
                            : isDarkMode
                              ? 'bg-slate-900/90 text-slate-200 border-slate-800/90 shadow-md'
                              : 'bg-white text-slate-800 border-slate-200/90 shadow-sm'
                        }`}
                      >
                        {msg.role === 'user' ? (
                          <div className="whitespace-pre-wrap">{msg.content}</div>
                        ) : (
                          <div className="markdown-content text-xs leading-relaxed space-y-2">
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              rehypePlugins={[rehypeRaw]}
                              components={{
                                table: ({ children }) => (
                                  <div className="overflow-x-auto my-2.5 rounded-xl border border-slate-700/60 shadow-sm">
                                    <table className="min-w-full text-left border-collapse text-xs">
                                      {children}
                                    </table>
                                  </div>
                                ),
                                thead: ({ children }) => (
                                  <thead className={isDarkMode ? 'bg-slate-800 text-cyan-300 border-b border-slate-700 font-semibold' : 'bg-slate-100 text-indigo-700 border-b border-slate-200 font-semibold'}>
                                    {children}
                                  </thead>
                                ),
                                tbody: ({ children }) => (
                                  <tbody className={isDarkMode ? 'divide-y divide-slate-800 bg-slate-900/60' : 'divide-y divide-slate-200 bg-white'}>
                                    {children}
                                  </tbody>
                                ),
                                tr: ({ children }) => (
                                  <tr className={isDarkMode ? 'hover:bg-slate-800/40 transition-colors' : 'hover:bg-slate-50 transition-colors'}>
                                    {children}
                                  </tr>
                                ),
                                th: ({ children }) => (
                                  <th className="px-3.5 py-2 text-[11px] font-semibold tracking-wider uppercase">
                                    {children}
                                  </th>
                                ),
                                td: ({ children }) => (
                                  <td className="px-3.5 py-2 text-xs">
                                    {children}
                                  </td>
                                ),
                                strong: ({ children }) => (
                                  <strong className={`font-semibold ${isDarkMode ? 'text-cyan-300' : 'text-indigo-600'}`}>
                                    {children}
                                  </strong>
                                ),
                                p: ({ children }) => (
                                  <p className="mb-2 last:mb-0 leading-relaxed">
                                    {children}
                                  </p>
                                ),
                                ul: ({ children }) => (
                                  <ul className="list-disc pl-5 my-2 space-y-1">
                                    {children}
                                  </ul>
                                ),
                                ol: ({ children }) => (
                                  <ol className="list-decimal pl-5 my-2 space-y-1">
                                    {children}
                                  </ol>
                                ),
                                li: ({ children }) => (
                                  <li className="leading-relaxed">{children}</li>
                                ),
                                code: ({ children }) => (
                                  <code className={`px-1.5 py-0.5 rounded font-mono text-[11px] ${
                                    isDarkMode ? 'bg-slate-800 text-amber-300 border border-slate-700' : 'bg-slate-100 text-purple-700 border border-slate-200'
                                  }`}>
                                    {children}
                                  </code>
                                )
                              }}
                            >
                              {msg.content}
                            </ReactMarkdown>
                          </div>
                        )}

                        {/* Interactive Click-to-Jump Timestamps */}
                        {msg.timestamps && msg.timestamps.length > 0 && (
                          <div className={`mt-3 pt-2 border-t flex flex-wrap items-center gap-1.5 ${
                            isDarkMode ? 'border-slate-800/80' : 'border-slate-100'
                          }`}>
                            <span className={`text-[10px] font-medium ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>Jump to video scene:</span>
                            {msg.timestamps.map((t, idx) => (
                              <button
                                key={idx}
                                onClick={() => seekVideo(t.seconds)}
                                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-mono transition cursor-pointer border ${
                                  isDarkMode
                                    ? 'bg-cyan-500/15 text-cyan-300 hover:bg-cyan-500/30 border-cyan-500/30'
                                    : 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border-indigo-200 font-semibold'
                                }`}
                                title={`Jump to ${t.time}`}
                              >
                                <Play className={`w-2.5 h-2.5 ${isDarkMode ? 'text-cyan-400' : 'text-indigo-600'}`} />
                                <span>{t.time}</span>
                                {t.label && <span className={`${isDarkMode ? 'text-slate-400' : 'text-slate-600'} font-sans`}>({t.label})</span>}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                {isChatting && (
                  <div className={`flex gap-2.5 max-w-md items-center text-xs p-2.5 rounded-xl border ${
                    isDarkMode
                      ? 'text-slate-400 bg-slate-900/80 border-slate-800'
                      : 'text-indigo-700 bg-indigo-50/80 border-indigo-100'
                  }`}>
                    <Sparkles className="w-4 h-4 text-indigo-500 animate-spin" />
                    <span>Searching temporal video frames & multi-modal vector space...</span>
                  </div>
                )}
                <div ref={chatBottomRef} />
              </div>

              {/* Prompt Suggestion Chips */}
              <div className={`px-4 py-2 border-t flex items-center gap-2 overflow-x-auto text-xs ${
                isDarkMode ? 'border-slate-800/60 bg-slate-900/40' : 'border-slate-200/80 bg-white/80'
              }`}>
                <span className={`text-[10px] whitespace-nowrap ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>Suggested:</span>
                {[
                  'Explain key architecture from video at 00:45',
                  'Cross-reference video benchmarks with PDF data',
                  'Find timestamps with technical charts',
                ].map((chip, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(chip)}
                    className={`text-[11px] px-2.5 py-1 rounded-lg border whitespace-nowrap transition cursor-pointer flex items-center gap-1 ${
                      isDarkMode
                        ? 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700/60'
                        : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200 shadow-2xs hover:border-slate-300'
                    }`}
                  >
                    <span>{chip}</span>
                    <ChevronRight className="w-3 h-3 text-slate-400" />
                  </button>
                ))}
              </div>

              {/* Query Input Box */}
              <div className={`p-3.5 border-t ${
                isDarkMode ? 'border-slate-800/80 bg-slate-950/80' : 'border-slate-200 bg-white'
              }`}>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className={`flex items-center gap-2 border rounded-xl p-1.5 transition ${
                    isDarkMode
                      ? 'bg-slate-900/90 border-slate-800 focus-within:border-cyan-500/70'
                      : 'bg-slate-50 border-slate-200/90 focus-within:border-indigo-500 focus-within:bg-white shadow-2xs'
                  }`}
                >
                  <input
                    type="text"
                    value={inputQuery}
                    onChange={(e) => setInputQuery(e.target.value)}
                    placeholder="Ask about timestamps, video scenes, PDF metrics, or voice transcript..."
                    className={`flex-1 bg-transparent px-3 py-1 text-xs focus:outline-none ${
                      isDarkMode
                        ? 'text-slate-100 placeholder-slate-500'
                        : 'text-slate-800 placeholder-slate-400'
                    }`}
                  />
                  <button
                    type="submit"
                    disabled={!inputQuery.trim() || isChatting}
                    className={`p-2 rounded-lg font-bold shadow-sm transition cursor-pointer disabled:opacity-40 ${
                      isDarkMode
                        ? 'bg-gradient-to-r from-cyan-500 to-indigo-500 text-black hover:opacity-90'
                        : 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 shadow-indigo-500/20'
                    }`}
                  >
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </form>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
