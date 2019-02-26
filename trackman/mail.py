from datetime import datetime
from flask import current_app, render_template, url_for
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils
import smtplib
import ssl
from . import format_datetime


def get_smtp():
    s = smtplib.SMTP(current_app.config['SMTP_SERVER'],
                     current_app.config['SMTP_PORT'])
    if current_app.config['SMTP_TLS']:
        s.starttls(context=ssl.create_default_context())
    if len(current_app.config['SMTP_USER']) > 0:
        s.login(current_app.config['SMTP_USER'],
                current_app.config['SMTP_PASSWORD'])
    return s


def send_logout_reminder(dj):
    msg = MIMEText(render_template('email/logout_reminder.txt',
                                   dj=dj))
    msg['Date'] = email.utils.formatdate()
    msg['From'] = current_app.config['MAIL_FROM']
    msg['To'] = dj.email
    msg['Message-Id'] = email.utils.make_msgid()
    msg['X-Mailer'] = "Trackman"
    msg['Subject'] = "[{name}] Logout Reminder".format(
        name=current_app.config['TRACKMAN_NAME'])

    s = get_smtp()
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()


def send_playlist(djset, tracks):
    msg = MIMEMultipart('alternative')
    msg['Date'] = email.utils.formatdate()
    msg['From'] = current_app.config['MAIL_FROM']
    msg['To'] = djset.dj.email
    msg['Message-Id'] = email.utils.make_msgid()
    msg['X-Mailer'] = "Trackman"
    msg['Subject'] = "[{name}] {djname} - Playlist from {dtend}".format(
        name=current_app.config['TRACKMAN_NAME'],
        djname=djset.dj.airname,
        dtend=format_datetime(djset.dtend, "%Y-%m-%d"))

    msg.attach(MIMEText(
        render_template('email/playlist.txt',
                        djset=djset, tracks=tracks),
        'plain'))
    msg.attach(MIMEText(
        render_template('email/playlist.html',
                        djset=djset, tracks=tracks),
        'html'))

    s = get_smtp()
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()


def send_chart(chart):
    msg = MIMEMultipart('alternative')
    msg['Date'] = email.utils.formatdate()
    msg['From'] = current_app.config['MAIL_FROM']
    msg['To'] = current_app.config['CHART_MAIL_DEST']
    msg['Message-Id'] = email.utils.make_msgid()
    msg['X-Mailer'] = "Trackman"
    timestamp = datetime.utcnow()
    msg['Subject'] = "[{name}] New Music Chart {timestamp}".format(
        name=current_app.config['TRACKMAN_NAME'],
        timestamp=format_datetime(timestamp, "%Y-%m-%d"))

    msg.attach(MIMEText(
        render_template('email/new_chart.txt',
                        chart=chart, timestamp=timestamp),
        'plain'))

    s = get_smtp()
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()


def send_claim_email(claim_token, remote_addr):
    msg = MIMEMultipart('alternative')
    msg['Date'] = email.utils.formatdate()
    msg['From'] = current_app.config['MAIL_FROM']
    msg['To'] = claim_token.dj.email
    msg['Message-Id'] = email.utils.make_msgid()
    msg['X-Mailer'] = "Trackman"
    msg['Subject'] = "[{name}] DJ claim confirmation".format(
        name=current_app.config['TRACKMAN_NAME'])

    msg.attach(MIMEText(
        render_template(
            'email/claim_dj.txt',
            claim_token=claim_token,
            confirm_url=url_for('.confirm_claim',
                                id=claim_token.id,
                                token=claim_token.token,
                                _external=True),
            remote_addr=remote_addr),
        'plain'))
    try:
        s = get_smtp()
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()
    except Exception as exc:
        current_app.logger.warning(
            "Trackman: Sent DJ claim email - {0}".format(exc))
