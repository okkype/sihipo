var staticCacheName = 'sihipo-pwa-v1';

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(staticCacheName).then(function(cache) {
      return cache.addAll([
        '/',
        '/login/',
        '/manifest.json',
        '/static/img/hipo-icon.png',
        '/static/img/hipo-icon-2.png',
        '/static/style.css',
        '/static/sb-admin-2/vendor/bootstrap/css/bootstrap.min.css',
        '/static/sb-admin-2/vendor/metisMenu/metisMenu.min.css',
        '/static/sb-admin-2/vendor/datatables-plugins/dataTables.bootstrap.css',
        '/static/sb-admin-2/vendor/datatables-responsive/dataTables.responsive.css',
        '/static/sb-admin-2/dist/css/sb-admin-2.css',
        '/static/sb-admin-2/vendor/font-awesome/css/font-awesome.min.css',
        '/static/sb-admin-2/vendor/bootstrap-datetimepicker/css/bootstrap-datetimepicker.min.css',
        '/static/codemirror/lib/codemirror.css',
        '/static/js/pace.min.js',
        '/static/sb-admin-2/vendor/jquery/jquery.min.js',
        '/static/sb-admin-2/vendor/bootstrap/js/bootstrap.min.js',
        '/static/sb-admin-2/vendor/momentjs/moment.js',
        '/static/sb-admin-2/vendor/bootstrap-datetimepicker/js/bootstrap-datetimepicker.min.js',
        '/static/sb-admin-2/vendor/metisMenu/metisMenu.min.js',
        '/static/sb-admin-2/vendor/datatables/js/jquery.dataTables.min.js',
        '/static/sb-admin-2/vendor/datatables-plugins/dataTables.bootstrap.min.js',
        '/static/sb-admin-2/vendor/datatables-responsive/dataTables.responsive.js',
        '/static/sb-admin-2/dist/js/sb-admin-2.js',
        '/static/codemirror/lib/codemirror.js',
        '/static/codemirror/mode/python/python.js',
        '/static/codemirror/addon/selection/active-line.js',
        '/static/codemirror/addon/edit/matchbrackets.js'
      ]);
    })
  );
});

self.addEventListener('fetch', function(event) {
  var requestUrl = new URL(event.request.url);
    if (requestUrl.origin === location.origin) {
      if ((requestUrl.pathname === '/')) {
        event.respondWith(caches.match('/'));
        return;
      }
    }
    event.respondWith(
      caches.match(event.request).then(function(response) {
        return response || fetch(event.request);
      })
    );
});