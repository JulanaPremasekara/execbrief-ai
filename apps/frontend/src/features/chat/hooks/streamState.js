export const initialStream=()=>({blocks:[],sources:[],sequence:0,done:false,status:'Preparing',error:null});
export function applyEvent(state,event,p){
  if(state.done || p.sequence!==state.sequence+1)throw Error('Invalid event order');
  if(state.messageId && (state.messageId!==p.message_id || state.requestId!==p.request_id))throw Error('Stream identity changed');
  const s={...state,blocks:state.blocks.map(b=>({...b})),sequence:p.sequence,messageId:p.message_id,requestId:p.request_id};
  const active=s.blocks.find(b=>!b.complete);
  if(event==='status')s.status=p.message;
  else if(event==='block_start'){
    if(active || p.position!==s.blocks.length || s.blocks.some(b=>b.id===p.block_id) || !['text','chart'].includes(p.block_type))throw Error('Invalid block order');
    s.blocks.push({id:p.block_id,type:p.block_type,content:'',complete:false});
  } else if(['text_delta','chart','block_end'].includes(event)){
    if(!active || active.id!==p.block_id)throw Error('Unknown active block');
    if(event==='text_delta'){if(active.type!=='text'||typeof p.delta!=='string')throw Error('Invalid text');active.content+=p.delta;}
    if(event==='chart'){
      if(active.type!=='chart'||active.spec||!['bar','line'].includes(p.spec?.chart_type)||p.spec.dataset_id!==p.dataset?.id||![p.spec.x,...p.spec.y].every(c=>p.dataset.columns.includes(c)))throw Error('Invalid chart');
      active.spec=p.spec;active.dataset=p.dataset;
    }
    if(event==='block_end'){if(active.type==='chart'&&!active.spec)throw Error('Missing chart');active.complete=true;}
  } else if(event==='error'){s.error=p.message;s.status='Failed';}
  else if(event==='done'){
    if(!['completed','error'].includes(p.outcome)||(p.outcome==='completed'&&active))throw Error('Incomplete response');
    s.done=true;s.sources=p.sources;s.status=p.outcome==='completed'?'Complete':'Failed';
  }else throw Error('Unknown stream event');
  return s;
}

