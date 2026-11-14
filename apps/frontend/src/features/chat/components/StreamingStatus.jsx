export default function StreamingStatus({message}){
 const modes={mock:'Mock response',validated_blocks:'Validated blocks · content is checked before display',incremental:'Live model text stream'};
 return <div className="mt-3 text-xs text-teal-700" role="status">{message.status}{message.streamMode&&<p>{modes[message.streamMode]||message.streamMode}</p>}{message.error&&<p role="alert" className="mt-2 text-red-700">{message.error}</p>}</div>;
}
