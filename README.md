# Linki

The Command Line Client for the linki project - A tool to create distributed wikis. You can use this to publish a new wiki or copy an existing one. You can also use it to manage your wiki.

# What's a Distributed Wiki?

A distributed wiki means that it is easy to make a copy of it in another location that is yours to edit. It also means it is easy to share parts of it with others - they can copy individual edits and articles to their wiki (or wikis.) This lets people work on edits to the wiki in a way similar to the "production" version of the wiki, without needing to edit it directly.

## Why would I want to use this?

There are a lot more reasons why you'd want to use a distributed wiki than just preventing hasty, embarrassing edits.

### Data Replication

Let's say you're making a wiki focused on something that might not be a host's favorite thing. You don't need to worry about it being deleted, and you don't need to worry about the hassle of setting it back up. You have a copy locally. Everyone who edits it has a copy as well. You'll be able to find a new host and get up and running as fast as possible. If something happens to you and your wiki at the same time, someone else can get a copy running quickly as well.

### Inconsistent Internet

Let's say you have unreliable internet. It's a satellite connection, or it's cheaper to use at night than during the day where you live, or something like that. Point is, you don't have 24/7 internet access. Good news - You have a whole copy of the wiki on your person. In your phone, on a flash drive, whatever. You don't need the internet to edit it. You don't need the internet or a server to share it locally either.

### Copying Off Another Wiki

Let's say you're interested in bird watching, and you find a great bird wiki using linki. You run into an issue - their articles on birds local to you aren't anywhere near the quality of the rest of their articles. You feel a duty to improve on what they started. You have the power to copy those articles and edit on top of them, keeping attributions and history for all of them. You're not limited to individual articles either. You can copy whole groups or even the entire wiki.

# Installation

