#!/usr/bin/env python3
"""Praktik Plast public TEST preview. No external dependencies.
Ephemeral demo CMS: test changes reset when Render replaces an instance.
"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path
import os, re, json, html, hmac, secrets, urllib.parse, time, threading
from email.parser import BytesParser
from email import policy
ROOT=Path(__file__).resolve().parent
DB=ROOT/'demo-content.json'
MEDIA_DIR=ROOT/'media'
MEDIA_DIR.mkdir(parents=True,exist_ok=True)
IMAGE_PATH=re.compile(r'/media/[0-9a-f]{32}\.(?:png|jpg|webp)\Z')
MAX_IMAGE_BYTES=3*1024*1024
MAX_UPLOAD_REQUEST=4*1024*1024
LOCK=threading.RLock()
SESSIONS={}
ATTEMPTS={}
PASSWORD=os.environ.get('ADMIN_PASSWORD','')
if not PASSWORD or len(PASSWORD)<16: raise RuntimeError('Set ADMIN_PASSWORD in Render secret env')
NAV=[('/','Главная'),('/uslugi/','Услуги'),('/produkciya/','Продукция'),('/proizvodstvo/','Производство'),('/stati/','Статьи'),('/kontakty/','Контакты')]
SERVICES=[
 ('litye-plastmass','Литьё пластмасс под давлением','Контрактное изготовление пластиковых деталей, изделий и комплектующих на ТПА.'),
 ('izdeliya-po-chertezham','Изделия по чертежам и образцам','Производство пластиковых деталей по техническому заданию заказчика.'),
 ('ekstruziya','Экструзия полимерных изделий','Изготовление полимерных трубок и профилей по согласованным параметрам.'),
 ('hoztovary-na-zakaz','Хозяйственные изделия под заказ','Серийное производство полимерных товаров и комплектующих.')
]
PRODUCTS=[
 ('veshalki-plechiki','Вешалки-плечики','Пластиковые плечики для одежды и оптовых заказчиков.'),
 ('torgovye-veshalki','Торговые вешалки','Элементы оснащения торговых предприятий.'),
 ('kolca-dlya-shtor','Кольца для штор','Пластиковые комплектующие для штор.'),
 ('sito-filtry','Сито-фильтры','Хозяйственные изделия для сливов.'),
 ('formy-dlya-bruschatki','Формы для брусчатки','Полимерные формы для изготовления изделий.'),
 ('elektromontazhnye-korobki','Электромонтажные коробки','Коробки для скрытого монтажа.'),
 ('elektroizolyacionnye-trubki','Электроизоляционные трубки','Экструзионные изоляционные трубки, кембрики.'),
 ('komponenty-nizkovoltnye','Детали низковольтного оборудования','Полимерные компоненты электротехнических изделий.')
]
ARTICLES=[
 ('kak-podgotovit-tz-na-litye','Как подготовить техническое задание на литьё пластмасс','Параметры, которые стоит указать перед запросом производственного расчёта.'),
 ('litye-ili-ekstruziya','Литьё или экструзия: выбор технологии','Чем отличаются технологии изготовления изделий из пластика.')
]
HOME_HEADINGS=[
 ("services_heading","Услуги","От задачи до готового изделия",'<h2 class="section-title">От задачи до <em>готового изделия</em></h2>'),
 ("products_heading","Продукция","Продукция для предприятий",'<h2 class="section-title">Продукция для <em>предприятий</em></h2>'),
 ("process_heading","Производство","Понятный процесс работы с заказом",'<h2 class="section-title">Понятный процесс <em>работы с заказом</em></h2>'),
 ("steps_heading","Как заказать","Четыре шага к обсуждению заказа",'<h2 class="section-title">Четыре шага к <em>обсуждению заказа</em></h2>'),
 ("articles_heading","Статьи","Материалы о производстве",'<h2 class="section-title">Материалы о <em>производстве</em></h2>'),
 ("cta_heading","Призыв к действию","Нужно изготовить пластиковое изделие?","<h2>Нужно изготовить пластиковое изделие?</h2>")
]
HOME_IMAGES=[
 ("hero","Обложка главной","Концептуальная иллюстрация линии литья пластмасс"),
 ("service_injection","Услуги: литьё","Условная иллюстрация: Литьё пластмасс под давлением"),
 ("service_blueprint","Услуги: чертежи","Условная иллюстрация: Изделия по чертежам и образцам"),
 ("service_extrusion","Услуги: экструзия","Условная иллюстрация: Экструзия полимерных изделий"),
 ("service_household","Услуги: хозтовары","Условная иллюстрация: Хозяйственные изделия под заказ"),
 ("product_hangers","Продукция: плечики","Условная иллюстрация: Вешалки-плечики"),
 ("product_display","Продукция: торговые вешалки","Условная иллюстрация: Торговые вешалки"),
 ("product_rings","Продукция: кольца","Условная иллюстрация: Кольца для штор"),
 ("product_filters","Продукция: фильтры","Условная иллюстрация: Сито-фильтры"),
 ("product_paving","Продукция: формы","Условная иллюстрация: Формы для брусчатки"),
 ("product_boxes","Продукция: монтажные коробки","Условная иллюстрация: Электромонтажные коробки"),
 ("product_tubes","Продукция: трубки","Условная иллюстрация: Электроизоляционные трубки"),
 ("product_parts","Продукция: низковольтные детали","Условная иллюстрация: Детали низковольтного оборудования"),
 ("production_drawing","Схема чертежа","Условная схема чертежа детали")
]

def seed():
 return {'settings':{'hero':'Пластиковые изделия для вашего бизнеса. От чертежа до партии.',
  'intro':'Контрактное литьё пластмасс, экструзия и серийная продукция. Обсудим ваш проект и условия сотрудничества.'},
  'services':[dict(slug=s,title=t,description=d,published=True) for s,t,d in SERVICES],
  'products':[dict(slug=s,title=t,description=d,published=True) for s,t,d in PRODUCTS],
  'articles':[dict(slug=s,title=t,description=d,published=True) for s,t,d in ARTICLES],
  'pages':[]}
if not DB.exists():DB.write_text(json.dumps(seed(),ensure_ascii=False,indent=2),encoding='utf-8')
def read_data():
 with LOCK:return json.loads(DB.read_text(encoding='utf-8'))
def save_data(obj):
 with LOCK:
  tmp=DB.with_suffix('.tmp')
  tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
  tmp.replace(DB)
def esc(s):return html.escape(str(s),quote=True)
def path_for(k,slug):return '/'+ {'services':'uslugi','products':'produkciya','articles':'stati','pages':'stranicy'}[k]+'/'+slug+'/'
def head(title,desc='Демонстрационный сайт Практик Пласт'):
 return '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="'+esc(desc)+'"><title>'+esc(title)+' | Практик Пласт</title><link rel="stylesheet" href="/assets/style.css"></head><body>'
def header():
 return '<div class="thinbar"><div class="container">ПРОИЗВОДСТВО ИЗДЕЛИЙ ИЗ ПОЛИМЕРОВ · ЛЕНИНГРАДСКАЯ ОБЛАСТЬ <span class="demo-stamp">ДЕМО</span></div></div><header class="tophead"><div class="container headerinner"><a class="brand" href="/"><span class="brand-icon"></span><span class="brand-type"><strong>ПРАКТИК ПЛАСТ</strong><span>ПРОИЗВОДСТВО ИЗДЕЛИЙ ИЗ ПОЛИМЕРОВ</span></span></a><nav id="main-menu" class="menu">'+''.join('<a href="'+url+'">'+name+'</a>' for url,name in NAV[1:])+'</nav><div class="header-actions"><a class="btn btn-primary" href="/zapros-rascheta/">Запросить расчёт ↗</a></div><button class="navtoggle" aria-label="Меню" aria-controls="main-menu">☰</button></div></header>'
def footer():
 return '<section class="cta-band"><div class="container cta-wrap"><div><h2>Нужно изготовить изделие из пластика?</h2><p>Расскажите о задаче и предполагаемом тираже.</p></div><a class="btn btn-primary" href="/zapros-rascheta/">Запросить расчёт →</a></div></section><footer class="footer"><div class="container"><div class="footer-cols"><div><h3 style="color:white">ПРАКТИК ПЛАСТ</h3><p>Промышленный B2B-сайт · Тестовая демонстрация</p></div><div><div class="footer-title">Разделы</div><a href="/uslugi/">Услуги</a><a href="/produkciya/">Продукция</a></div><div><div class="footer-title">Компания</div><a href="/proizvodstvo/">Производство</a><a href="/kontakty/">Контакты</a></div><div><div class="footer-title">Запрос расчёта</div><a href="/zapros-rascheta/">Отправить запрос</a></div></div></div></footer><script src="/assets/main.js" defer></script></body></html>'
def page(title,body,desc='',seo_title=None,seo_desc=None):
 return head(seo_title or title,seo_desc or desc)+header()+'<section class="inner-hero"><div class="container"><div class="eyebrow light">ПРАКТИК ПЛАСТ · ДЕМО</div><h1>'+esc(title)+'</h1><p>'+esc(desc)+'</p></div></section><main class="container page-content">'+body+'</main>'+footer()
def media_images(item):
 return [url for url in item.get('images',[]) if isinstance(url,str) and IMAGE_PATH.fullmatch(url)][:8]
def photo_html(url,title,small=False):
 return '<img loading="lazy" src="'+esc(url)+'" alt="'+esc(title)+'" style="display:block;width:100%;height:'+('170px' if small else '310px')+';object-fit:contain;background:#eef5f7;padding:10px;border-radius:5px">'
def cards(kind,entries):
 out=[]
 for item in entries:
  if not item.get('published',True):continue
  ims=media_images(item)
  image=photo_html(ims[0],item['title'],True) if ims else '<div style="height:170px;background:#e8f2f5;display:flex;align-items:center;justify-content:center;color:#658b96;font-size:13px">Фотография товара / услуги</div>'
  out.append('<a href="'+path_for(kind,item["slug"])+'">'+image+'<div style="padding:18px"><span class="service-tag">'+esc(kind)+'</span><h3>'+esc(item["title"])+'</h3><p>'+esc(item.get("description",""))+'</p><span class="text-arrow">Подробнее →</span></div></a>')
 return '<div class="listing">'+''.join(out)+'</div>'
def block_render(items):
 if not isinstance(items,list):return ''
 out=[]
 for item in items[:30]:
  if not isinstance(item,dict):continue
  kind=item.get('type')
  title=esc(item.get('title','')[:160])
  text=esc(item.get('text','')[:6000]).replace('\n','<br>')
  img=item.get('image','')
  if kind=='heading':
   out.append('<section style="padding:16px 0"><h2>'+title+'</h2></section>')
  elif kind=='text':
   out.append('<section class="section" style="padding:20px 0"><div style="max-width:870px"><h2>'+title+'</h2><p>'+text+'</p></div></section>')
  elif kind=='image' and isinstance(img,str) and IMAGE_PATH.fullmatch(img):
   out.append('<figure style="margin:35px 0"><img loading="lazy" src="'+esc(img)+'" alt="'+title+'" style="max-width:100%;max-height:600px;object-fit:contain;border-radius:8px"><figcaption>'+title+'</figcaption></figure>')
  elif kind=='cta':
   url=item.get('url','/zapros-rascheta/')
   if not isinstance(url,str) or not (url.startswith('/') and not url.startswith('//')):url='/zapros-rascheta/'
   out.append('<div class="darkpanel" style="margin:35px 0"><h2>'+title+'</h2><p>'+text+'</p><a class="btn btn-primary" href="'+esc(url)+'">'+esc(item.get('button','Запросить расчёт'))+'</a></div>')
  elif kind=='faq':
   content='<h2>'+title+'</h2>'
   for line in str(item.get('text','')).splitlines()[:15]:
    if '|' not in line:continue
    q,a=line.split('|',1)
    content+='<details style="padding:15px;border-bottom:1px solid #d7e5eb"><summary><b>'+esc(q)+'</b></summary><p>'+esc(a)+'</p></details>'
   out.append('<section style="margin:35px 0">'+content+'</section>')
 return ''.join(out)
def checked_blocks(value):
 if not isinstance(value,list) or len(value)>30:raise ValueError('Максимум 30 блоков')
 allowed={'heading','text','image','cta','faq'}
 result=[]
 for item in value:
  if not isinstance(item,dict) or item.get('type') not in allowed:raise ValueError('Недопустимый тип блока')
  entry={k:str(item.get(k,''))[:({'text':6000}.get(k,200))] for k in ('title','text','image','url','button')}
  entry['type']=item['type']
  if entry['image'] and not IMAGE_PATH.fullmatch(entry['image']):raise ValueError('Недопустимый путь к изображению')
  result.append(entry)
 return result

def render(route):
 data=read_data()
 if route=='/' or route=='/index.html':
  original=(ROOT/'index.html').read_text(encoding='utf-8')
  old='Пластиковые изделия <em>для вашего бизнеса.</em> От чертежа до партии.'
  original=original.replace(old,esc(data['settings']['hero']))
  original=original.replace('Контрактное литьё пластмасс, экструзия и серийная продукция. Обсудим ваш проект, технические требования и условия сотрудничества.',esc(data['settings']['intro']))
  original=original.replace('href="assets/','href="/assets/').replace('src="assets/','src="/assets/')
  original=original.replace('href="index.html"','href="/"')
  original=re.sub(r'href="(uslugi|produkciya|proizvodstvo|stati|o-kompanii|kontakty|zapros-rascheta|politika-konfidencialnosti)/',r'href="/\1/',original)
  settings=data.get('settings',{})
  for key,label,default,needle in HOME_HEADINGS:
   wrap='<h2 class="section-title">' if key!='cta_heading' else '<h2>'
   original=original.replace(needle,wrap+esc(settings.get(key,default))+'</h2>')
  slots=settings.get('slots',{})
  hero_images=media_images(settings)
  if hero_images and not slots.get('hero'):
   original=original.replace('src="/assets/hero-factory.svg"', 'src="'+esc(hero_images[0])+'"')
  for key,label,alt in HOME_IMAGES:
   url=slots.get(key)
   if not isinstance(url,str) or not IMAGE_PATH.fullmatch(url):continue
   pattern=r'(<img\b[^>]*?src=")[^"]+("[^>]*?alt="'+re.escape(alt)+'")'
   original=re.sub(pattern,lambda m:m.group(1)+esc(url)+m.group(2),original)
  published_products=[i for i in data['products'] if i.get('published',True)]
  gallery='<section class="section soft"><div class="container"><div class="section-head"><div><span class="kicker">КАТАЛОГ</span><h2 class="section-title">Изделия из пластика</h2></div><a href="/produkciya/">Весь каталог →</a></div>'+cards('products',published_products[:4])+'</div></section>'
  original=original.replace('</main>', gallery+'</main>')
  return original
 if route=='/health':return 'ok'
 cleaned=route.strip('/')
 parts=cleaned.split('/')
 if cleaned in ('uslugi','produkciya','stati','stranicy'):
  k={'uslugi':'services','produkciya':'products','stati':'articles','stranicy':'pages'}[cleaned]
  return page({'services':'Производственные услуги','products':'Каталог продукции','articles':'Статьи и материалы','pages':'Страницы'}[k],cards(k,data[k]),'Производство пластиковых изделий для предприятий и оптовых покупателей.')
 if len(parts)==2 and parts[0] in ('uslugi','produkciya','stati','stranicy'):
  k={'uslugi':'services','produkciya':'products','stati':'articles','stranicy':'pages'}[parts[0]]
  obj=next((x for x in data[k] if x['slug']==parts[1] and x.get('published',True)),None)
  if obj:
   b='<div class="split"><div><p style="font-size:19px">'+esc(obj.get('description',''))+'</p><p>Для точного расчёта производства укажите материал, предполагаемую партию и технические требования.</p><a class="btn btn-primary" href="/zapros-rascheta/">Запросить расчёт ↗</a></div><div class="darkpanel"><h3>'+esc(obj['title'])+'</h3><p>Номенклатура, наличие и условия поставки уточняются у предприятия.</p></div></div>'
   ims=media_images(obj)
   if ims:
    gallery='<section style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:32px">'+''.join(photo_html(url,obj['title']) for url in ims)+'</section>'
    b=gallery+b
   b+=block_render(obj.get('blocks',[]))
   return page(obj['title'],b,obj.get('description',''),obj.get('seo_title'),obj.get('seo_description'))
 if cleaned=='proizvodstvo':
  return page('Производство','<p>Контрактное литьё пластмасс, экструзия, производство изделий по чертежам и образцам.</p><p>Технические характеристики оборудования и сведения о производстве требуют подтверждения заказчиком.</p>')
 if cleaned=='o-kompanii':
  return page('О компании','<p>ООО «Практик». Предприятие в Ленинградской области. Производство и поставки полимерных изделий.</p>')
 if cleaned=='kontakty':
  return page('Контакты','<p><strong>Телефон:</strong> <a href="tel:+79219703920">+7 (921) 970-39-20</a></p><p><strong>Электронная почта:</strong> <a href="mailto:kobzealeksandr@yandex.ru">kobzealeksandr@yandex.ru</a></p><p>Ленинградская область, пгт Виллози.</p><p class="muted">Контакты и реквизиты требуют подтверждения перед коммерческой публикацией.</p>')
 if cleaned=='zapros-rascheta':
  b='<div class="form-box"><p class="notice">Демонстрационная форма. Сервер не хранит заявки и не передаёт их в CRM: откроется почтовая программа.</p><form id="request" data-mailto-form><label>Контактное лицо<input name="name" required></label><label>Компания<input name="company"></label><label>Телефон или e-mail<input name="contact" required></label><label>Тип заказа<select name="type"><option>Контрактное литьё</option><option>Экструзия</option><option>Готовая продукция</option></select></label><label>Тираж<input name="quantity"></label><label>Описание<textarea name="comment" required></textarea></label><button class="btn btn-primary" type="submit">Подготовить письмо →</button></form></div>'
  return page('Запросить расчёт',b,'Расскажите о вашем проекте')
 if cleaned=='politika-konfidencialnosti':
  return page('Обработка персональных данных','<p>Это демонстрационная версия. До коммерческого запуска необходимо утвердить политику обработки персональных данных.</p>')
 return None
def home_image_fields(settings):
 slots=settings.get('slots',{})
 out='<div class="panel"><h2>Все изображения главной</h2><p class="muted">Заменяй фотографии каждого блока прямо здесь. После загрузки нажми «Сохранить изменения».</p>'
 for key,label,alt in HOME_IMAGES:
  url=slots.get(key,'')
  if not isinstance(url,str) or not IMAGE_PATH.fullmatch(url):url=''
  out+='<div class="media-slot"><div style="flex:1;min-width:240px"><b>'+esc(label)+'</b><p class="muted">'+esc(alt)+'</p><input readonly name="slot_'+esc(key)+'" data-media-url value="'+esc(url)+'" placeholder="Пока используется стандартное изображение"></div><div><img data-media-preview style="width:120px;height:80px;object-fit:contain;background:#e9f2f6" '+('src="'+esc(url)+'"' if url else '')+' alt=""><input type="file" data-media-input accept="image/png,image/jpeg,image/webp" style="width:200px"><button type="button" data-media-remove class="btn danger" style="padding:5px 12px;font-size:12px">Убрать</button></div></div>'
 return out+'</div>'
HOME_UPLOAD_JS=r"""<script>(function(){
const csrf=document.querySelector('input[name="csrf"]'),info=document.getElementById('home-upload-status'),save=document.getElementById('home-save');
document.querySelectorAll('.media-slot').forEach(row=>{
 const file=row.querySelector('[data-media-input]'),url=row.querySelector('[data-media-url]'),img=row.querySelector('[data-media-preview]'),remove=row.querySelector('[data-media-remove]');
 if(!file||!url)return;
 file.addEventListener('change',async()=>{const f=file.files&&file.files[0];if(!f)return;if(save)save.disabled=true;
 try{if(f.size>3145728)throw Error('Максимум 3 МБ');const fd=new FormData();fd.append('csrf',csrf.value);fd.append('file',f);
 const res=await fetch('/admin/upload',{method:'POST',body:fd,credentials:'same-origin'});const data=await res.json();if(!res.ok||!data.url)throw Error(data.error||'Ошибка загрузки');
 url.value=data.url;img.src=data.url;if(info)info.textContent='Фотография загружена. Сохрани изменения.';}
 catch(err){if(info)info.textContent=err.message}finally{file.value='';if(save)save.disabled=false;}});
 remove.addEventListener('click',()=>{url.value='';img.removeAttribute('src')});
});
})()</script>"""

CSSADMIN="""<style>body{background:#f4f6f8;font:15px/1.5 Arial,sans-serif;color:#142a3b;margin:0}.wrap{max-width:1030px;margin:35px auto;padding:0 20px}h1{font-size:28px;margin:12px 0}.nav{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}.nav a{padding:9px 14px;background:white;border:1px solid #d6e1e8;border-radius:5px;color:#075b6d;text-decoration:none}.panel{background:white;padding:25px;border:1px solid #dce5eb;border-radius:9px;margin-bottom:16px}.warn{background:#fff7e4;border:1px solid #e6bc70;padding:13px 17px;border-radius:5px;color:#795c21}input,textarea,select{display:block;width:100%;padding:11px;border:1px solid #cbdce4;border-radius:5px;margin:6px 0 16px;box-sizing:border-box;font:inherit}textarea{min-height:145px}.btn{background:#0d7e87;color:white;padding:11px 18px;border:none;border-radius:5px;cursor:pointer;font:inherit}.danger{background:#b84848}.listitem{display:flex;justify-content:space-between;gap:15px;padding:12px;border-bottom:1px solid #edf0f3}.muted{color:#758996;font-size:13px}a{color:#037e90}label{font-weight:650}.tabs{display:flex;gap:16px;flex-wrap:wrap}.small{font-size:12px}.block-card{padding:17px;border:1px solid #dee8ed;background:#f9fbfc;border-radius:8px;margin:12px 0}.block-top{display:flex;align-items:center;gap:10px;margin-bottom:15px}.block-top b{flex:1}.block-btn{border:1px solid #d7e4e9;background:white;border-radius:5px;padding:5px 9px;cursor:pointer}.block-buttons{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.block-buttons .btn{font-size:12px;padding:8px 10px}.media-slot{display:flex;gap:15px;align-items:center;border:1px solid #e0e8ed;border-radius:8px;padding:12px;margin:9px 0;flex-wrap:wrap}.media-slot input[type=file]{font-size:12px;margin:7px 0}.media-slot .btn{padding:5px 9px}
</style>"""
def admin_html(auth=True):
 return '<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">'+CSSADMIN+'<div class="wrap"><p><a href="/">← Открыть сайт</a></p><h1>Практик Пласт · CMS (тест)</h1><div class="warn"><b>Демо-режим:</b> на бесплатном хостинге изменения могут исчезнуть при перезапуске или новой публикации. Не используйте здесь реальные персональные данные или коммерчески важные материалы.</div>'
def session_from(h):
 c=SimpleCookie()
 try:c.load(h.headers.get('Cookie',''))
 except Exception:return None
 item=c.get('pp_session')
 if not item:return None
 s=SESSIONS.get(item.value)
 return s if s and s['expire']>time.time() else None
def image_editor(item):
 images=media_images(item)
 imgs=json.dumps(images,ensure_ascii=False)
 return ('<div class="panel" style="background:#f8fafb"><h3>Фотографии</h3>'
  '<p class="muted">Можно загрузить до 8 JPG, PNG или WebP, не более 3 МБ каждое. Изображения появятся в каталоге после сохранения.</p>'
  '<input id="images-value" type="hidden" name="images" value="'+esc(imgs)+'">'
  '<div id="image-gallery-editor" style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px"></div>'
  '<label>Добавить фотографии<input id="add-images" type="file" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp" multiple></label>'
  '<p class="muted" id="upload-status">Фотографии временно сохраняются на тестовом сервере. При перезапуске Render они могут пропасть.</p></div>')
IMAGE_EDITOR_JS=r"""<script>(function(){
const file=document.getElementById('add-images'),hidden=document.getElementById('images-value'),gallery=document.getElementById('image-gallery-editor'),status=document.getElementById('upload-status'),submit=document.getElementById('save-record'),csrf=document.querySelector('input[name="csrf"]');
if(!file||!hidden||!gallery||!csrf)return;
let images=[];try{images=JSON.parse(hidden.value)||[]}catch(e){}
function draw(){
 gallery.replaceChildren();
 images.forEach((url,index)=>{
  const wrap=document.createElement('div');wrap.style.cssText='width:142px;background:#fff;padding:7px;border:1px solid #d9e5e9;border-radius:6px';
  const img=document.createElement('img');img.src=url;img.alt='Фото '+(index+1);img.style.cssText='width:126px;height:100px;object-fit:contain;background:#eef5f7';
  const btn=document.createElement('button');btn.type='button';btn.textContent='Удалить';btn.className='btn danger';btn.style.cssText='padding:5px 10px;font-size:12px;width:100%';
  btn.addEventListener('click',()=>{images.splice(index,1);draw()});
  wrap.append(img,btn);gallery.append(wrap);
 });
 hidden.value=JSON.stringify(images);
}
file.addEventListener('change',async()=>{
 const files=Array.from(file.files||[]);
 if(!files.length)return;
 if(images.length+files.length>8){status.textContent='Максимум 8 изображений на запись';file.value='';return}
 if(submit)submit.disabled=true;
 try{
  for(const f of files){
   if(f.size>3*1024*1024){throw Error('Файл '+f.name+' больше 3 МБ')}
   const body=new FormData();body.append('csrf',csrf.value);body.append('file',f);
   status.textContent='Загружаю '+f.name+'...';
   const res=await fetch('/admin/upload',{method:'POST',body,credentials:'same-origin'});
   const json=await res.json().catch(()=>({error:'Ответ сервера не получен'}));
   if(!res.ok||!json.url)throw Error(json.error||'HTTP '+res.status);
   images.push(json.url);draw();
  }
  status.textContent='Загружено. Нажми «Сохранить», чтобы прикрепить фотографии к записи.';
 }catch(err){status.textContent='Ошибка загрузки: '+err.message}
 finally{file.value='';if(submit)submit.disabled=false}
});
draw();
})()</script>"""
def blocks_form(item):
 raw=esc(json.dumps(item.get('blocks',[]),ensure_ascii=False))
 return ('<div class="panel"><h2>Конструктор страницы</h2>'
  '<p class="muted">Добавляйте заголовки, текст, изображения, FAQ и призывы к действию. Меняйте порядок стрелками. Результат появится на опубликованной странице.</p>'
  '<input type="hidden" name="blocks" id="blocks-state" value="'+raw+'">'
  '<div id="blocks-editor"></div><div class="block-buttons">'
  '<button type="button" class="btn" data-new-block="heading">+ Заголовок</button> '
  '<button type="button" class="btn" data-new-block="text">+ Текст</button> '
  '<button type="button" class="btn" data-new-block="image">+ Фото</button> '
  '<button type="button" class="btn" data-new-block="faq">+ Вопросы / FAQ</button> '
  '<button type="button" class="btn" data-new-block="cta">+ Кнопка / CTA</button></div></div>')
BLOCK_EDITOR_JS=r"""<script>(function(){
const field=document.getElementById('blocks-state'),root=document.getElementById('blocks-editor'),csrf=document.querySelector('input[name="csrf"]'),save=document.getElementById('save-record');
if(!field||!root)return;
let blocks=[];try{blocks=JSON.parse(field.value)||[]}catch(e){}
const types={heading:'Заголовок H2',text:'Текстовый блок',image:'Изображение',faq:'Вопросы и ответы',cta:'Призыв к действию'};
function sync(){field.value=JSON.stringify(blocks)}
function elt(tag,props={}){const e=document.createElement(tag);Object.entries(props).forEach(([k,v])=>{if(k==='text')e.textContent=v;else if(k==='className')e.className=v;else e[k]=v});return e}
function addField(card,b,name,label,multi=false){
const lab=elt('label',{text:label});const inp=elt(multi?'textarea':'input');inp.value=b[name]||'';inp.placeholder=label;inp.maxLength=name==='text'?6000:200;
inp.addEventListener('input',()=>{b[name]=inp.value;sync()});lab.appendChild(inp);card.append(lab);return inp;
}
function draw(){
root.replaceChildren();sync();
blocks.forEach((b,i)=>{
const card=elt('div',{className:'block-card'}),top=elt('div',{className:'block-top'}),h=elt('b',{text:(i+1)+'. '+(types[b.type]||b.type)});
top.append(h);
[['↑',()=>{if(i){[blocks[i-1],blocks[i]]=[blocks[i],blocks[i-1]];draw()}}],
 ['↓',()=>{if(i+1<blocks.length){[blocks[i+1],blocks[i]]=[blocks[i],blocks[i+1]];draw()}}],
 ['✕',()=>{blocks.splice(i,1);draw()}]].forEach(([name,cb])=>{const btn=elt('button',{type:'button',text:name,className:'block-btn'});btn.addEventListener('click',cb);top.append(btn)});
card.append(top);
addField(card,b,'title','Заголовок блока');
if(['text','faq','cta'].includes(b.type))addField(card,b,'text',b.type==='faq'?'По одной паре на строку: Вопрос | Ответ':'Текст',true);
if(b.type==='cta'){addField(card,b,'button','Текст кнопки');addField(card,b,'url','Ссылка кнопки (например /zapros-rascheta/)')}
if(b.type==='image'){
const prev=elt('img');prev.style.cssText='display:block;max-width:250px;max-height:180px;object-fit:contain;margin:10px 0;background:#e7f0f4';
if(b.image)prev.src=b.image;card.append(prev);
const input=elt('input',{type:'file'});input.accept='image/jpeg,image/png,image/webp';
const status=elt('p',{className:'muted',text:'Фотография до 3 МБ'});
input.addEventListener('change',async()=>{
const f=input.files&&input.files[0];if(!f)return;if(save)save.disabled=true;
try{if(f.size>3145728)throw Error('Файл слишком большой');const fd=new FormData();fd.append('csrf',csrf.value);fd.append('file',f);
const res=await fetch('/admin/upload',{method:'POST',body:fd});const obj=await res.json();if(!res.ok||!obj.url)throw Error(obj.error||'Не удалось загрузить');
b.image=obj.url;prev.src=obj.url;status.textContent='Загружено. Нажми «Сохранить».';sync();
}catch(e){status.textContent=e.message}finally{input.value='';if(save)save.disabled=false}});
card.append(input,status);
}
root.append(card);
});
}
document.querySelectorAll('[data-new-block]').forEach(button=>button.addEventListener('click',()=>{
if(blocks.length>=30){alert('Максимум 30 блоков на страницу');return}
const type=button.dataset.newBlock;blocks.push({type,title:'',text:'',image:'',url:'/zapros-rascheta/',button:'Запросить расчёт'});draw();
}));
draw();
})()</script>"""

def edit_form(k,data,slug=''):
 entries=data.get(k,[])
 item=next((x for x in entries if x['slug']==slug),None) if slug else None
 if item is None:item={'title':'','slug':'','description':'','published':True,'images':[]}
 opts={'services':'Услуги','products':'Каталог','articles':'Статьи','pages':'Страницы'}
 return ('<div class="panel"><h2>'+('Редактировать' if slug else 'Добавить')+' · '+opts[k]+'</h2>'
  '<form method="post" action="/admin/save"><input type="hidden" name="csrf" value="{{csrf}}"><input type="hidden" name="kind" value="'+k+'"><input type="hidden" name="original" value="'+esc(slug)+'">'
  '<label>Название<input required maxlength="150" name="title" value="'+esc(item['title'])+'"></label>'
  '<label>Адрес (латиницей: a-z, цифры, дефис)<input required pattern="[a-z0-9-]+" maxlength="70" name="slug" value="'+esc(item['slug'])+'"></label>'
  '<label>Краткое описание<textarea maxlength="4000" name="description">'+esc(item.get('description',''))+'</textarea></label>'
  '<label>SEO Title<input maxlength="180" name="seo_title" value="'+esc(item.get('seo_title',''))+'" placeholder="Если пусто — название страницы"></label>'
  '<label>SEO Description<textarea maxlength="450" name="seo_description" placeholder="Если пусто — краткое описание">'+esc(item.get('seo_description',''))+'</textarea></label>'
  +image_editor(item)+blocks_form(item)+
  '<label><input style="display:inline;width:auto" type="checkbox" name="published" '+('checked' if item.get('published',True) else '')+'> Опубликовано</label>'
  '<p><button id="save-record" class="btn">Сохранить</button> '+('<a href="'+path_for(k,slug)+'" target="_blank">Открыть страницу ↗</a>' if slug else '')+'</p></form></div>'+IMAGE_EDITOR_JS+BLOCK_EDITOR_JS)
class H(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,status,body,ctype='text/html; charset=utf-8',cookie=None):
  data=body.encode('utf-8') if isinstance(body,str) else body
  self.send_response(status)
  for k,v in [('Content-Type',ctype),('Content-Length',str(len(data))),('X-Content-Type-Options','nosniff'),('X-Frame-Options','DENY'),('Referrer-Policy','no-referrer'),('Cache-Control','no-store')]:self.send_header(k,v)
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(data)
 def redirect(self,to,cookie=None):
  self.send_response(303);self.send_header('Location',to)
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers()
 def do_GET(self):
  p=urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
  if p.startswith('/media/'):
   if not IMAGE_PATH.fullmatch(p):return self.send(404,'Not found','text/plain')
   path=MEDIA_DIR/Path(p).name
   if not path.is_file():return self.send(404,'File not found','text/plain')
   ext=path.suffix.lower()
   return self.send(200,path.read_bytes(),{'.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp'}[ext])
  if p.startswith('/assets/'):
   suffix=Path(p).suffix.lower()
   if suffix=='.svg':
    label=esc(Path(p).stem.replace('-',' ').title())
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="680" height="430" viewBox="0 0 680 430"><rect width="680" height="430" fill="#d9eaf0"/><circle cx="500" cy="120" r="180" fill="#b2d3db"/><rect x="110" y="145" width="420" height="170" rx="14" fill="#14556b"/><rect x="150" y="185" width="330" height="90" rx="8" fill="#20a2a5" opacity=".6"/><path d="M175 240h280m-150-60v100" stroke="#d9eeee" stroke-width="8"/><text x="340" y="362" fill="#155267" font-size="23" text-anchor="middle" font-family="Arial">'+label+'</text></svg>'
    return self.send(200,svg,'image/svg+xml')
   if suffix in ('.css','.js'):
    name=Path(p).name
    f=ROOT/'assets'/name
    if f.exists():return self.send(200,f.read_bytes(),'text/css' if suffix=='.css' else 'text/javascript')
  if p=='/admin' or p.startswith('/admin/'):
   s=session_from(self)
   if not s:
    return self.send(200,admin_html()+'<div class="panel"><h2>Вход в редактор</h2><form method="post" action="/admin/login"><label>Логин<input name="username" required autocomplete="username"></label><label>Пароль<input name="password" type="password" required autocomplete="current-password"></label><button class="btn">Войти</button></form></div></div>')
   data=read_data();csrf=esc(s['csrf'])
   kind=urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get('kind',['products'])[0]
   if kind not in ('products','services','articles','pages','settings'):kind='products'
   slug=urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get('slug',[''])[0]
   nav='<div class="nav">'+''.join('<a href="/admin/?kind='+k+'">'+text+'</a>' for k,text in [('products','Каталог'),('services','Услуги'),('articles','Статьи'),('pages','Страницы'),('settings','Главная')])+'</div>'
   b=admin_html()+nav
   if kind=='settings':
    item=data['settings']
    b+='<form method="post" action="/admin/save"><input type="hidden" name="csrf" value="'+csrf+'"><input type="hidden" name="kind" value="settings">'
    b+='<div class="panel"><h2>Первый экран</h2><label>Главный заголовок H1<input maxlength="180" name="hero" value="'+esc(item.get('hero',''))+'"></label><label>Подзаголовок<textarea maxlength="600" name="intro">'+esc(item.get('intro',''))+'</textarea></label></div>'
    b+='<div class="panel"><h2>Заголовки всех секций</h2><p class="muted">Изменения сразу отражаются на публичной странице после сохранения.</p>'
    for key,label,default,_ in HOME_HEADINGS:b+='<label>'+esc(label)+'<input name="'+key+'" maxlength="160" value="'+esc(item.get(key,default))+'"></label>'
    b+='</div>'+home_image_fields(item)
    b+='<div class="panel"><p class="muted" id="home-upload-status">Изображения: JPG, PNG, WebP до 3 МБ.</p><button id="home-save" class="btn">Сохранить изменения</button> <a href="/" target="_blank" style="margin-left:12px">Посмотреть главную ↗</a></div></form>'+HOME_UPLOAD_JS
   else:
    b+='<div class="panel"><h2>Материалы: '+str(len(data[kind]))+'</h2>'
    for i in data[kind]:
     b+='<div class="listitem"><div>'+esc(i['title'])+' <span class="muted">'+('Опубликовано' if i.get('published') else 'Черновик')+'</span></div><a href="/admin/?kind='+kind+'&slug='+esc(i['slug'])+'">Редактировать</a></div>'
    b+='</div>'+edit_form(kind,data,slug).replace('{{csrf}}',csrf)
   b+='<div class="panel"><form action="/admin/logout" method="post"><input type="hidden" name="csrf" value="'+csrf+'"><button class="btn danger">Выйти</button></form></div></div>'
   return self.send(200,b)
  if p.startswith('/cms/') or p.startswith('/.'):return self.send(404,'Not found','text/plain')
  route='/'+p.strip('/')
  if Path(route).suffix=='.html':route=route.removesuffix('index.html')
  if not route.endswith('/'):route+='/'
  output=render(route)
  return self.send(200,output) if output is not None else self.send(404,page('Страница не найдена','<p>Такой страницы пока нет.</p>'))
 def do_POST(self):
  route=urllib.parse.urlsplit(self.path).path
  size=int(self.headers.get('Content-Length','0') or '0')
  if route not in ('/admin/login','/admin/save','/admin/logout','/admin/upload'):return self.send(404,'Not found','text/plain')
  if size<1 or size>MAX_UPLOAD_REQUEST:return self.send(413,'Слишком большой запрос','text/plain')
  if route=='/admin/upload':
   sess=session_from(self)
   if not sess:return self.send(403,json.dumps({'error':'Требуется вход в CMS'}),'application/json')
   ctype=self.headers.get('Content-Type','')
   if not ctype.lower().startswith('multipart/form-data;'):return self.send(415,json.dumps({'error':'Требуется multipart/form-data'}),'application/json')
   raw=self.rfile.read(size)
   try:
    email_data=b'Content-Type: '+ctype.encode('ascii')+b'\r\nMIME-Version: 1.0\r\n\r\n'+raw
    multi=BytesParser(policy=policy.default).parsebytes(email_data)
    if not multi.is_multipart():raise ValueError('Некорректный multipart')
    fields={p.get_param('name',header='content-disposition'):p for p in multi.iter_parts()}
    csrf_part=fields.get('csrf')
    supplied=csrf_part.get_payload(decode=True).decode('ascii') if csrf_part else ''
    if not hmac.compare_digest(supplied,sess['csrf']):return self.send(403,json.dumps({'error':'Недействительный CSRF'}),'application/json')
    file=fields.get('file')
    if file is None or not file.get_filename():raise ValueError('Файл не выбран')
    data=file.get_payload(decode=True)
    if not data or len(data)>MAX_IMAGE_BYTES:raise ValueError('Максимальный размер файла — 3 МБ')
    if data[:8]==bytes.fromhex('89504e470d0a1a0a') and b'IEND' in data[-24:]:ext='.png'
    elif data[:3]==bytes.fromhex('ffd8ff') and data[-2:]==bytes.fromhex('ffd9'):ext='.jpg'
    elif data[:4]==b'RIFF' and data[8:12]==b'WEBP':ext='.webp'
    else:raise ValueError('Разрешены только PNG, JPG и WebP')
    filename=secrets.token_hex(16)+ext
    with (MEDIA_DIR/filename).open('xb') as out:out.write(data)
    return self.send(201,json.dumps({'url':'/media/'+filename}),'application/json')
   except (ValueError,UnicodeError,TypeError) as error:
    return self.send(400,json.dumps({'error':str(error)},ensure_ascii=False),'application/json')
  if size>220000:return self.send(413,'Слишком большой запрос','text/plain')
  form=urllib.parse.parse_qs(self.rfile.read(size).decode('utf-8','replace'))
  get=lambda k,default='':form.get(k,[default])[0]
  if route=='/admin/login':
   ip=self.client_address[0];now=time.time();ATTEMPTS[ip]=[t for t in ATTEMPTS.get(ip,[]) if now-t<600]
   if len(ATTEMPTS[ip])>=10:return self.send(429,'Слишком много попыток входа','text/plain')
   if not (hmac.compare_digest(get('username'),'admin') and hmac.compare_digest(get('password'),PASSWORD)):
    ATTEMPTS[ip].append(now)
    return self.send(401,admin_html()+'<div class="panel">Неверный логин или пароль. <a href="/admin">Повторить</a></div></div>')
   token=secrets.token_urlsafe(32);SESSIONS[token]={'csrf':secrets.token_urlsafe(24),'expire':time.time()+8*3600}
   return self.redirect('/admin',cookie='pp_session='+token+'; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=28800')
  sess=session_from(self)
  if not sess or not hmac.compare_digest(get('csrf'),sess['csrf']):return self.send(403,'Нет доступа или недействительный CSRF','text/plain')
  if route=='/admin/logout':
   c=SimpleCookie();c.load(self.headers.get('Cookie',''));obj=c.get('pp_session')
   if obj:SESSIONS.pop(obj.value,None)
   return self.redirect('/admin',cookie='pp_session=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0')
  kind=get('kind')
  if kind not in ('services','products','articles','pages','settings'):return self.send(400,'Invalid kind','text/plain')
  data=read_data()
  try:
   image_list=json.loads(get('images','[]'))
   if not isinstance(image_list,list) or len(image_list)>8 or any(not isinstance(u,str) or not IMAGE_PATH.fullmatch(u) for u in image_list):raise ValueError()
  except (ValueError,TypeError):
   return self.send(400,'Недопустимые ссылки на изображения','text/plain')
  if kind=='settings':
   current=data['settings']
   current['hero']=get('hero')[:180]
   current['intro']=get('intro')[:600]
   for key,_,default,_ in HOME_HEADINGS:
    current[key]=get(key,default)[:160]
   slots=current.get('slots',{})
   for key,_,_ in HOME_IMAGES:
    url=get('slot_'+key)
    if url and not IMAGE_PATH.fullmatch(url):return self.send(400,'Некорректный путь к изображению','text/plain')
    slots[key]=url
   current['slots']=slots
   current['images']=image_list
  else:
   slug=get('slug');old=get('original')
   if not re.fullmatch('[a-z0-9][a-z0-9-]{0,68}',slug):return self.send(400,'URL: только латинские буквы и цифры','text/plain')
   if old and slug!=old:return self.send(400,'Изменять URL существующей страницы нельзя','text/plain')
   try:blocks=checked_blocks(json.loads(get('blocks','[]')))
   except (ValueError,TypeError):return self.send(400,'Некорректные блоки страницы','text/plain')
   new={'slug':slug,'title':get('title')[:150],'description':get('description')[:4000],'seo_title':get('seo_title')[:180],'seo_description':get('seo_description')[:450],'blocks':blocks,'published':bool(get('published')),'images':image_list}
   if not new['title']:return self.send(400,'Title required','text/plain')
   records=data[kind];existing=next((x for x in records if x['slug']==slug),None)
   if existing:records[records.index(existing)]=new
   else:records.append(new)
  save_data(data)
  return self.redirect('/admin/?kind='+urllib.parse.quote(kind))
if __name__=='__main__':
 port=int(os.getenv('PORT','10000'))
 print('Praktik Plast demo listening on',port,flush=True)
 ThreadingHTTPServer(('0.0.0.0',port),H).serve_forever()
