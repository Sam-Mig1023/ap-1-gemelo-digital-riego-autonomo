import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  MessageSquare,
  Bot,
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Settings,
  X,
  Sparkles,
  Key,
  Check,
  AlertCircle,
  Minimize2,
  Maximize2,
  Trash2,
  Eye,
  EyeOff,
  HelpCircle,
  Cpu,
  Layers,
  Activity
} from 'lucide-react';
import {
  AgriculturalField,
  ManagementZone,
  RLDecision,
  SensorTelemetry,
  WeatherRadarCell
} from '../types';
import {
  ChatMessage,
  AVAILABLE_GROQ_MODELS,
  DEFAULT_MODEL,
  getStoredGroqApiKey,
  setStoredGroqApiKey,
  getStoredGroqModel,
  setStoredGroqModel,
  buildAgronomicSystemPrompt,
  queryGroqChat
} from '../services/groqService';

interface AgronomicChatbotProps {
  field: AgriculturalField;
  zones: ManagementZone[];
  decisions: RLDecision[];
  sensors: SensorTelemetry[];
  radarCells: WeatherRadarCell[];
}

const INITIAL_GREETING: ChatMessage = {
  id: 'msg-welcome-01',
  role: 'assistant',
  content: '¡Hola! Soy tu **Asistente Agronómico de IA** conectado al Gemelo Digital VRI. Puedo responder tus dudas sobre el balance hídrico, recomendaciones PPO del agente RL, índices de estrés CWSI o lecturas del radar en tiempo real. Puedes escribirme o pulsar el **micrófono** para dictarme por voz.',
  timestamp: new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
};

const SUGGESTED_QUESTIONS = [
  '¿Por qué se recomiendan 11.5 mm en Zona 4?',
  '¿Cuál es el estado de estrés CWSI del cultivo?',
  '¿Cómo influye la lluvia prevista del radar?',
  '¿Cómo funciona la recalibración de ciclo cerrado?'
];

