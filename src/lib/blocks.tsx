import { RichText } from '@payloadcms/richtext-lexical/react'
import type { SerializedEditorState } from '@payloadcms/richtext-lexical/lexical'
import { toMediaURL } from './content'
import React from 'react'
type Block = Record<string, any> & {blockType:string;id?:string}
export function Blocks({layout}:{layout:unknown}){
 if(!Array.isArray(layout))return null
 return <div className="cms-blocks">{(layout as Block[]).map((b,i)=>{
  const key=b.id||i
  if(b.blockType==='hero')return <section className="cms-hero" key={key}><div className="container split"><div><small className="kicker">{b.eyebrow}</small><h2>{b.title}</h2><p>{b.subtitle}</p>{b.buttonText&&<a className="btn btn-primary" href={b.buttonHref||'/zapros-rascheta/'}>{b.buttonText}</a>}</div>{toMediaURL(b.image)&&<img alt={b.title||''} src={toMediaURL(b.image)}/>}</div></section>
  if(b.blockType==='text')return <section className="section" key={key}><div className="container"><h2 className="section-title">{b.heading}</h2>{b.body&&<div className="prose"><RichText data={b.body as SerializedEditorState}/></div>}</div></section>
  if(b.blockType==='image')return <figure className="cms-figure" key={key}>{toMediaURL(b.image)&&<img src={toMediaURL(b.image)} alt={b.caption||''}/>}<figcaption>{b.caption}</figcaption></figure>
  if(b.blockType==='cta')return <section className="cta-band" key={key}><div className="container cta-wrap"><div><h2>{b.heading}</h2><p>{b.text}</p></div><a className="btn btn-primary" href={b.buttonHref||'/zapros-rascheta/'}>{b.buttonText||'Запросить расчёт'}</a></div></section>
  if(b.blockType==='faq')return <section className="section soft" key={key}><div className="container"><h2 className="section-title">{b.heading}</h2>{(b.items||[]).map((q:{id:string;question:string;answer:string},index:number)=><details key={q.id||index} className="faq"><summary>{q.question}</summary><p>{q.answer}</p></details>)}</div></section>
  if(b.blockType==='cards')return <section className="section" key={key}><div className="container"><h2 className="section-title">{b.heading}</h2><div className="listing">{(b.items||[]).map((card:{id:string;title:string;description:string;href:string;image:unknown},j:number)=><a key={card.id||j} href={card.href||'#'}>{toMediaURL(card.image)&&<img className="cms-card-image" src={toMediaURL(card.image)} alt={card.title||''}/>}<h3>{card.title}</h3><p>{card.description}</p></a>)}</div></div></section>
  return null
 })}</div>
}
