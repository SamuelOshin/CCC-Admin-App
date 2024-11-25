const CACHE_NAME = 'cccadmin-cache-v1';
const urlsToCache = [
  '/',
  '/static/assets/bootstrap/css/bootstrap.min.css',
  '/static/assets/css/styles.css',
  '/static/fontawesomefree/css/brands.css',
  '/static/fontawesomefree/css/fontawesome.css',
  '/static/assets/build/css/intlTelInput.css',
  '/static/assets/fonts/fontawesome-all.min.css',
  '/static/assets/css/animate.min.css',
  '/static/assets/css/stylesi.css',
  '/static/fontawesomefree/css/solid.css',
  '/static/assets/css/vanila-zoom.min.css',
  '/static/css/dataTables.bootstrap5.min.css',
  '/static/css/buttons.bootstrap5.min.css',
  '/static/assets/img/777899999.png',
  '/static/assets/img/hello.png',
  '/static/assets/img/flames.png',
  '/static/assets/js/dataTables.bootstrap5.min.js',
  '/static/assets/js/jquery.dataTables.min.js',
  '/static/assets/js/buttons.bootstrap4.min.js',
  '/static/assets/js/jquery-3.7.0.js',
  '/static/assets/js/dataTables.buttons.min.js',
  '/static/assets/js/bs-init.js',
  '/static/assets/js/number.js',
  '/static/assets/build/js/intlTelInputWithUtils.js',
  '/static/assets/bootstrap/js/bootstrap.min.js',
  '/static/assets/js/theme.js',
  '/static/assets/js/vanila-zoom.js',
  '/static/assets/fonts/fa-solid-900.woff2',
  '/static/fontawesomefree/webfonts/fa-solid-900.woff2',
  '/offline.html'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
      .catch(() => caches.match('/offline.html'))
  );
});

self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
