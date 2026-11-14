import {useEffect,useState} from 'react';
import {useExecutiveStream} from '../hooks/useExecutiveStream';
import ChatMessage from './ChatMessage';
import MessageInput from './MessageInput';
export default function ChatWindow(){
 const chat=useExecutiveStream();
 const [mode,setMode]=useState('unknown');
 useEffect(()=>{const controller=new AbortController();fetch('/api/health',{signal:controller.signal}).then(r=>{if(!r.ok)throw Error();return r.json()}).then(data=>setMode(data.mode)).catch(()=>{});return ()=>controller.abort();},[]);
 return <main className="mx-auto max-w-4xl px-4 py-10">
  <header className="mb-10"><div className="mb-8 flex items-center justify-between border-b border-slate-200 pb-5"><span className="text-xl font-bold">ExecBrief <span className="text-teal-700">AI</span></span><span className="rounded-full bg-amber-100 px-3 py-1 text-xs text-amber-900">{mode==='live'?'Live pipeline configured':mode==='mock'?'Mock demonstration':'Checking connection'}</span></div>
  <p className="text-xs font-semibold uppercase tracking-widest text-teal-700">Nexora Solutions (Pvt) Ltd</p><h1 className="mt-3 text-4xl font-semibold tracking-tight">A clearer view of performance.</h1><p className="mt-3 text-slate-500">Executive insights with evidence and charts. May–October 2026.</p></header>
  <aside className="mb-6 rounded-lg bg-teal-50 p-4 text-sm text-teal-900">Fictional company data. {mode==='mock'?'Questions return a fixed sample briefing. Include “text only” to omit charts.':'Briefings use backend analytics and document evidence. Sources appear with each response.'}</aside>
  <section aria-label="Conversation" className="space-y-5">{chat.messages.map(m=><ChatMessage key={m.id} message={m}/>)}</section><MessageInput {...chat}/>
 </main>;
}