We're on PyPI! You can just run `pip install linki` and continue.  
Alternatively, download a release from [the releases](#installation).

# Getting Started

You can get started by running `linki init` to start your own wiki. The initialization procedure should have created a folder that we'll be calling this folder the `working directory`. This is where your wiki will live.

The working directory should have a hidden folder in it called `.linki`. Don't touch this. Its for linki to handle, and its a sensitive folder.

## Terminology

### Titles

linki puts documents known as "Titles" on display. Named after the fact that they're content associated with a title. Titles are Articles, under the hood. They're just special because they're what's on display. Other Articles are considered to be history.

### Articles

Articles are an archive of all changes to a Title whether or not that Title is on display. When you do commands to a title, you're actually doing a command to an Article. Anything that works on an Article should work on a Title. This may not always be the case the other way around.

### Drafts

Drafts are your works in progress. They aren't titles and they aren't articles. When you're using the command line application they're the files in your working directory. You can `publish` drafts so that they become Titles and get archived as Articles.

# Writing your Drafts

Writing Drafts is pretty easy - just use markdown in any text editor you prefer. As long as it can save to markdown directly, you're golden. (Future versions will support anything [Pandoc](https://pandoc.org/) can!)

If a Draft is inside of a folder, it'll remember that - When you get to publishing it'll save the folder structure as part of the Title.You can edit your drafts like you would normal files. Move folders around. Rename things. linki will know what you changed when you ask it to publish your drafts.

# Publishing Drafts

When you're ready to turn your Drafts into Titles and archive them as Articles, run `linki publish`. When a reader interacts with your wiki, they'll see those Titles. If something goes wrong while you're publishing don't fret - it'll roll back the publishing and your wiki will be safe.

# Copying Articles from Other Wikis

See something you like on another wiki? Maybe a version of an article you wrote that you like better? Or an article you think would be important on your wiki that you don't have? You can copy it! You can copy it _and_ its history! When this thing has comments, it'll copy the comments too! Just run `linki copy <url of article>` and it'll copy all of that over to your wiki, ready to go. You can treat it like one of your own articles - edit its draft, change its groups, whatever. It's yours to change now.

Your wiki will only update Drafts you haven't changed. This will let you copy an article and change the title without changing the draft. You might need to do a bit of effort to add your draft's changes to the article, but this avoids what is known as an "[edit conflict](https://en.wikipedia.org/wiki/Edit_conflict)".

## Copying a wiki

If you want to, you can even copy a whole wiki. Just do `linki copy <url to wiki>` and it'll work the same - think of it as running copy on every article in the wiki.

### Filtering

When you copy an entire wiki you can use the `--filter` flag to filter titles using regex. This will let you only download specific file types, or only Titles that share parts of their label.

## Starting with a copy of a Wiki

Instead of running `linki init` you can use `linki copy`. This will automatically initialize the folder, and then run the copy command like normal for you. It's a great way to get up and running with a pre-made set of articles you want to build on top of.

# Subscribing to Wikis

There are likely wikis that you'd like to copy from consistently. This might be a copy of your wiki deployed to a server, or a wiki that covers a topic very related to your own. You can use `linki subscribe <url>` to do this.

If you subscribe to the same url multiple times, it'll unsubscribe from the wiki and then subscribe again. This is a good way to change settings on a subscription.

## Reading your Subscriptions

When you subscribe to a wiki, linki will show you to updates to wikis with `linki inbox`. If the same title has changed multiple times, it'll batch these changes together so that you only see the latest one. You can pick and choose which ones you'd like to copy over using the `linki copy` command.

Just like `linki copy` you can subscribe to a whole wiki, a group in that wiki, or just an individual page. It'll subscribe accordingly. You can subscribe to the same wiki multiple times, using different urls. This is useful if you want different subscriptions to the same wiki to have different settings.

## Automatic Subscriptions

You can set a subscription to be automatic with the `--automatic` flag. If a subscription is set to automatic, it will copy every update it sees after informing you of the changes. This is useful for making a replication of a wiki you work on.

You can stop a subscription from being automatic by subscribing again with the `--not-automatic` flag.

## Subscribing to Multiple Wikis

You can subscribe to multiple wikis. You do this by using `linki subscribe` any number of times. If you aren't subscribed to the wiki already, it'll add it to your list of subscriptions.

### Subscription priority

It's likely some of the wikis you subscribe to will have similar articles with the same title. Because of this, linki subscriptions have priority.

Automatic subscriptions will copy updates from all automatic subscriptions. Priority determines which article becomes the title article.

You can view your existing subscriptions and their priorities with `linki subscriptions` with no parameters. This will show you both your automatic and non-automatic subscriptions. It will also show you your wiki, labeled as `This Wiki`. Your Wiki defaults to having the highest priority.

A new subscription has the lowest priority until you change it. You can also set the priority when you run `linki subscribe` with `linki subscribe <url> [priority]`. You can also use this format to change the priority of an existing subscription. Your Wiki's url is `this`.

# Making your wiki public

`linki serve` will provide you with a ready-to-go web server that can display all your titles and articles. Your drafts will stay private, they're called drafts for a reason. It'll run up a web server with a basic wiki interface that displays your titles. You can use `linki serve --home=<title>` to set a title as a home page. If you do not, it will display a list of your ungrouped groups and titles.

This also makes your wiki public for other linki installations to subscribe to! It'll also create an API to access your titles and articles. You can read more about the API options in the [API Documentation](#).

## I don't want to have some of these features

Use `linki serve --no-web` to only serve your API and Subscription access. You can also do `linki serve --no-api` to turn off the API. Similarly you can do `linki serve --no-subscribe`. You can do any mix of these, but if you do all three it might just be better not to serve in the first place.

The linki Server comes with a basic search function, html displays of your articles, a history view of your titles, title lists, an API, and an endpoint for subscribers to update from.

## I don't want to host this on my personal computer

Smart! You can run `linki serve` on a server, and this is the recommended option.

## I don't want to maintain a server

Find a public linki host that will serve your wiki for you. They'll likely have advanced tools to help you, such as user groups or multi-author wiki tools. They'll likely also offer you search and discovery tools too.

# Contributing to other wikis

You can contribute to other wikis, and they might like to know when you're making a contribution to them. You can do this with the `linki announce` function. The `linki announce` function tells wikis that you've made some updates they should copy over. You can track which wikis receive announcements using the `linki contribute` command. It operates similarly to the `linki subscribe` command. Similarly, you can see who you're contributing to with the `linki contributions` command.

# Questions

These are questions I either asked myself or that someone asked me while discussing this concept.

## Why should I use this instead of git

Git isn't very oriented toward non-developers, and its purpose is different. Existing wiki solutions built on top of git are great, but they are not purpose-built.

For example, a linki hosting service (like [roughdrafts.xyz](#)) could provide permissions on who can read what articles by article, group, or wiki. It could also introduce something like pull requests for articles. (By the way, [roughdrafts.xyz](#)) does this today. Check it out!)

## How do I prevent plagiarism?

If you use a linki hosting service it might be able to act as a Timestamp Authority. If this is the case, anyone who trusts that host can use it to verify who published something first and you can use it to store copies of the verification.

You could also use this [pre-publish hook](#) to digitally timestamp your articles using the [FreeTSA Timestamp Authority service](https://www.freetsa.org/index_en.php) and [Sigstore TSA](https://www.sigstore.dev/).

Outside of using a Timestamp authority the best you can do is digitally sign something to say that it was written by you. This does not prevent someone from copying the text and signing it themselves. You can encrypt your articles and develop a web of trust, sharing your public keys with those you want to read your articles.

If you want to do that you can use this [pre-publish hook](#) to automatically digitally sign everything you publish. If you're subscribed to a signed wiki you can run a [post-copy hook](#) that verifies the entries automatically. If you'd like to encrypt and decrypt as well you can use [this set of hooks](#) to do that.

In addition to all of this, Articles identify themselves based on the articles they have been edited from. If you can find a public record of an article's history you can verify the authenticity of its identifier by comparing it against that.

## How do I delete something?

Assume anything you publish is out there forever. You can send out a blank update, but you can't guarantee people will copy it. Some clients might be able to receive that or another special signal as a request to delete an entire article's history manually.

For data integrity reasons, there's no built-in way to request the deletion of an article's history, as it might break an edit history tree.

If being able to delete your articles is a concern, develop a personal [web of trust](https://en.wikipedia.org/wiki/Web_of_trust), encrypt your articles using a secret key made just for linki, and use another communication channel to request your public key be deleted when you need to make your data inaccessible.

# Thanks

Thank You, Ward Cunningham, for sharing the [concept of a Federated Wiki](https://www.youtube.com/watch?v=BdwLczSgvcc) at TEDx and laying the ground work necessary to build off of.
