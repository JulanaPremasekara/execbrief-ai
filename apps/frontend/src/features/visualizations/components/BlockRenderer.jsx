import TextBlock from './TextBlock';import {chartRegistry} from '../registry/chartRegistry';
export default function BlockRenderer({block}){if(block.type==='text')return <TextBlock block={block}/>;if(!block.spec)return <p>Preparing chart…</p>;const Chart=chartRegistry[block.spec.chart_type];return Chart?<Chart block={block}/>:<p role="alert">Unsupported chart</p>}
