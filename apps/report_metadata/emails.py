from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

__author__ = "Alan Viars @ CDC"



def send_test_email():
    """Send test email."""
    subject = 'Subject'
    html_message = render_to_string('report_metadata/email-test.html', {'name': 'Foowee'})
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = settings.DEFAULT_FROM_EMAIL
    mail.send_mail(subject, plain_message, from_email, [to,], html_message=html_message)


def send_onboarding_request_received_to_approval_team(request_access):
    """Send email to approval team with a notice of new subbmited application."""
    context = {"request_access": request_access,}
    html_message = render_to_string('report_metadata/email-request-access-received-to-approval-team.html',
                                    context)
    plain_message = strip_tags(html_message)
    subject = """[%s] A new access request was received by %s %s""" % (
        settings.ORGANIZATION_NAME, request_access.first_name, request_access.last_name)    
    from_email = settings.DEFAULT_FROM_EMAIL
    to = settings.DEFAULT_ADMIN_EMAIL
    mail.send_mail(subject, plain_message, from_email, [to,], html_message=html_message)


def send_onboarding_request_received_to_applicant(request_access):
    """Send email to applicant that submission is being reviewed."""
    context = {"request_access": request_access,}   
    html_message = render_to_string('report_metadata/email-request-access-received-to-applicant.html',
                                    context)
    plain_message = strip_tags(html_message)
    subject = """[%s] Your access request has been received and is pending review.""" % (
        settings.ORGANIZATION_NAME)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [request_access.email,]
    mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)


def send_onboarding_request_approved_to_applicant(request_access):
    """Send email to applicant that submission is approved."""
    context = {"request_access": request_access,}   
    html_message = render_to_string('report_metadata/email-request-access-approved-to-applicant.html',
                                    context)
    plain_message = strip_tags(html_message)
    subject = """[%s] Your access request is approved""" % (
        settings.ORGANIZATION_NAME)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [request_access.email,]
    mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)

