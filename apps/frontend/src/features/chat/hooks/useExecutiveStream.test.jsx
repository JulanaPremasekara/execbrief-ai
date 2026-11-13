import {it,expect,vi,afterEach} from 'vitest';
import {renderHook,act,cleanup,waitFor} from '@testing-library/react';
import {useExecutiveStream} from './useExecutiveStream';
import {streamChat} from '../services/chatApi';
vi.mock('../services/chatApi',()=>({streamChat:vi.fn()}));
afterEach(()=>{cleanup();vi.resetAllMocks();});

it('cancels a pending request and preserves its partial response',async()=>{
 streamChat.mockImplementation((q,h,signal,emit)=>new Promise((resolve,reject)=>{
  emit('block_start',{sequence:1,message_id:'m',request_id:'r',block_id:'b',block_type:'text',position:0});
  emit('text_delta',{sequence:2,message_id:'m',request_id:'r',block_id:'b',delta:'Partial'});
  signal.addEventListener('abort',()=>reject(new DOMException('Aborted','AbortError')));
 }));
 const {result}=renderHook(()=>useExecutiveStream());
 act(()=>{result.current.send('Question');});
 expect(result.current.loading).toBe(true);
 act(()=>result.current.cancel());
 await waitFor(()=>expect(result.current.loading).toBe(false));
 expect(result.current.messages[1].blocks[0].content).toBe('Partial');
 expect(result.current.messages[1].status).toBe('Cancelled');
});

it('reports early EOF and preserves earlier conversation messages',async()=>{
 streamChat.mockResolvedValue();
 const {result}=renderHook(()=>useExecutiveStream());
 await act(async()=>{await result.current.send('First');});
 expect(result.current.messages[1].error).toContain('interrupted');
 await act(async()=>{await result.current.send('Second');});
 expect(result.current.messages).toHaveLength(4);
 expect(result.current.messages[0].content).toBe('First');
});
