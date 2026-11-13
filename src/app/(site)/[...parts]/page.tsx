import type {Metadata} from 'next'
import {notFound} from 'next/navigation'
import {cms,getOne,getPublished,toMediaURL,type Kind} from '@/lib/content'
import {PageShell} from '@/lib/components'
import {Blocks} from '@/lib/blocks'
import {fallbackServices,fallbackProducts,fallbackArticles} from '@/lib/fixtures'
export const dynamic='force-dynamic'
type Props={params:Promise<{parts:string[]}>}
const routing:Record<string,Kind>={uslugi:'services',produkciya:'products',stati:'articles',stranicy:'pages'}
const titles:Record<string,string>={uslugi:'Производственные услуги',produkciya:'Каталог продукции',stati:'Статьи о производстве',stranicy:'Страницы'}
const fixture:Record<string,{slug:string;title:string;summary:string}[]>={uslugi:fallbackServices,produkciya:fallbackProducts,stati:fallbackArticles,stranicy:[]}
function label(v:unknown){return typeof v==='string'?v:''}
async function details(parts:string[]){
 if(parts.length!==2||!routing[parts[0]])return null
 try{return await getOne(routing[parts[0]],parts[1])}catch{return null}
}
export async function generateMetadata({params}:Props):Promise<Metadata>{
 const {parts}=await params
 const item=await details(parts) as Record<string,any>|null
 return {title:item?.metaTitle||label(item?.title)||titles[parts[0]]||'Практик Пласт',description:item?.metaDescription||label(item?.summary)||label(item?.excerpt)||'',robots:{index:false,follow:false}}
}
export default async function Route({params}:Props){
 const {parts}=await params
 const [section,slug]=parts
 if(parts.length===1&&routing[section]){
  let records:Record<string,any>[]=[]
  try{const rows=await getPublished(routing[section]);records=rows.docs as Record<string,any>[]}catch(err){console.error(err)}
  if(!records.length)records=fixture[section]||[]
  return <PageShell title={titles[section]} subtitle="Производство полимерных изделий и технические материалы"><section className="section"><div className="container listing">{records.map(i=><a key={i.slug} href={`/${section}/${i.slug}/`}>{toMediaURL(i.cover)&&<img className="cms-card-image" src={toMediaURL(i.cover)} alt={i.title}/>}<h3>{i.title}</h3><p>{i.summary||i.excerpt||''}</p><strong>Подробнее →</strong></a>)}</div></section></PageShell>
 }
 if(parts.length===2&&routing[section]){
  const doc=await details(parts) as Record<string,any>|null
  const fb=fixture[section]?.find(i=>i.slug===slug)
  if(!doc&&!fb)notFound()
  const record=doc||fb!
  return <PageShell title={record.title} subtitle={record.summary||record.excerpt||record.description||'Изготовление пластиковых изделий для B2B-заказчиков'}>
    <section className="section"><div className="container split"><div><p className="section-desc">{record.summary||record.excerpt||record.description}</p><p>Для коммерческого расчёта подготовьте чертёж, характеристики материала и требуемый тираж.</p><a className="btn btn-primary" href="/zapros-rascheta/">Запросить расчёт →</a></div>{toMediaURL(record.cover)&&<img src={toMediaURL(record.cover)} alt={record.title} className="cms-detail-cover"/>}</div></section>
    {Array.isArray(record.layout)&&<Blocks layout={record.layout}/>}
    {section==='produkciya'&&Array.isArray(record.skus)&&record.skus.length>0&&<section className="section soft"><div className="container"><h2>Артикулы и характеристики</h2><table className="data-table"><thead><tr><th>Артикул</th><th>Размер</th><th>Упаковка</th></tr></thead><tbody>{record.skus.map((v:Record<string,string>,i:number)=><tr key={i}><td>{v.article}</td><td>{v.size}</td><td>{v.pack}</td></tr>)}</tbody></table></div></section>}
  </PageShell>
 }
 if(parts.length!==1)notFound()
 if(section==='proizvodstvo')return <PageShell title="Производство" subtitle="Литьё пластмасс под давлением и экструзия"><section className="section"><div className="container"><h2>Производственные возможности</h2><p>Изготовление пластиковых изделий на заказ. Технические параметры оборудования необходимо подтвердить перед запуском рекламы.</p></div></section></PageShell>
 if(section==='o-kompanii')return <PageShell title="О компании"><section className="section"><div className="container"><p>Практик Пласт — производственный B2B-проект. Данные о предприятии требуют подтверждения.</p></div></section></PageShell>
 if(section==='kontakty')return <PageShell title="Контакты"><section className="section"><div className="container"><p>Контактные данные необходимо подтвердить с заказчиком перед публикацией.</p><a className="btn btn-primary" href="/zapros-rascheta/">Запросить расчёт</a></div></section></PageShell>
 if(section==='zapros-rascheta')return <PageShell title="Запросить расчёт"><section className="section"><div className="container form-box"><p className="notice">Демонстрационная версия. Отправка заявок и Bitrix24 будут подключены после согласования.</p><label>Имя<input disabled placeholder="Неактивно в демоверсии"/></label><label>Телефон<input disabled placeholder="Неактивно в демоверсии"/></label><label>Описание<textarea disabled placeholder="Неактивно в демоверсии"/></label></div></section></PageShell>
 if(section==='politika-konfidencialnosti')return <PageShell title="Политика конфиденциальности"><div className="container"><p>Демонстрационный сайт не принимает персональные данные через формы.</p></div></PageShell>
 notFound()
}
