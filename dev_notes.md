# TODO Transfer Stuff

clone <uri>
: Copy an existing repository.

Starting the sprint with this, and focusing on http implementation first using webpy

Test should make a repo, then have it serve and prepare for cloning, and then the new repo should have all the content of the original repo. Just checking that the expected folder structure is there should be fine. Also check for same file sizes. Unless assert has a way to check that files are the same.

copy <uri>
: Copy an edit from another repository.

# Web interface

Actually, making this high priority. Next feature. Its important to actually reflecting the _goal_ of this project. Hosting and displaying the wiki is just as important as the rest of it. People won't host if it isn't easy and it needs to be able to host itself and integrate to cgi servers well.

Use webpy and pypandoc to make the display interface. Allow in-browser editing if its markdown and localhost.
https://pypi.org/project/pypandoc/
https://webpy.org/

serve <port>
: Serve a simple web version of the wiki.

# Pandoc magic

Important for the web interface

Maybe allow any type of file that pandoc supports, and have some magic that automatically converts them to your preferred format, then convert them back before turning them into objects? That way the original author has what they're familiar with seeing in case pandoc would do something weird to the original file. Either that or have pandoc convert it to some kind of good storage format.

Pandoc should convert all incoming data to markdown to improve diffing, storage, and compression. Let output be configured somehow so people can get docx or whatever they want out for editing on top of, but plaintext is easiest to store.

# Remote

remote publish <uri>
: update any or all remote with your version of the wiki. (Copies over articles and deltas, sets remotes' articles)

remote add <uri>
: add a remote url to push to (cloning automatically does this)

remote del <uri>
: remote the indicated remote

## Considerations

hg does not implement any actual remote and leaves that to the user to script or something. I don't think I like that approach. I kind of like git's approach, but I want something similar to noosphere's concept of an address book and I want to have something reminiscent of following on Tumblr. The primary goal of this is to be able to build a wiki with multiple distributions editing their own distribution and others copying over stuff they like. Whats the concept of a remote here for? Is it just for easily syncing to another distribution that you control? Is that a good feature?

### Submit <refid> <uri>

Send a diff to the uri if they have submissions open, and they can choose whether or not to accept it. Accepting it can apply it to the source it was edited from, or it can (if compatible) apply to the latest article. Some kind of bib-like sourcing or something will have to be done to make this work.

# Content Ref ID

Might be a good idea to have every file generate a Content Ref ID? This could be stored in the edit_log as a third column. It would allow for finding the shortest path to rehydration, and it would allow for storage optimizations as well, and it would help with refid generation.

# Shared rationing on Rough Drafts

If a user copies an edit, they take on part of the size of the edit or file. The more people using it, the less it costs from their data budget. This will be possible cause Rough Drafts will have a global edits folder that repos hard link to.

# Comment system

Need to detail this out for v0.3.

# Random Thoughts

- Should probably have a cache folder that holds compiled versions of files, or offer REDIS integration for that or something - Just in case someone accesses a version of a file a lot without putting it in the wiki.

- Should Rough Drafts do some kind of data poisoning implementation? https://arxiv.org/pdf/2302.10149.pdf
