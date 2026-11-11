const CACHE = 'blue-uni-v1';
const FILES = ['/', '/static/manifest.json', '/static/logo_blue.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener('fetch', e => { e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).catch(()=>caches.match('/')))); });
