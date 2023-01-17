- Should probably have a cache folder that holds compiled versions of files, or offer REDIS integration for that or something - Just in case someone accesses a version of a file a lot without putting it in the wiki.
- Need to implement the [delta thing](https://detools.readthedocs.io/en/latest/)
- Can probably use cherrypy for the web server. Looks like it'll cost about 2.5Mb?
- marko or python-markdown might be good for the web server's markdown interpreter?

# Content Ref ID

Might be a good idea to have every file generate a Content Ref ID? This could be stored in the edit_log as a third column. It would allow for finding the shortest path to rehydration, and it would allow for storage optimizations as well, and it would help with refid generation.

# Comment system

Need to detail this out for v1.2.
