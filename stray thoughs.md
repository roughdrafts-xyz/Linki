- Should probably have a cache folder that holds compiled versions of files, or offer REDIS integration for that or something - Just in case someone accesses a version of a file a lot without putting it in the wiki.
- Can probably use cherrypy for the web server. Looks like it'll cost about 2.5Mb?
- marko or python-markdown might be good for the web server's markdown interpreter?

# TODO Web Stuff

copy <uri>
: Copy an edit from another repository.

clone <uri>
: Copy an existing repository.

# Content Ref ID

Might be a good idea to have every file generate a Content Ref ID? This could be stored in the edit_log as a third column. It would allow for finding the shortest path to rehydration, and it would allow for storage optimizations as well, and it would help with refid generation.

# Shared rationing on Rough Drafts

If a user copies an edit, they take on part of the size of the edit or file. The more people using it, the less it costs from their data budget. This will be possible cause Rough Drafts will have a global edits folder that repos hard link to.

# Comment system

Need to detail this out for v1.2.

# Web interface

Use webpy and pypandoc to make the display interface. Allow in-browser editing if its markdown?
https://pypi.org/project/pypandoc/
https://webpy.org/

serve <port>
: Serve a simple web version of the wiki.

# Pandoc magic

Maybe allow any type of file that pandoc supports, and have some magic that automatically converts them to your preferred format, then convert them back before turning them into objects? That way the original author has what they're familiar with seeing in case pandoc would do something weird to the original file. Either that or have pandoc convert it to some kind of good storage format.

# Submit <refid> <uri>

Send a diff to the uri if they have submissions open, and they can choose whether or not to accept it. Accepting it can apply it to the source it was edited from, or it can (if compatible) apply to the latest article. Some kind of bib-like sourcing or something will have to be done to make this work.
