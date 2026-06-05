import json
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.utils.html import escape
from django.views.decorators.http import require_POST

from .models import ContactMessage, TestimonialSubmission


def build_notification_email(title, subtitle, fields, message_label, message):
    field_rows = ''.join(
        (
            '<tr>'
            '<td style="padding: 14px 0; border-bottom: 1px solid #eeeeee;">'
            f'<div style="font-size: 11px; letter-spacing: 1.8px; text-transform: uppercase; color: #777777; font-weight: 700;">{escape(label)}</div>'
            f'<div style="font-size: 17px; line-height: 1.5; color: #111111; font-weight: 700; margin-top: 4px;">{escape(value)}</div>'
            '</td>'
            '</tr>'
        )
        for label, value in fields
    )

    html_message = f"""
    <!doctype html>
    <html>
    <body style="margin: 0; padding: 0; background: #f4f4f4; font-family: Arial, Helvetica, sans-serif;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: #f4f4f4; padding: 36px 16px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width: 640px; background: #ffffff; border-radius: 24px; overflow: hidden; border: 1px solid #e8e8e8;">
                        <tr>
                            <td style="background: #050505; padding: 34px 34px 30px;">
                                <div style="display: inline-block; width: 44px; height: 44px; line-height: 44px; text-align: center; border-radius: 50%; background: #ffffff; color: #050505; font-size: 20px; font-weight: 900; margin-bottom: 22px;">R</div>
                                <div style="font-size: 12px; letter-spacing: 2.5px; text-transform: uppercase; color: #bdbdbd; font-weight: 700;">Rohan Oza Portfolio</div>
                                <h1 style="margin: 10px 0 0; color: #ffffff; font-size: 34px; line-height: 1.1; font-weight: 900;">{escape(title)}</h1>
                                <p style="margin: 14px 0 0; color: #d7d7d7; font-size: 16px; line-height: 1.6;">{escape(subtitle)}</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 30px 34px 8px;">
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                    {field_rows}
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px 34px 34px;">
                                <div style="font-size: 11px; letter-spacing: 1.8px; text-transform: uppercase; color: #777777; font-weight: 700;">{escape(message_label)}</div>
                                <div style="margin-top: 10px; padding: 20px; border-radius: 18px; background: #0d0d0d; color: #ffffff; font-size: 16px; line-height: 1.7; white-space: pre-wrap;">{escape(message)}</div>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px 34px 30px; border-top: 1px solid #eeeeee; color: #777777; font-size: 13px; line-height: 1.5;">
                                This email was sent automatically from your portfolio website.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    plain_message = '\n'.join(
        [title, subtitle, '']
        + [f'{label}: {value}' for label, value in fields]
        + ['', f'{message_label}:', message]
    )

    return plain_message, html_message


def send_notification_email(subject, message, html_message=None):
    recipient = getattr(settings, 'CONTACT_NOTIFICATION_EMAIL', '')
    sender = getattr(settings, 'DEFAULT_FROM_EMAIL', '')
    if not recipient or not sender:
        return False

    try:
        sent_count = send_mail(
            subject,
            message,
            sender,
            [recipient],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception:
        return False

    return sent_count > 0


def send_telegram_message(message):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        return False

    payload = urllib.parse.urlencode({
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
    }).encode()

    request = urllib.request.Request(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data=payload,
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def get_post_value(request, key):
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            data = {}
        return str(data.get(key, '')).strip()

    return request.POST.get(key, '').strip()


def portfolio(request):
    context = {
        'profile': {
            'name': 'Rohan Oza',
            'title': 'UI/UX Developer',
            'tagline': 'A fresher UI/UX designer with strong design fundamentals, good learning ability, and a passion for creating clean, user-friendly digital experiences.',
            'bio': 'I build high-performance, visually stunning web applications with cutting-edge technologies. Passionate about clean code, modern aesthetics, and seamless user experiences.',
            'email': 'rohan@example.com',
            'phone': '+91 98765 43210',
            'location': 'Mumbai, India',
            'resume_url': '#',
            'github': 'https://github.com/Rohanoza001',
            'linkedin': 'https://www.linkedin.com/in/rohan-oza/',
            'twitter': 'https://x.com/home'
        },
        'skills': [
            {
                'category': 'Frontend Foundations',
                'items': [
                    {'name': 'HTML', 'level': 95},
                    {'name': 'CSS', 'level': 92},
                    {'name': 'JavaScript', 'level': 85},
                    {'name': 'Responsive Design', 'level': 90},
                ]
            },
            {
                'category': 'Design Tools',
                'items': [
                    {'name': 'Figma', 'level': 92},
                    {'name': 'Photoshop', 'level': 82},
                    {'name': 'Stitch', 'level': 78},
                    {'name': 'Wireframing', 'level': 88},
                ]
            },
            {
                'category': 'Workflow',
                'items': [
                    {'name': 'GitHub', 'level': 86},
                    {'name': 'Prototyping', 'level': 88},
                    {'name': 'User Research', 'level': 80},
                    {'name': 'Design Systems', 'level': 84},
                ]
            }
        ],
        'projects': [
            {
                'title': 'IRCTC Case Study',
                'desc': 'A UX case study focused on improving the train booking journey with clearer navigation, smoother search flow, and more usable booking interactions.',
                'tech': ['UX Research', 'Wireframing', 'Figma', 'Prototyping'],
                'image': static('images/irctc-case-study.png'),
                'live_url': 'https://www.figma.com/design/BvY0xHE1jEa8wBJOf32AN5/Case-Study--IRCTC-?t=4VMCM0q2sYq6dp2X-0',
                'github_url': ''
            },
            {
                'title': 'Nike Case Study',
                'desc': 'A product experience case study exploring a modern Nike shopping flow, visual hierarchy, product discovery, and conversion-focused UI decisions.',
                'tech': ['UI Design', 'User Flow', 'Figma', 'Design System'],
                'image': static('images/nike-case-study.png'),
                'live_url': 'https://www.figma.com/design/YnoxHNZAMnG8c9cWTHUx47/Case-Study--Nike-?node-id=34-6&p=f&t=4VMCM0q2sYq6dp2X-0',
                'github_url': ''
            }
        ],
        'experiences': [
            {
                'role': 'Real Estate Agent',
                'company': 'MN Real Estate',
                'period': 'Dec 2025 - Present',
                'desc': 'Working with clients on property discovery, site visits, lead follow-ups, and real estate sales support while helping buyers find suitable property options.'
            },
            {
                'role': 'Data Analyst',
                'company': 'Rezide Solution',
                'period': 'Dec 2023 - Apr 2025',
                'desc': 'Worked on database management systems, organizing and maintaining structured data while supporting analysis, reporting, and smooth operational workflows.'
            },
            {
                'role': 'Flutter Developer',
                'company': 'Patel Brothers Services & Engineering Pvt. Ltd.',
                'period': 'May 2024 - Jul 2024',
                'desc': 'Developed and maintained mobile application interfaces with a focus on user-friendly screens, Firebase integration, and reliable app functionality.'
            },
            {
                'role': 'Sales And Marketing Intern',
                'company': 'Patel Brothers Services & Engineering Pvt. Ltd.',
                'period': 'Jul 2023 - Sep 2023',
                'desc': 'Supported marketing outreach for Kerodex, preparing client communication and promoting the product across manufacturing, healthcare, and engineering industries.'
            },
            {
                'role': 'Technical Support Engineer',
                'company': 'Multisoft India',
                'period': 'Feb 2021 - Jul 2021',
                'desc': 'Assisted clients with software and hardware support, troubleshooting technical issues, and improving the reliability of day-to-day systems.'
            }
        ],
        'testimonials': []
    }
    return render(request, 'portfolio.html', context)


@require_POST
def submit_contact(request):
    name = get_post_value(request, 'name')
    email = get_post_value(request, 'email')
    phone = get_post_value(request, 'phone')
    subject = 'Contact form'
    message = get_post_value(request, 'message')

    if not all([name, email, phone, message]):
        return JsonResponse({'ok': False, 'message': 'Please complete all fields.'}, status=400)

    contact_message = ContactMessage.objects.create(
        name=name,
        email=email,
        phone=phone,
        subject=subject,
        message=message,
    )

    telegram_message = (
        '<b>New contact message</b>\n\n'
        f'<b>Name:</b> {name}\n'
        f'<b>Email:</b> {email}\n'
        f'<b>Mobile:</b> {phone}\n'
        f'<b>Message:</b>\n{message}'
    )
    email_message, html_email_message = build_notification_email(
        'New contact message',
        'Someone filled out the Get in Touch form.',
        [
            ('Name', name),
            ('Email', email),
            ('Mobile', phone),
        ],
        'Message',
        message,
    )
    contact_message.telegram_sent = send_telegram_message(telegram_message)
    contact_message.email_sent = send_notification_email(
        'New portfolio contact message',
        email_message,
        html_email_message,
    )
    contact_message.save(update_fields=['telegram_sent', 'email_sent'])

    return JsonResponse({'ok': True, 'message': 'Message sent successfully.'})


@require_POST
def submit_testimonial(request):
    name = get_post_value(request, 'name')
    designation = get_post_value(request, 'designation')
    company = get_post_value(request, 'company')
    rating = get_post_value(request, 'feedback-rating')
    feedback = get_post_value(request, 'feedback')

    if not all([name, designation, company, rating, feedback]):
        return JsonResponse({'ok': False, 'message': 'Please complete all fields.'}, status=400)

    try:
        rating_value = int(rating)
    except ValueError:
        return JsonResponse({'ok': False, 'message': 'Please choose a valid rating.'}, status=400)

    if rating_value < 1 or rating_value > 5:
        return JsonResponse({'ok': False, 'message': 'Please choose a rating from 1 to 5.'}, status=400)

    testimonial = TestimonialSubmission.objects.create(
        name=name,
        designation=designation,
        company=company,
        rating=rating_value,
        feedback=feedback,
    )

    telegram_message = (
        '<b>New testimonial</b>\n\n'
        f'<b>Name:</b> {name}\n'
        f'<b>Designation:</b> {designation}\n'
        f'<b>Company:</b> {company}\n'
        f'<b>Rating:</b> {rating_value}/5\n\n'
        f'<b>Feedback:</b>\n{feedback}'
    )
    email_message, html_email_message = build_notification_email(
        'New testimonial',
        'Someone shared their experience from your portfolio.',
        [
            ('Name', name),
            ('Designation', designation),
            ('Company', company),
            ('Rating', f'{rating_value}/5'),
        ],
        'Feedback',
        feedback,
    )
    testimonial.telegram_sent = send_telegram_message(telegram_message)
    testimonial.email_sent = send_notification_email(
        'New portfolio testimonial',
        email_message,
        html_email_message,
    )
    testimonial.save(update_fields=['telegram_sent', 'email_sent'])

    return JsonResponse({'ok': True, 'message': 'Feedback sent successfully.'})
