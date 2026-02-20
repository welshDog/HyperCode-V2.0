// Hyperfocus Support Service Worker (scoped to /support)
const CACHE_NAME = 'hyperfocus-support-v1.3';
const urlsToCache = [
  'index.html',
  'css/styles.css',
  'js/main.js',
  'manifest.json',
  'assets/favicon.ico',
  'assets/icon-192x192.png',
  'assets/icon-512x512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => Promise.all(
      cacheNames.map((cacheName) => { if (cacheName !== CACHE_NAME) return caches.delete(cacheName); })
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) return response;
      return fetch(event.request).then((net) => {
        if (!net || net.status !== 200 || net.type !== 'basic') return net;
        const copy = net.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return net;
      }).catch(() => {
        if (event.request.destination === 'document') return caches.match('index.html');
        return Promise.reject();
      });
    })
  );
});

self.addEventListener('message', (event) => { if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting(); });
self.addEventListener('message', (event) => { if (event.data && event.data.type === 'CHECK_UPDATE') self.registration.update(); });
console.log('🚀 Hyperfocus Support Service Worker loaded (local scope)');
