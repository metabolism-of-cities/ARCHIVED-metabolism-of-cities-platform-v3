from django_cron import CronJobBase, Schedule
from django.urls import reverse
from datetime import date
import datetime
from django.utils import timezone

from .models import Topic, Category, Message, MessageRead, TaskForceMember, TopicForm, TaskForceMemberForm, TaskForceTicketForm, TaskForceTicket, TicketLog, TopicSubscription, TaskForceUnit, Project

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string

# We use this to manage which site this is
from django.contrib.sites.models import Site

# Because we need to break lines in the mail message variable
from django.template.defaultfilters import linebreaksbr
from django.contrib.auth.models import User

class Digest(CronJobBase):
    RUN_AT_TIMES = ['23:50']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'team.digest' # Unique code for logging purposes

    def do(self):

        recipients = User.objects.filter(is_staff=True, is_active=True)
        current_site = Site.objects.get_current()
        url = "https://" + current_site.domain

        start_time_daily = timezone.now() - datetime.timedelta(days=1)
        start_time_weekly = timezone.now() - datetime.timedelta(days=7)

        for recipient in recipients:

            today = timezone.now()
            day_of_the_week = today.weekday()
            if day_of_the_week == 4:
                # On Friday we send the weekly digest; rest of the days only the daily one
                subscriptions = TopicSubscription.objects.filter(user=recipient, type__in=['daily', 'weekly'])
            else:
                subscriptions = TopicSubscription.objects.filter(user=recipient, type__in=['daily'])

            for subscription in subscriptions:
                topic = subscription.topic
                if subscription.type == 'daily':
                    posts = Message.objects.filter(topic=topic, date__gte=start_time_daily)
                    type = 'daily'
                else:
                    posts = Message.objects.filter(topic=topic, date__gte=start_time_weekly)
                    type = 'weekly'
                
                if posts:
                    # We must check to see that this is not just a post by the user
                    # TODO We can see if this can be done more efficiently
                    send = False
                    for post in posts:
                        if post.author != recipient:
                            send = True

                    if send:
                        context = {
                            'url': url + '/intranet/topic/'+str(topic.id)+'/view',
                            'url_unsubscribe': url + '/intranet/topic/'+str(topic.id)+'/subscription/unsubscribe',
                            'url_weekly': url + '/intranet/topic/'+str(topic.id)+'/subscription/weekly',
                            'url_daily': url + '/intranet/topic/'+str(topic.id)+'/subscription/daily',
                            'url_instantly': url + '/intranet/topic/'+str(topic.id)+'/subscription/instantly',
                            'domain' : url,
                            'topic': topic.name,
                            'type': type,
                            'posts': posts,
                        }

                        msg_html = render_to_string('team/mail/digest.html', context)
                        msg_plain = render_to_string('team/mail/digest.txt', context)

                        recipientlist = [recipient.email]

                        send_mail(
                            topic.name + str(' - ') + type + str(' digest'),
                            msg_plain,
                            'automail@metabolismofcities.org',
                            recipientlist,
                            html_message=msg_html,
                        )


class ProgressReport(CronJobBase):
    RUN_AT_TIMES = ['23:50']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'team.progressreport' # Unique code for logging purposes

    def do(self):

        today = timezone.now()
        day_of_the_week = today.weekday()

        # Only send the report on Fridays
        if day_of_the_week == 4:

            one_week_ago = timezone.now() - datetime.timedelta(days=7)

            recipients = User.objects.filter(is_staff=True, is_active=True)
            current_site = Site.objects.get_current()
            url = "https://" + current_site.domain

            for recipient in recipients:

                taskforces = Category.objects.filter(members=recipient)
                membership = TaskForceMember.objects.filter(user=recipient)
                progress = TicketLog.objects.filter(ticket__taskforce__in=taskforces, title='Progress update', created_at__gte=one_week_ago).order_by('ticket__taskforce')
                completed = TicketLog.objects.filter(ticket__taskforce__in=taskforces, title='Status changed to: Completed', created_at__gte=one_week_ago).order_by('ticket__taskforce')
                context = { 'completed': completed, 'progress': progress, 'taskforces': membership, 'url': url }

                msg_html = render_to_string('team/mail/weeklyreport.html', context)
                msg_plain = render_to_string('team/mail/weeklyreport.txt', context)

                recipientlist = [recipient.email]

                send_mail(
                    'Weekly progress report from Metabolism of Cities',
                    msg_plain,
                    'automail@metabolismofcities.org',
                    recipientlist,
                    html_message=msg_html,
                )
