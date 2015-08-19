"""
=================
flask-geckoboard
=================

Geckoboard_ is a hosted, real-time status board serving up indicators
from web analytics, CRM, support, infrastructure, project management,
sales, etc.  It can be connected to virtually any source of quantitative
data.  This Flask_ plugin provides view decorators to help create
custom widgets.

.. _Geckoboard: http://www.geckoboard.com/
.. _Flask: http://flask.pocoo.org/


Installation
============

To install flask-geckoboard, simply place the ``flask_geckoboard``
package somewhere on the Python path.


Limiting access
===============

If you want to protect the data you send to Geckoboard from access by
others, you can use an API key shared by Geckoboard and your widget
views.  Set ``GECKOBOARD_API_KEY`` in the Flask config.

If you do not set an API key, anyone will be able to view the data by
visiting the widget URL.


Encryption
==========

Geckoboard encryption allows encrypting data before it is sent to Geckoboard's
servers. After entering the password used to encrypt the data when the Geckoboard
is loaded, the data will be decrypted in the browser.

To use encryption, first set a ``GECKOBOARD_PASSWORD`` in the Flask config.

Next, enable encryption for each widget using the decorator arguments::

    from flask import Flask
    from flask_geckoboard import Geckoboard

    app = Flask(__name__)
    geckoboard = Geckoboard(app)

    @app.route('/user-count')
    @geckoboard.number(encrypted=True)
    def user_count(request):
        return User.objects.count()


Creating custom widgets
=======================

The available custom widgets are described in the Geckoboard support
section, under `Geckoboard API`_.  From the perspective of a Flask
project, a custom widget is just a view.  The flask-geckoboard
application provides view decorators that render the correct response
for the different widgets.

Let's say you want to add a widget to your dashboard that shows the
number of number of comments posted today.  First create a view, using a
flask-geckoboard decorator::

    from datetime import date, time, datetime

    from flask import Flask
    from flask_geckoboard import Geckoboard

    app = Flask(__name__)
    geckoboard = Geckoboard(app)

    @app.route('/comment-count')
    @geckoboard.number
    def comment_count():
        midnight = datetime.combine(date.today(), time.min)
        return Comment.objects.filter(submit_date__gte=midnight).count()


If your widget has optional settings, you can pass them in the decorator
definition::

    @app.route('/gecko/comment/count-absolute')
    @geckoboard.number(absolute='true')
    def comment_count(request):
        midnight = datetime.combine(date.today(), time.min)
        return Comment.objects.filter(submit_date__gte=midnight).count()


This is all the Flask code you need to display the comment count on
your dashboard. When you create a custom widget in Geckoboard, enter the
following information:

Encryption
    Enable if the field is encrypted (see instructions above).

URL data feed
    The view URL.  In the example above this would be something like
    ``http://HOSTNAME/geckoboard/comment_count/``.

API key
    The content of the ``GECKOBOARD_API_KEY`` setting, if you have set
    it.

Widget type
    *Custom*

Feed format
    Either *XML* or *JSON*.  If you don't specify a format the decorators will
    automatically detect and output the correct format or default to XML
    if this is not enabled (by default the format isn't appended by
    Geckoboard as a parameter any more)

Request type
    Either *GET* or *POST*.  The view decorators accept both.


The following decorators are available from the
``flask_geckoboard.decorators`` module:


``number``
-----------------

Render a *Number & Secondary Stat* widget.

The decorated view must return a tuple *(current, [previous],
[prefix])* where the *current* parameter is the current value, optional
*previous* parameter is the previous value of the measured quantity and
the optional parameter *prefix* is the prefix used in Geckoboard widget.
If there is only one parameter you do not need to return it in a tuple.
For example, to render a widget that shows the number of users and the
difference from last week::

    from datetime import datetime, timedelta

    @geckoboard.number
    def user_count(request):
        last_week = datetime.now() - timedelta(weeks=1)
        users = User.objects
        last_week_users = users.filter(date_joined__lt=last_week)
        return (users.count(), last_week_users.count())

    @geckoboard.number
    def users_count_with_prefix(request):
        last_week = datetime.now() - timedelta(weeks=1)
        users = User.objects
        last_week_users = users.filter(date_joined__lt=last_week)
        return (users.count(), last_week_users.count(), '$')


``rag``
--------------

Render a *RAG Column & Numbers* or *RAG Numbers* widget.

The decorated view must return a tuple with three tuples *(value,
[text])*.  The *value* parameters are the numbers shown in red, amber
and green (in that order).  The optional *text* parameters will be
displayed next to the respective values in the dashboard.

For example, to render a widget that shows the number of comments that
were approved or deleted by moderators in the last 24 hours::

    from datetime import datetime, timedelta

    @geckoboard.rag
    def comments(request):
        start_time = datetime.now() - timedelta(hours=24)
        comments = Comment.objects.filter(submit_date__gt=start_time)
        total_count = comments.count()
        approved_count = comments.filter(
                flags__flag=CommentFlag.MODERATOR_APPROVAL).count()
        deleted_count = Comment.objects.filter(
                flags__flag=CommentFlag.MODERATOR_DELETION).count()
        pending_count = total_count - approved_count - deleted_count
        return (
            (deleted_count, "Deleted comments"),
            (pending_count, "Pending comments"),
            (approved_count, "Approved comments"),
        )


``text``
---------------

Render a *Text* widget.

The decorated view must return a list of tuples *(message, [type])*.
The *message* parameters are strings that will be shown in the widget.
The *type* parameters are optional and tell Geckoboard how to annotate
the messages.  Use ``TEXT_INFO`` for informational messages,
``TEXT_WARN`` for for warnings and ``TEXT_NONE`` for plain text (the
default).  If there is only one plain message, you can just return it
without enclosing it in a list and tuple.

For example, to render a widget showing the latest Geckoboard twitter
updates, using Mike Verdone's `Twitter library`_::

    import twitter

    @geckoboard.text
    def twitter_status(request):
        twitter = twitter.Api()
        updates = twitter.GetUserTimeline('geckoboard')
        return [(u.text, TEXT_NONE) for u in updates]

.. _`Twitter library`: http://pypi.python.org/pypi/twitter


``pie_chart``
-------------

Render a *Pie chart* widget.

The decorated view must return an iterable over tuples *(value, label,
[color])*.  The optional *color* parameter is a string ``'RRGGBB[TT]'``
representing red, green, blue and optionally transparency.

For example, to render a widget showing the number of normal, staff and
superusers::

    @geckoboard.pie_chart
    def user_types(request):
        users = User.objects.filter(is_active=True)
        total_count = users.count()
        superuser_count = users.filter(is_superuser=True).count()
        staff_count = users.filter(is_staff=True,
                                   is_superuser=False).count()
        normal_count = total_count = superuser_count - staff_count
        return [
            (normal_count,    "Normal users", "ff8800"),
            (staff_count,     "Staff",        "00ff88"),
            (superuser_count, "Superusers",   "8800ff"),
        ]


``line_chart``
--------------

Render a *Line chart* widget.

The decorated view must return a tuple *(values, x_axis, y_axis,
[color])*.  The *values* parameter is a list of data points.  The
*x-axis* parameter is a label string or a list of strings, that will be
placed on the X-axis.  The *y-axis* parameter works similarly for the
Y-axis.  If there are more than one axis label, they are placed evenly
along the axis.  The optional *color* parameter is a string
``'RRGGBB[TT]'`` representing red, green, blue and optionally
transparency.

For example, to render a widget showing the number of comments per day
over the last four weeks (including today)::

    from datetime import date, timedelta

    @geckoboard.line_chart
    def comment_trend(request):
        since = date.today() - timedelta(days=29)
        days = dict((since + timedelta(days=d), 0)
                for d in range(0, 29))
        comments = Comment.objects.filter(submit_date__gte=since)
        for comment in comments:
            days[comment.submit_date.date()] += 1
        return (
            days.values(),
            [days[i] for i in range(0, 29, 7)],
            "Comments",
        )


``geck_o_meter``
----------------

Render a *Geck-O-Meter* widget.

The decorated view must return a tuple *(value, min, max)*.  The *value*
parameter represents the current value.  The *min* and *max* parameters
represent the minimum and maximum value respectively.  They are either a
value, or a tuple *(value, text)*.  If used, the *text* parameter will
be displayed next to the minimum or maximum value.

For example, to render a widget showing the number of users that have
logged in in the last 24 hours::

    from datetime import datetime, timedelta

    @geckoboard.geck_o_meter
    def login_count(request):
        since = datetime.now() - timedelta(hours=24)
        users = User.objects.filter(is_active=True)
        total_count = users.count()
        logged_in_count = users.filter(last_login__gt=since).count()
        return (logged_in_count, 0, total_count)


``funnel``
----------

Render a *Funnel* widget.

The decorated view must return a dictionary with at least an *items*
key.  To render a funnel showing the breakdown of authenticated users
vs. anonymous users::

    @geckoboard.funnel
    def user_breakdown(request):
        all_users = User.objects
        active_users =all_users.filter(is_active=True)
        staff_users = all_users.filter(is_staff=True)
        super_users = all_users.filter(is_superuser=True)
        return {
            "items": [
                (all_users.count(), 'All users'),
                (active_users.count(), 'Active users'),
                (staff_users.count(), 'Staff users'),
                (super_users.count(), 'Super users'),
            ],
            "type": "standard",   # default, 'reverse' changes direction
                                  # of the colors.
            "percentage": "show", # default, 'hide' hides the percentage
                                  # values.
            "sort": False,        # default, `True` orders the values
                                  # descending.
        }

``bullet``
----------

Render a *Bullet* widget.

The decorated view must return a dictionary with at least keys *label*,
*axis_points*, *current* and *comparative*. To render Geckoboard's own example
at
http://support.geckoboard.com/entries/274940-custom-chart-widget-type-definitions::

    @geckoboard.bullet
    def geckoboard_bullet_example(request):
        return = {
            'label': 'Revenue 2011 YTD',
            'axis_points': [0, 200, 400, 600, 800, 1000],
            'current': 500,
            'comparative': 600,
            'sublabel': 'U.S. $ in thousands',
            'red': [0, 400],
            'amber': [401, 700],
            'green': [701, 1000],
            'projected': [100, 900],
            'auto_scale': False,
        }

.. _`Geckoboard API`: http://geckoboard.zendesk.com/forums/207979-geckoboard-api
"""


class Geckoboard(object):
    import decorators
    app = None
    bullet = decorators.bullet
    funnel = decorators.funnel
    geck_o_meter = decorators.geck_o_meter
    leaderboard = decorators.leaderboard
    line_chart_legacy = decorators.line_chart_legacy
    line_chart = decorators.line_chart
    pie_chart = decorators.pie_chart
    text = decorators.text_widget
    rag = decorators.rag_widget
    number = decorators.number_widget

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.api_key = app.config.get('GECKOBOARD_API_KEY')
        self.password = app.config.get('GECKOBOARD_PASSWORD')
        self.app = app

__author__ = "Rob Eroh"
__email__ = "rob@eroh.me"
__version__ = "0.2.1"
__copyright__ = "Copyright (C) 2011-2014 Rob Eroh and others"
__license__ = "MIT License"
