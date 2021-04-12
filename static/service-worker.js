// Cached files declaration
const CACHE_NAME = 'wise-nose-cache';

const FILES_TO_CACHE = [
  '/static/offline.html',
];

self.addEventListener('install', (evt) => {
    console.log('[ServiceWorker] Install');
    evt.waitUntil(
      caches.open(CACHE_NAME).then((cache) => {
        console.log('[ServiceWorker] Pre-caching offline page');
        return cache.addAll(FILES_TO_CACHE);
      })
    );
  
    self.skipWaiting();
});

self.addEventListener('activate', (evt) => {
    console.log('[ServiceWorker] Activate');
    evt.waitUntil(
      caches.keys().then((keyList) => {
        return Promise.all(keyList.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing old cache', key);
            return caches.delete(key);
          }
        }));
      })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (evt) => {
    if (evt.request.mode !== 'navigate') {
      return;
    }
    evt.respondWith(fetch(evt.request).catch(() => {
        return caches.open(CACHE_NAME).then((cache) => {
          return cache.match(FILES_TO_CACHE[0]);
        });
      })
    );
  });

// TODO test and check
/*
self.addEventListener('sync', (event) => {
  if (event.tag === 'create-session') {
    event.waitUntil(
      getMessagesFromOutbox().then(messages => {

      }
        // Post the messages to the server
        return fetch('/create-session', {
          method: 'POST',
          body: JSON.stringify(messages),
          headers: { 'Content-Type': 'application/json' }
        }).then(() => {

          // Success! Remove them from the outbox
          return removeMessagesFromOutbox(messages);
        });

      }).then(() => {

        // Tell pages of your success so they can update UI
        return clients.matchAll({ includeUncontrolled: true });
      }).then(clients => {
        clients.forEach(client => client.postMessage('outbox-processed'))
      })
    }
});*/
