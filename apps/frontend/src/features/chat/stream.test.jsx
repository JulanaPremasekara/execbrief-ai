import React from 'react';
import {describe,it,expect,vi,afterEach} from 'vitest';
import {render,screen,cleanup} from '@testing-library/react';
import {ReadableStream} from 'node:stream/web';
import {consumeSSE} from './services/chatApi';
import {initialStream,applyEvent} from './hooks/streamState';
import BlockRenderer from '../visualizations/components/BlockRenderer';
import StreamingStatus from './components/StreamingStatus';
vi.mock('recharts',async()=>{
 const actual=await vi.importActual('recharts');
 return {...actual,ResponsiveContainer:({children})=><div>{React.cloneElement(children,{width:600,height:300})}</div>};
});
afterEach(cleanup);
const payload=(sequence,more={})=>({sequence,message_id:'m',request_id:'r',...more});
describe('stream transport and state',()=>{
 it('decodes byte-fragmented UTF-8, CRLF and multiple frames',async()=>{
  const bytes=new TextEncoder().encode('event: status\r\ndata: {"message":"café"}\r\n\r\nevent: done\ndata: {}\n\n');
  const body=new ReadableStream({start(c){for(const byte of bytes)c.enqueue(new Uint8Array([byte]));c.close();}});
  const seen=[];await consumeSSE(body,(e,p)=>seen.push([e,p]));
  expect(seen).toEqual([['status',{message:'café'}],['done',{}]]);
 });
 it('rejects incomplete frames',async()=>{
  const body=new ReadableStream({start(c){c.enqueue(new TextEncoder().encode('event: done'));c.close();}});
  await expect(consumeSSE(body,()=>{})).rejects.toThrow('Incomplete');
 });
 it('appends text and preserves sequential blocks',()=>{
  let s=initialStream();
  s=applyEvent(s,'block_start',payload(1,{block_id:'a',block_type:'text',position:0}));
  s=applyEvent(s,'text_delta',payload(2,{block_id:'a',delta:'Hello '}));
  s=applyEvent(s,'text_delta',payload(3,{block_id:'a',delta:'world'}));
  s=applyEvent(s,'block_end',payload(4,{block_id:'a'}));
  s=applyEvent(s,'block_start',payload(5,{block_id:'b',block_type:'text',position:1}));
  expect(s.blocks.map(b=>b.id)).toEqual(['a','b']);
  expect(s.blocks[0].content).toBe('Hello world');
  expect(()=>applyEvent(s,'done',payload(6,{outcome:'completed'}))).toThrow('Incomplete');
 });
 it('rejects wrong order and unknown blocks',()=>{
  expect(()=>applyEvent(initialStream(),'status',payload(2))).toThrow();
  expect(()=>applyEvent(initialStream(),'text_delta',payload(1,{block_id:'missing',delta:'x'}))).toThrow();
 });
 it('retains partial content after errors and renders the error',()=>{
  let s=applyEvent(initialStream(),'block_start',payload(1,{block_id:'a',block_type:'text',position:0}));
  s=applyEvent(s,'text_delta',payload(2,{block_id:'a',delta:'Partial'}));
  s=applyEvent(s,'error',payload(3,{message:'Unavailable'}));
  s=applyEvent(s,'done',payload(4,{outcome:'error',sources:[]}));
  expect(s.blocks[0].content).toBe('Partial');
  render(<StreamingStatus message={s}/>);
  expect(screen.getByRole('alert').textContent).toBe('Unavailable');
 });
});
it('renders text, line, text, bar and recommendations in order',()=>{
 const chart=(id,kind)=>({id,type:'chart',spec:{chart_type:kind,title:kind,x:'month',y:['actual','target']},dataset:{units:'LKR millions',rows:[{month:'May',actual:12,target:13}]}});
 const blocks=[{id:'a',type:'text',content:'Summary'},chart('b','line'),{id:'c',type:'text',content:'Analysis'},chart('d','bar'),{id:'e',type:'text',content:'Recommendations'}];
 const {container}=render(<div>{blocks.map(b=><BlockRenderer key={b.id} block={b}/>)}</div>);
 expect([...container.firstChild.children].map(e=>e.tagName)).toEqual(['P','FIGURE','P','FIGURE','P']);
 expect(container.querySelector('.recharts-line')).not.toBeNull();
 expect(container.querySelector('.recharts-bar')).not.toBeNull();
});
