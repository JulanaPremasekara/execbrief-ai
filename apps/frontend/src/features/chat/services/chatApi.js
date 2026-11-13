export async function consumeSSE(body, onEvent) {
  const reader=body.getReader(), decoder=new TextDecoder(); let buffer='';
  try {
    while(true){
      const {value,done}=await reader.read();
      buffer+=decoder.decode(value,{stream:!done});
      let match;
      while((match=/\r?\n\r?\n/.exec(buffer))){
        const frame=buffer.slice(0,match.index); buffer=buffer.slice(match.index+match[0].length);
        let event='message'; const data=[];
        for(const line of frame.split(/\r?\n/)){
          if(line.startsWith('event:'))event=line.slice(6).trim();
          if(line.startsWith('data:'))data.push(line.slice(5).replace(/^ /,''));
        }
        if(data.length)onEvent(event,JSON.parse(data.join('\n')));
      }
      if(done){if(buffer.trim())throw Error('Incomplete stream frame');break;}
    }
  } finally {await reader.cancel();reader.releaseLock();}
}
export async function streamChat(question,history,signal,onEvent){
  const response=await fetch('/api/chat/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question,history}),signal});
  if(!response.ok)throw Error('Request failed ('+response.status+')');
  if(!response.body || !response.headers.get('content-type')?.includes('text/event-stream'))throw Error('Invalid stream response');
  await consumeSSE(response.body,onEvent);
}

