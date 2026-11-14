import {useEffect,useRef,useState} from 'react';
import {streamChat} from '../services/chatApi';
import {initialStream,applyEvent} from './streamState';
export function useExecutiveStream(){
 const [messages,setMessages]=useState([]),[loading,setLoading]=useState(false),controller=useRef(null),mounted=useRef(true);
 useEffect(()=>{mounted.current=true;return ()=>{mounted.current=false;controller.current?.abort();};},[]);
 async function send(question){
  if(controller.current)return;
  const ctrl=new AbortController();controller.current=ctrl;setLoading(true);
  const id=crypto.randomUUID();let state=initialStream();
  const history=messages.filter(m=>m.role==='user'||(m.done&&!m.error)).map(m=>({role:m.role,content:(m.role==='user'?m.content:m.blocks.filter(b=>b.type==='text').map(b=>b.content).join('\n')).slice(0,10000)})).filter(m=>m.content).slice(-20);
  setMessages(old=>[...old,{id:id+'user',role:'user',content:question},{id,role:'assistant',...state}]);
  const update=()=>{const snapshot=state;if(mounted.current)setMessages(old=>old.map(m=>m.id===id?{...m,...snapshot}:m));};
  try{await streamChat(question,history,ctrl.signal,(event,p)=>{state=applyEvent(state,event,p);update();});if(!state.done)throw Error('Response interrupted before completion');}
  catch(error){state={...state,status:ctrl.signal.aborted?'Cancelled':'Failed',error:ctrl.signal.aborted?'Response cancelled.':error.message};update();}
  finally{controller.current=null;if(mounted.current)setLoading(false);}
 }
 return {messages,loading,send,cancel:()=>controller.current?.abort()};
}

