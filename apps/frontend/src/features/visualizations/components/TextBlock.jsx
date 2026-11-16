export default function TextBlock({block}) {
  const lines = block.content.split('\n');
  const headings = new Set(['Revenue Performance Overview', 'Key business insights', 'Recommended actions']);
  if (!headings.has(lines[0])) return <p className="whitespace-pre-wrap leading-7">{block.content}</p>;
  return <section className="space-y-3"><h3 className="font-semibold text-slate-900">{lines[0]}</h3>
    {lines.slice(1).map((line, index) => line.startsWith('• ')
      ? <p key={index} className="pl-3 leading-7">{line}</p>
      : <p key={index} className="leading-7">{line}</p>)}
  </section>;
}
