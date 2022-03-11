from google.appengine.api import wrap_wsgi_app
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
import re
import http

# This datastore model keeps track of which users uploaded which photos.
class UserPhoto(ndb.Model):
    user = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()

class UploadFormHandler:
  def __call__(self, environ, start_response):
    upload_url = blobstore.create_upload_url('/upload_photo')

    response = """
              <html><body>
              <form action="{0}" method="POST" enctype="multipart/form-data">
                Upload File: <input type="file" name="file"><br>
                <input type="submit" name="submit" value="Submit">
              </form>
              </body></html>""".format(upload_url)
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [response.encode('utf-8')]

class UploadPhotoHandler(blobstore.BlobstoreUploadHandler):
  """Upload handler called by blobstore when a blob is uploaded in the test."""
  def post(self, environ):
    upload = self.get_uploads(environ)[0]
    user_photo = UserPhoto(
        user=users.get_current_user().user_id(),
        blob_key=upload.key())
    user_photo.put()

    # Redirect to the '/view_photo/<Photo Key>' URL
    return "", http.HTTPStatus.FOUND, [('Location', '/view_photo/%s' % upload.key())]

class ViewPhotoHandler(blobstore.BlobstoreDownloadHandler):
  def get_photo(self, environ, photo_key):
    if not blobstore.get(photo_key):
      return "Photo key not found", http.HTTPStatus.NOT_FOUND, []
    else:
      return "", http.HTTPStatus.OK, list(self.send_blob(environ, photo_key).items())

  def get(self, environ):
    photo_key = (environ['app.url_args'])[0]
    return self.get_photo(environ, photo_key)


# map urls to functions
urls = [
    (r'^$', UploadFormHandler),
    (r'upload_photo/?$', UploadPhotoHandler),
    (r'view_photo/(.+)$', ViewPhotoHandler)
]

class Application(object):
    def __init__(self, routes):
        self.routes = routes

    def not_found(self, environ, start_response):
      start_response('404 Not Found', [('Content-Type', 'text/plain')])
      return ['404 Not Found']

    def __call__(self, environ, start_response):
      path = environ.get('PATH_INFO', '').lstrip('/')
      print(environ)
      for regex, handler in self.routes:
        match = re.search(regex, path)
        if match is not None:
          environ['app.url_args'] = match.groups()
          print("match.groups for %s: " % match, match.groups())
          callback = handler()  # instantiate the handler class
          return callback(environ, start_response)
      return self.not_found(environ, start_response)

app = wrap_wsgi_app(Application(urls))