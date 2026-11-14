import {it,expect,vi,afterEach} from 'vitest';
import React from 'react';
import {renderHook,render,screen,act,cleanup,waitFor} from '@testing-library/react';
import ChatMessage from './components/ChatMessage';
import {ReadableStream} from 'node:stream/web';
import {useExecutiveStream} from './hooks/useExecutiveStream';

afterEach(()=>{cleanup();vi.unstubAllGlobals();});

it('renders each completed SSE block progressively and preserves previous messages',async()=>{
 let wire,sequence=0;
 const body=new ReadableStream({start(controller){wire=controller;}});
 const fetch=vi.fn().mockResolvedValue({ok:true,body,headers:{get:()=> 'text/event-stream'}});
 vi.stubGlobal('fetch',fetch);
 const {result}=renderHook(()=>useExecutiveStream());
 let request;
 act(()=>{request=result.current.send('How is our company performing over the last six months?');});
 const emit=(event,p)=>{
  const bytes=new TextEncoder().encode(`event: ${event}\ndata: ${JSON.stringify({sequence:++sequence,message_id:'m',request_id:'r',...p})}\n\n`);
  // Fragment every frame to exercise the real network parser, not a hook stub.
  wire.enqueue(bytes.slice(0,9));wire.enqueue(bytes.slice(9));
 };
 const blocks=[['text','Summary'],['chart','line'],['text','Analysis'],['chart','bar'],['text','Recommendation: Review delivery.']];
 emit('status',{message:'Validating',stream_mode:'validated_blocks'});
 for(let i=0;i<blocks.length;i++){
  const [type,value]=blocks[i],id=`b${i}`;
  emit('block_start',{block_id:id,block_type:type,position:i});
  if(type==='text')emit('text_delta',{block_id:id,delta:value});
  else emit('chart',{block_id:id,spec:{chart_type:value,dataset_id:'revenue',x:'month',y:['actual_revenue']},dataset:{id:'revenue',columns:['month','actual_revenue'],rows:[{month:'2026-10',actual_revenue:14000000}]}});
  emit('block_end',{block_id:id,sources:[{id:'source',filename:'Verified analytics'}]});
  await waitFor(()=>expect(result.current.messages[1].blocks).toHaveLength(i+1));
  expect(result.current.messages[1].blocks[0].content).toBe('Summary');
  expect(result.current.loading).toBe(true);
  expect(result.current.messages[1].done).toBe(false);
  const view=render(<ChatMessage message={result.current.messages[1]}/>);
  expect(screen.getByText('Summary')).toBeTruthy();
  expect(view.container.querySelectorAll('figure')).toHaveLength(i>=3?2:i>=1?1:0);
  view.unmount();
 }
 emit('done',{outcome:'completed',sources:[],stream_mode:'validated_blocks'});
 wire.close();
 await act(async()=>{await request;});
 expect(result.current.messages[1].sources).toHaveLength(1);
 expect(result.current.messages[1].done).toBe(true);
 expect(result.current.loading).toBe(false);
 expect(JSON.parse(fetch.mock.calls[0][1].body).history).toEqual([]);
});
