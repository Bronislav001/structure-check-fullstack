# Краткая шпаргалка по ЛР-4

## Что сделано
1. SEO-оптимизация:
   - dynamic title/description;
   - canonical URL;
   - Open Graph meta tags;
   - JSON-LD;
   - `robots.txt` и `sitemap.xml` на backend;
   - 404 страница;
   - lazy loading тяжёлого блока с внешними источниками.
2. Внешний API:
   - backend-адаптер к Google Books;
   - timeout;
   - retry;
   - rate limiting;
   - нормализация ответа под формат приложения.
3. Объектное хранилище:
   - MinIO как S3-compatible storage;
   - файл хранится в bucket;
   - в БД лежат только метаданные и object key;
   - скачивание через signed URL;
   - удаление удаляет объект и метаданные.

## Что говорить
> В 4 лабораторной я выполнил SEO-доработку приложения: добавил meta tags, canonical, Open Graph, structured data, robots.txt, sitemap.xml и 404. Также интегрировал внешний API для подбора источников через backend-адаптер с обработкой ошибок. Для файлов использовано S3-compatible объектное хранилище MinIO: файлы лежат в bucket, а клиент получает их по signed URL.

## Что показать
1. Главная страница и эталон.
2. `http://127.0.0.1:8080/robots.txt`.
3. `http://127.0.0.1:8080/sitemap.xml`.
4. На главной — блок подбора источников по теме.
5. В разделе проверки — загрузка файла.
6. В MinIO Console — объект в bucket.
7. В истории — скачать вложение.
8. Открыть несуществующий маршрут и показать 404.
