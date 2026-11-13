# Практик Пласт: Payload CMS / Next.js — тестовый стенд

## Архитектура
- Next.js 16, Payload CMS 3.93, PostgreSQL.
- Collections: pages, products, services, articles, media, users.
- SiteSettings global: header, hero, section headings, image, layout, SEO.
- Страницы из блоков Hero/Text/Image/Cards/FAQ/CTA.
- Черновики, автосохранение, история версий.
- Роли: admin, editor, catalog, seo, viewer.
- Дизайн главной страницы сохранён с первой HTML-версии в `src/legacy/home.html`, CSS в `src/app/(site)/site.css`.
- Старый Python-стенд не затронут.

## Локальный запуск
Node >=24.22.1, PostgreSQL 18. Создайте файл .env по примеру .env.example.
```bash
npm install
npm run dev
```
Payload admin: http://localhost:3000/admin. Первый администратор создаётся через первоначальную страницу настройки.

## Render
- Отдельный web service на бесплатном плане и отдельная тестовая PostgreSQL.
- Переменные: DATABASE_URL (internal connectionString), PAYLOAD_SECRET, PREVIEW_SECRET, PREVIEW_AUTO_SEED=true, PREVIEW_SCHEMA_PUSH=true, NEXT_PUBLIC_SERVER_URL.
- Версии: NODE_VERSION=24.22.3, NPM_CONFIG_PRODUCTION=false.
- Build: `npm install --no-audit --no-fund && npm run build`
- Start: `npm run start`
- Загрузка медиа отключена, пока не подключено постоянное S3-совместимое хранилище. Это намеренно: временный диск Render не подходит для CMS.
- Для Cloudflare R2 / S3: S3_BUCKET, S3_REGION, S3_ENDPOINT, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_PUBLIC_URL. Все ключи — только в Render Environment; в репозитории секретов нет.
- PostgreSQL Render Free истекает и не предназначена для долговременной эксплуатации. Нужна замена до истечения срока.
- Домен тестовый, весь сайт noindex.

## Контроль качества
1. Проверить /health и /
2. Создать первого администратора в /admin.
3. Создать услугу и товар, опубликовать. Открыть URL.
4. Создать статью из блоков H2, текст, FAQ, CTA.
5. Изменить настройки главной, опубликовать и открыть главную.
6. Проверить черновик/версии и публичную невозможность увидеть черновик.
7. Подключить S3 и проверить загрузку/последующее чтение изображения и перезапуск сервиса.
8. Перед продакшеном: миграции вместо schema push, резервное копирование, SMTP, ограничения доступа, rate limiting, SEO-карта редиректов, реальные формы и Bitrix24.

Тестовые данные относятся к предыдущему проекту; сведения о производстве и контакты до запуска согласовать с заказчиком.