export const AgronomicChatbot: React.FC<AgronomicChatbotProps> = ({
  field,
  zones,
  decisions,
  sensors,
  radarCells
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isMinimized, setIsMinimized] = useState<boolean>(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  // Groq API Key & Model
  const [apiKey, setApiKey] = useState<string>('');
  const [apiKeyInput, setApiKeyInput] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>(DEFAULT_MODEL);
  const [showApiKey, setShowApiKey] = useState<boolean>(false);
  const [keySaveSuccess, setKeySaveSuccess] = useState<boolean>(false);

  // Chat conversation
  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_GREETING]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // Voice features (STT & TTS)
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [speakingMsgId, setSpeakingMsgId] = useState<string | null>(null);
  const [autoSpeak, setAutoSpeak] = useState<boolean>(false);

  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize stored API Key & Model on mount
  useEffect(() => {
    const storedKey = getStoredGroqApiKey();
    const storedModel = getStoredGroqModel();
    if (storedKey) {
      setApiKey(storedKey);
      setApiKeyInput(storedKey);
    }
    if (storedModel) {
      setSelectedModel(storedModel);
    }
  }, []);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (isOpen && !isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen, isMinimized]);

  // Setup Speech Recognition (STT)
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'es-PE';

      recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        if (transcript) {
          setInputMessage(transcript);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Error en reconocimiento de voz:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  // Toggle Voice Dictation (Microphone)
  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Tu navegador no soporta la API de reconocimiento de voz. Intenta con Google Chrome o Microsoft Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error('Error al iniciar reconocimiento:', err);
        setIsListening(false);
      }
    }
  };

  // Speech Synthesis (TTS: Read out loud)
  const speakMessage = (id: string, text: string) => {
    if (!('speechSynthesis' in window)) {
      alert('Tu navegador no soporta síntesis de voz (Text-to-Speech).');
      return;
    }

    // If currently speaking this message, stop
    if (isSpeaking && speakingMsgId === id) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setSpeakingMsgId(null);
      return;
    }

    // Cancel any previous speech
    window.speechSynthesis.cancel();

    // Clean markdown characters for pleasant speech
    const cleanText = text
      .replace(/[*#_`~]/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/[•-]/g, '')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'es-PE';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    // Try to pick a natural Spanish voice
    const voices = window.speechSynthesis.getVoices();
    const esVoice = voices.find(v => v.lang.includes('es-PE') || v.lang.includes('es-ES') || v.lang.startsWith('es'));
    if (esVoice) {
      utterance.voice = esVoice;
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
      setSpeakingMsgId(id);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setSpeakingMsgId(null);
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      setSpeakingMsgId(null);
    };

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setSpeakingMsgId(null);
    }
  };

  // Save Settings
  const handleSaveSettings = () => {
    const trimmed = apiKeyInput.trim();
    setStoredGroqApiKey(trimmed);
    setApiKey(trimmed);
    setStoredGroqModel(selectedModel);
    setKeySaveSuccess(true);
    setErrorBanner(null);
    setTimeout(() => {
      setKeySaveSuccess(false);
      setIsSettingsOpen(false);
    }, 1200);
  };

  // Send Message
  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputMessage).trim();
    if (!query || isLoading) return;

    // Check for API key
    if (!apiKey) {
      setIsSettingsOpen(true);
      setErrorBanner('Por favor configura tu API Key de Groq para habilitar el asistente.');
      return;
    }

    // Add user message
    const userMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
    };

    const newHistory = [...messages, userMsg];
    setMessages(newHistory);
    setInputMessage('');
    setIsLoading(true);
    setErrorBanner(null);

    // Stop microphone if still listening
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }

    try {
      const systemPrompt = buildAgronomicSystemPrompt(field, zones, decisions, sensors, radarCells);
      const groqMessages = newHistory.map(m => ({
        role: m.role,
        content: m.content
      }));

      const botReplyText = await queryGroqChat(groqMessages, systemPrompt, apiKey, selectedModel);

      const botMsgId = `bot-${Date.now()}`;
      const botMsg: ChatMessage = {
        id: botMsgId,
        role: 'assistant',
        content: botReplyText,
        timestamp: new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, botMsg]);

      // If autoSpeak is enabled, read response out loud
      if (autoSpeak) {
        speakMessage(botMsgId, botReplyText);
      }
    } catch (err: any) {
      console.error(err);
      if (err?.message === 'API_KEY_MISSING') {
        setIsSettingsOpen(true);
        setErrorBanner('Se requiere una clave API de Groq válida.');
      } else {
        setErrorBanner(err?.message || 'Error al conectar con el servicio de Groq.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = () => {
    stopSpeaking();
    setMessages([INITIAL_GREETING]);
  };

  return (
    <>
      {/* Botón Flotante de Activación (FAB) */}
      {!isOpen && (
        <button
          onClick={() => {
            setIsOpen(true);
            setIsMinimized(false);
          }}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-500 text-white font-semibold text-xs shadow-2xl hover:scale-105 active:scale-95 transition-all duration-200 border border-emerald-300/40 shadow-emerald-950/40"
          aria-label="Abrir Asistente Agronómico con IA"
          title="Abrir Chatbot Agronómico VRI (Groq)"
        >
          <div className="relative">
            <Bot className="w-5 h-5 text-white" />
            <span className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full border-2 border-slate-900 ${apiKey ? 'bg-emerald-300 animate-pulse' : 'bg-amber-400'}`} />
          </div>
          <span className="tracking-wide">Asistente IA VRI</span>
          <Sparkles className="w-3.5 h-3.5 text-emerald-200" />
        </button>
      )}

      {/* Ventana del Chatbot */}
      {isOpen && (
        <div
          className={`fixed z-50 transition-all duration-300 ${
            isMinimized
              ? 'bottom-6 right-6 w-72 h-14'
              : 'bottom-4 right-4 sm:bottom-6 sm:right-6 w-[calc(100vw-2rem)] sm:w-[420px] md:w-[460px] h-[580px] max-h-[85vh]'
          } bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden backdrop-blur-xl`}
        >
          {/* Header del Chatbot */}
          <div className="bg-gradient-to-r from-slate-900 via-slate-950 to-slate-900 text-white p-3.5 border-b border-slate-800 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white shrink-0 border border-emerald-400/40 shadow-md">
                <Bot className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <h3 className="text-xs font-bold tracking-tight text-white truncate">
                    Asistente Agronómico VRI
                  </h3>
                  <span className="text-[9px] font-semibold uppercase px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Groq
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 truncate">
                  {apiKey ? 'Conectado a LLaMA 3.3' : 'Requiere API Key de Groq'}
                </p>
              </div>
            </div>

            {/* Acciones de la barra superior */}
            <div className="flex items-center gap-1 text-slate-400">
              {/* Toggle de lectura automática en voz alta */}
              <button
                onClick={() => {
                  if (isSpeaking) stopSpeaking();
                  setAutoSpeak(!autoSpeak);
                }}
                className={`p-1.5 rounded-lg transition-colors ${
                  autoSpeak
                    ? 'text-emerald-400 bg-emerald-950/60 border border-emerald-500/30'
                    : 'hover:text-white hover:bg-slate-800'
                }`}
                title={autoSpeak ? 'Lectura en voz alta: Activada' : 'Lectura en voz alta: Desactivada'}
              >
                {autoSpeak ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
              </button>

              {/* Botón de Ajustes (Clave Groq) */}
              <button
                onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                className={`p-1.5 rounded-lg transition-colors ${
                  isSettingsOpen || !apiKey
                    ? 'text-amber-400 bg-amber-950/40 border border-amber-500/30'
                    : 'hover:text-white hover:bg-slate-800'
                }`}
                title="Configurar API Key de Groq y Modelo"
              >
                <Settings className="w-3.5 h-3.5" />
              </button>

              {/* Minimizar / Maximizar */}
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1.5 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
                title={isMinimized ? 'Expandir' : 'Minimizar'}
              >
                {isMinimized ? <Maximize2 className="w-3.5 h-3.5" /> : <Minimize2 className="w-3.5 h-3.5" />}
              </button>

              {/* Cerrar */}
              <button
                onClick={() => {
                  stopSpeaking();
                  setIsOpen(false);
                }}
                className="p-1.5 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
                title="Cerrar Asistente"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Si está minimizado, solo mostramos la barra superior */}
          {!isMinimized && (
            <>
              {/* Modal o Panel de Configuración de API Key de Groq */}
              {isSettingsOpen && (
                <div className="bg-slate-100 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 p-4 text-xs space-y-3 shrink-0 animate-fadeIn">
                  <div className="flex items-center justify-between">
                    <span className="font-bold flex items-center gap-1.5 text-slate-900 dark:text-white">
                      <Key className="w-3.5 h-3.5 text-amber-400" />
                      Configuración de Groq API Key
                    </span>
                    <button
                      onClick={() => setIsSettingsOpen(false)}
                      className="text-slate-500 hover:text-slate-800 dark:hover:text-white text-xs"
                    >
                      ✕
                    </button>
                  </div>

                  <div className="space-y-1.5">
                    <label className="block text-slate-600 dark:text-slate-400 text-[11px] font-medium">
                      API Key de Groq (<a href="https://console.groq.com/keys" target="_blank" rel="noreferrer" className="text-emerald-500 hover:underline">obtener gratis en console.groq.com</a>):
                    </label>
                    <div className="relative flex items-center">
                      <input
                        type={showApiKey ? 'text' : 'password'}
                        placeholder="gsk_..."
                        value={apiKeyInput}
                        onChange={(e) => setApiKeyInput(e.target.value)}
                        className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg pl-3 pr-9 py-1.5 text-xs text-slate-900 dark:text-white font-mono focus:outline-none focus:border-emerald-500"
                      />
                      <button
                        type="button"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="absolute right-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                      >
                        {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  {/* Selector de Modelo */}
                  <div className="space-y-1">
                    <label className="block text-slate-600 dark:text-slate-400 text-[11px] font-medium">
                      Modelo LLM en Groq:
                    </label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-emerald-500 cursor-pointer"
                    >
                      {AVAILABLE_GROQ_MODELS.map(m => (
                        <option key={m.id} value={m.id}>
                          {m.name} ({m.speed})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[10px] text-slate-500 dark:text-slate-400">
                      Se almacena de forma segura en tu navegador (`localStorage`).
                    </span>
                    <button
                      onClick={handleSaveSettings}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold text-xs flex items-center gap-1 shadow-md transition-all"
                    >
                      {keySaveSuccess ? <Check className="w-3 h-3" /> : null}
                      <span>{keySaveSuccess ? '¡Guardada!' : 'Guardar Clave'}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Banner de alerta si no hay API Key */}
              {!apiKey && !isSettingsOpen && (
                <div className="bg-amber-500/10 border-b border-amber-500/30 p-2.5 px-3.5 flex items-center justify-between text-xs text-amber-600 dark:text-amber-300">
                  <span className="flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                    Coloca tu API Key de Groq para chatear en tiempo real.
                  </span>
                  <button
                    onClick={() => setIsSettingsOpen(true)}
                    className="font-semibold underline hover:text-amber-500 text-[11px]"
                  >
                    Ingresar Clave
                  </button>
                </div>
              )}

              {/* Banner de error si ocurre en la llamada */}
              {errorBanner && (
                <div className="bg-rose-500/10 border-b border-rose-500/30 p-2 px-3 flex items-center justify-between text-xs text-rose-600 dark:text-rose-300">
                  <span className="flex items-center gap-1.5 truncate">
                    <AlertCircle className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                    <span className="truncate">{errorBanner}</span>
                  </span>
                  <button onClick={() => setErrorBanner(null)} className="text-slate-400 hover:text-slate-600 text-xs">✕</button>
                </div>
              )}

              {/* Indicador de Lectura de Audio Global */}
              {isSpeaking && (
                <div className="bg-emerald-500/10 border-b border-emerald-500/30 px-3 py-1.5 flex items-center justify-between text-xs text-emerald-600 dark:text-emerald-300 animate-pulse">
                  <span className="flex items-center gap-1.5 text-[11px] font-medium">
                    <Volume2 className="w-3.5 h-3.5 text-emerald-500" />
                    Leyendo respuesta en voz alta...
                  </span>
                  <button
                    onClick={stopSpeaking}
                    className="text-[10px] font-bold uppercase tracking-wider text-rose-500 hover:underline"
                  >
                    Detener Audio
                  </button>
                </div>
              )}

              {/* Lista de Mensajes */}
              <div className="flex-1 overflow-y-auto p-3.5 sm:p-4 space-y-3.5 text-xs scrollbar-none">
                {messages.map((msg) => {
                  const isBot = msg.role === 'assistant';
                  const isCurrentSpeaking = isSpeaking && speakingMsgId === msg.id;

                  return (
                    <div
                      key={msg.id}
                      className={`flex flex-col ${isBot ? 'items-start' : 'items-end'} space-y-1`}
                    >
                      <div className="flex items-center gap-1 text-[10px] text-slate-600 dark:text-slate-400 px-1">
                        <span>{isBot ? 'Asistente VRI' : 'Tú'}</span>
                        <span>•</span>
                        <span>{msg.timestamp}</span>
                      </div>

                      <div className="flex items-start gap-1.5 max-w-[88%] group">
                        {isBot && (
                          <div className="w-6 h-6 rounded-lg bg-emerald-500/20 text-emerald-500 flex items-center justify-center shrink-0 mt-0.5 border border-emerald-500/30">
                            <Bot className="w-3.5 h-3.5" />
                          </div>
                        )}

                        <div
                          className={`p-3 rounded-2xl leading-relaxed ${
                            isBot
                              ? 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700/70 rounded-tl-none shadow-sm'
                              : 'bg-emerald-600 text-white rounded-tr-none shadow-md shadow-emerald-950/20'
                          }`}
                        >
                          {isBot ? (
                            <div className="text-xs leading-relaxed space-y-1.5">
                              <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                  p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                                  strong: ({ children }) => <strong className="font-bold text-slate-900 dark:text-white">{children}</strong>,
                                  em: ({ children }) => <em className="italic text-slate-800 dark:text-slate-200">{children}</em>,
                                  ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
                                  ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
                                  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                                  h1: ({ children }) => <h1 className="text-sm font-bold text-slate-900 dark:text-white mt-2.5 mb-1.5 pb-1 border-b border-slate-200 dark:border-slate-700">{children}</h1>,
                                  h2: ({ children }) => <h2 className="text-xs font-bold text-slate-900 dark:text-white mt-2 mb-1">{children}</h2>,
                                  h3: ({ children }) => <h3 className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 mt-2 mb-1">{children}</h3>,
                                  table: ({ children }) => (
                                    <div className="overflow-x-auto my-2 rounded-lg border border-slate-200 dark:border-slate-700">
                                      <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700 text-[11px]">{children}</table>
                                    </div>
                                  ),
                                  thead: ({ children }) => <thead className="bg-slate-200/60 dark:bg-slate-900/60">{children}</thead>,
                                  tbody: ({ children }) => <tbody className="divide-y divide-slate-200/50 dark:divide-slate-700/50">{children}</tbody>,
                                  tr: ({ children }) => <tr>{children}</tr>,
                                  th: ({ children }) => <th className="px-2.5 py-1.5 text-left font-semibold text-slate-800 dark:text-slate-200">{children}</th>,
                                  td: ({ children }) => <td className="px-2.5 py-1.5 text-slate-700 dark:text-slate-300">{children}</td>,
                                  code: ({ inline, children, ...props }: any) => {
                                    if (inline) {
                                      return (
                                        <code className="bg-slate-200/70 dark:bg-slate-900 px-1 py-0.5 rounded text-[11px] font-mono text-emerald-600 dark:text-emerald-400" {...props}>
                                          {children}
                                        </code>
                                      );
                                    }
                                    return (
                                      <pre className="bg-slate-900 text-slate-100 p-2.5 rounded-lg overflow-x-auto text-[11px] font-mono my-2 border border-slate-700">
                                        <code>{children}</code>
                                      </pre>
                                    );
                                  },
                                  hr: () => <hr className="my-2 border-slate-200 dark:border-slate-700" />,
                                  blockquote: ({ children }) => (
                                    <blockquote className="border-l-2 border-emerald-500 pl-2.5 italic text-slate-600 dark:text-slate-400 my-1.5">
                                      {children}
                                    </blockquote>
                                  )
                                }}
                              >
                                {msg.content}
                              </ReactMarkdown>
                            </div>
                          ) : (
                            <div className="whitespace-pre-wrap">{msg.content}</div>
                          )}
                        </div>

                        {/* Botón para escuchar mensaje individual del bot */}
                        {isBot && (
                          <button
                            onClick={() => speakMessage(msg.id, msg.content)}
                            className={`p-1 rounded-lg border transition-all shrink-0 mt-1 opacity-80 group-hover:opacity-100 ${
                              isCurrentSpeaking
                                ? 'bg-emerald-500 text-white border-emerald-400 animate-pulse'
                                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700 hover:text-emerald-500'
                            }`}
                            title={isCurrentSpeaking ? 'Pausar audio' : 'Escuchar respuesta en voz alta'}
                          >
                            {isCurrentSpeaking ? (
                              <VolumeX className="w-3.5 h-3.5" />
                            ) : (
                              <Volume2 className="w-3.5 h-3.5" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}

                {/* Indicador de carga de Groq */}
                {isLoading && (
                  <div className="flex items-center gap-2 text-xs text-emerald-500 dark:text-emerald-400 p-2">
                    <Bot className="w-4 h-4 animate-spin" />
                    <span>Analizando gemelo digital y razonando con Groq...</span>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Preguntas Frecuentes / Chips Sugeridos */}
              {messages.length <= 2 && (
                <div className="px-3 pb-2 flex flex-wrap gap-1.5 shrink-0">
                  {SUGGESTED_QUESTIONS.map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(q)}
                      disabled={isLoading}
                      className="px-2.5 py-1 text-[11px] rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-emerald-500/10 dark:hover:bg-emerald-500/20 text-slate-700 dark:text-slate-300 hover:text-emerald-600 dark:hover:text-emerald-400 border border-slate-300 dark:border-slate-700 transition-all text-left"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}

              {/* Barra de Entrada (Texto y Micrófono) */}
              <div className="p-3 bg-slate-50 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 space-y-1.5 shrink-0">
                {isListening && (
                  <div className="flex items-center justify-between px-2 py-1 bg-rose-500/10 rounded-lg text-rose-500 text-[11px] font-semibold animate-pulse border border-rose-500/20">
                    <span className="flex items-center gap-1.5">
                      <Mic className="w-3.5 h-3.5 text-rose-500" />
                      Escuchando tu voz en español... Di tu consulta.
                    </span>
                    <button
                      onClick={toggleListening}
                      className="text-xs text-rose-600 hover:underline font-bold"
                    >
                      Finalizar
                    </button>
                  </div>
                )}

                <div className="flex items-center gap-2">
                  {/* Botón de Micrófono para Dictar (STT) */}
                  <button
                    type="button"
                    onClick={toggleListening}
                    className={`p-2 rounded-xl border transition-all shrink-0 ${
                      isListening
                        ? 'bg-rose-600 text-white border-rose-500 shadow-lg shadow-rose-950/40 animate-bounce'
                        : 'bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700 hover:text-emerald-500 hover:border-emerald-500/50'
                    }`}
                    title={isListening ? 'Detener dictado' : 'Dictar por voz (Micrófono)'}
                  >
                    {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </button>

                  {/* Cuadro de Texto */}
                  <input
                    type="text"
                    placeholder="Escribe o pulsa el micrófono para dictar..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    disabled={isLoading}
                    className="flex-1 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-all"
                  />

                  {/* Botón Enviar */}
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={!inputMessage.trim() || isLoading}
                    className={`p-2 rounded-xl text-white font-medium transition-all shrink-0 ${
                      inputMessage.trim() && !isLoading
                        ? 'bg-emerald-600 hover:bg-emerald-500 shadow-md shadow-emerald-950/30 cursor-pointer'
                        : 'bg-slate-300 dark:bg-slate-800 text-slate-500 dark:text-slate-600 cursor-not-allowed'
                    }`}
                    title="Enviar mensaje"
                  >
                    <Send className="w-4 h-4" />
                  </button>

                  {/* Limpiar Historial */}
                  <button
                    onClick={handleClearHistory}
                    className="p-2 rounded-xl bg-white dark:bg-slate-900 text-slate-400 hover:text-rose-400 border border-slate-300 dark:border-slate-700 transition-colors shrink-0"
                    title="Reiniciar conversación"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};
