import {readFile} from 'node:fs/promises'
import path from 'node:path'
import type {Metadata} from 'next'
import {cms} from '@/lib/content'
export const dynamic='force-dynamic'
function esc(value:unknown){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]||ch))}
async function homeSettings(){try{const payload=await cms();return await payload.findGlobal({slug:'site-settings',depth:2})}catch(err){console.error('home settings unavailable',err);return null}}
export async function generateMetadata():Promise<Metadata>{
 const s=await homeSettings() as Record<string,any>|null
 return {title:s?.metaTitle||'Практик Пласт — пластиковые изделия для бизнеса',description:s?.metaDescription||'Контрактное литьё и экструзия.',robots:{index:false,follow:false}}
}
export default async function Home(){
 const full=await readFile(path.join(process.cwd(),'src','legacy','home.html'),'utf8')
 const raw=full.slice(full.indexOf('<body>')+6,full.lastIndexOf('</body>'))
 const settings=await homeSettings() as Record<string,any>|null
 let html=raw.replace(/<script[^>]*src="assets\/main.js"[^>]*><\/script>/ig,'')
   .replace(/(src|href)="assets\//g,'$1="/assets/')
   .replace(/href="index.html"/g,'href="/"')
   .replace(/href="(uslugi|produkciya|proizvodstvo|stati|o-kompanii|kontakty|zapros-rascheta|politika-konfidencialnosti)\//g,'href="/$1/')
 if(settings){
  html=html.replace('Пластиковые изделия <em>для вашего бизнеса.</em> От чертежа до партии.',esc(settings.heroTitle||'Пластиковые изделия для вашего бизнеса. От чертежа до партии.'))
  html=html.replace('Контрактное литьё пластмасс, экструзия и серийная продукция. Обсудим ваш проект, технические требования и условия сотрудничества.',esc(settings.heroLead||'Контрактное литьё пластмасс, экструзия и серийная продукция.'))
  const headings=[
   ['servicesHeading','От задачи до <em>готового изделия</em>'],
   ['productsHeading','Продукция для <em>предприятий</em>'],
   ['stepsHeading','Четыре шага к <em>обсуждению заказа</em>'],
   ['articlesHeading','Материалы о <em>производстве</em>']
  ] as const
  for(const [field,original] of headings)if(typeof settings[field]==='string'&&settings[field])html=html.replace(original,esc(settings[field]))
  const picture=settings.heroImage
  if(picture&&typeof picture==='object'&&typeof picture.url==='string'&&/^https?:\/\//.test(picture.url))
    html=html.replace('/assets/hero-factory.svg',esc(picture.url))
 }
 // Trusted, version-controlled HTML template. Every CMS substitution is HTML-escaped.
 return <div dangerouslySetInnerHTML={{__html:html}}/>
}
