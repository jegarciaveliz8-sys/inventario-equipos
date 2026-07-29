const CACHE_NAME = 'inventario-v1';
const urlsToCache = [
  '/',
  '/escanear-qr/',
  '/buscar/',
  '/reportes/equipos/'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
