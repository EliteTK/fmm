FMM
===

FMM or Feed Me/My Mail is a small python application which is designed to read
a database of feeds, synchronise the feeds and then send an email for each new
feed to a specified email address using the specified information.

Configuration
-------------
### Basic
For the most basic setup of fmm, create a new section within the default
users.ini with the section name being your email address, an optional name
element inside the section name can be added (this does nothing at the moment).

Next set up the sender address in fmm.ini correctly and change your mail-server
to one you have set up. The application should be able to take correctly
formatted email via stdin and be able to infer the details from this data.
(e.g. msmtp -t)

Lastly, add some feeds to lists/default.feeds, this file should be a newline
separated list of feed urls to any feeds supported by feedparser.

### Advanced
For advanced configuration, create a list of users as above inside users.ini,
the name field is optional and you can override the feed list using the
feed-list variable, all variables in all initialisation files are inherited
from the internal defaults, and the defaults can be changed through a [DEFAULT]
section, these details then get passed on to any sections within the files.

After creating a list of users and specifying their feed lists, create the
corresponding feed lists in the locations specified. Feeds in feed lists should
be as before, a newline delimited list of URLs.

Next, set up any feed specific information in feedsettings.ini, here you can
specify the contents of the List-Id mail header through list-id, additionally
you can specify a different template, templates are basic Jinja2 templates, the
available variables are the same variables specified in the RSS 2.0
specification located at <http://www.rssboard.org/rss-specification>. If you
need feed specific settings, create a section with the url of the feed as the
section name, and override any settings within it.

Finally, set up fmm.ini as before.

Running
-------
Currently FMM needs to be ran periodically, but FMM will keep track of feed
items to ensure that no item is sent twice.
