## Short Version

Any page you go to on the web server can be seen as a json object by just changing the `/w/` to `/api/`.

## Public API

Anything listed here promises to stay the same until the next major update.

### /api/titles/

Lists all the titles on the server

### /api/articles/

Lists all the articles on the server. Very messy, use cautiously.

### /api/:label/

If you have the label of an article (name of it or id of it), then you can access it directly.

## Private API

Anything listed here is for internal use by linki, and might change in any version. Use with caution.

### /api/me/

If you're authenticated, this returns your profile on the server.

### /api/contribute/

If you're authenticated, this lets you send a contribution in the form of a MessagePack.

### /copy/<titles|articles|:label>

As `/api/` but it returns a MessagePack instead of a json object.
