#!/usr/bin/env python3
"""Praktik Plast public TEST preview. No external dependencies.
Ephemeral demo CMS: test changes reset when Render replaces an instance.
"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path
import os, re, json, html, hmac, secrets, urllib.parse, time, threading
ROOT=Path(__file__).resolve().parent
DB=ROOT/'demo-content.json'
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
def page(title,body,desc=''):
 return head(title,desc)+header()+'<section class="inner-hero"><div class="container"><div class="eyebrow light">ПРАКТИК ПЛАСТ · ДЕМО</div><h1>'+esc(title)+'</h1><p>'+esc(desc)+'</p></div></section><main class="container page-content">'+body+'</main>'+footer()
def cards(kind,entries):
 return '<div class="listing">'+''.join('<a href="'+path_for(kind,item["slug"])+'"><span class="service-tag">'+esc(kind)+'</span><h3>'+esc(item["title"])+'</h3><p>'+esc(item.get("description",""))+'</p><span class="text-arrow">Подробнее →</span></a>' for item in entries if item.get('published',True))+'</div>'
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
   return page(obj['title'],b,obj.get('description',''))
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
CSSADMIN="""<style>body{background:#f4f6f8;font:15px/1.5 Arial,sans-serif;color:#142a3b;margin:0}.wrap{max-width:1030px;margin:35px auto;padding:0 20px}h1{font-size:28px;margin:12px 0}.nav{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}.nav a{padding:9px 14px;background:white;border:1px solid #d6e1e8;border-radius:5px;color:#075b6d;text-decoration:none}.panel{background:white;padding:25px;border:1px solid #dce5eb;border-radius:9px;margin-bottom:16px}.warn{background:#fff7e4;border:1px solid #e6bc70;padding:13px 17px;border-radius:5px;color:#795c21}input,textarea,select{display:block;width:100%;padding:11px;border:1px solid #cbdce4;border-radius:5px;margin:6px 0 16px;box-sizing:border-box;font:inherit}textarea{min-height:145px}.btn{background:#0d7e87;color:white;padding:11px 18px;border:none;border-radius:5px;cursor:pointer;font:inherit}.danger{background:#b84848}.listitem{display:flex;justify-content:space-between;gap:15px;padding:12px;border-bottom:1px solid #edf0f3}.muted{color:#758996;font-size:13px}a{color:#037e90}label{font-weight:650}.tabs{display:flex;gap:16px;flex-wrap:wrap}.small{font-size:12px}</style>"""
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
def edit_form(k,data,slug=''):
 entries=data.get(k,[])
 item=next((x for x in entries if x['slug']==slug),None) if slug else None
 if item is None:item={'title':'','slug':'','description':'','published':True}
 opts={'services':'Услуги','products':'Каталог','articles':'Статьи','pages':'Страницы'}
 return '<div class="panel"><h2>'+('Редактировать' if slug else 'Добавить')+' · '+opts[k]+'</h2><form method="post" action="/admin/save"><input type="hidden" name="csrf" value="{{csrf}}"><input type="hidden" name="kind" value="'+k+'"><input type="hidden" name="original" value="'+esc(slug)+'"><label>Название<input required maxlength="150" name="title" value="'+esc(item['title'])+'"></label><label>Адрес (латиницей: a-z, цифры, дефис)<input required pattern="[a-z0-9-]+" maxlength="70" name="slug" value="'+esc(item['slug'])+'"></label><label>Описание / SEO description<textarea maxlength="4000" name="description">'+esc(item.get('description',''))+'</textarea></label><label><input style="display:inline;width:auto" type="checkbox" name="published" '+('checked' if item.get('published',True) else '')+'> Опубликовано</label><p><button class="btn">Сохранить</button></p></form></div>'
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
    b+='<div class="panel"><h2>Первый экран сайта</h2><form method="post" action="/admin/save"><input type="hidden" name="csrf" value="'+csrf+'"><input type="hidden" name="kind" value="settings"><label>Заголовок<input name="hero" value="'+esc(item['hero'])+'"></label><label>Описание<textarea name="intro">'+esc(item['intro'])+'</textarea></label><button class="btn">Сохранить</button></form></div>'
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
  if size<1 or size>30000:return self.send(413,'Слишком большой запрос','text/plain')
  if route not in ('/admin/login','/admin/save','/admin/logout'):return self.send(404,'Not found','text/plain')
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
  if kind=='settings':
   data['settings']['hero']=get('hero')[:180]
   data['settings']['intro']=get('intro')[:600]
  else:
   slug=get('slug');old=get('original')
   if not re.fullmatch('[a-z0-9][a-z0-9-]{0,68}',slug):return self.send(400,'URL: только латинские буквы и цифры','text/plain')
   if old and slug!=old:return self.send(400,'Изменять URL существующей страницы нельзя','text/plain')
   new={'slug':slug,'title':get('title')[:150],'description':get('description')[:4000],'published':bool(get('published'))}
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
