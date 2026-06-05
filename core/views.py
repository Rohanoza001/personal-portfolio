import json
import urllib.parse
import urllib.request

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import ContactMessage, TestimonialSubmission


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
            'tagline': 'Designing intuitive digital experiences that blend thoughtful UX, clean interfaces, and modern development.',
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
                'image': 'https://images.unsplash.com/photo-1474487548417-781cb71495f3?auto=format&fit=crop&w=900&q=80',
                'live_url': 'https://www.figma.com/design/BvY0xHE1jEa8wBJOf32AN5/Case-Study--IRCTC-?t=4VMCM0q2sYq6dp2X-0',
                'github_url': ''
            },
            {
                'title': 'Nike Case Study',
                'desc': 'A product experience case study exploring a modern Nike shopping flow, visual hierarchy, product discovery, and conversion-focused UI decisions.',
                'tech': ['UI Design', 'User Flow', 'Figma', 'Design System'],
                'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80',
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
    subject = 'Contact form'
    message = get_post_value(request, 'message')

    if not all([name, email, message]):
        return JsonResponse({'ok': False, 'message': 'Please complete all fields.'}, status=400)

    contact_message = ContactMessage.objects.create(
        name=name,
        email=email,
        subject=subject,
        message=message,
    )

    telegram_message = (
        '<b>New contact message</b>\n\n'
        f'<b>Name:</b> {name}\n'
        f'<b>Email:</b> {email}\n'
        f'<b>Message:</b>\n{message}'
    )
    contact_message.telegram_sent = send_telegram_message(telegram_message)
    contact_message.save(update_fields=['telegram_sent'])

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
    testimonial.telegram_sent = send_telegram_message(telegram_message)
    testimonial.save(update_fields=['telegram_sent'])

    return JsonResponse({'ok': True, 'message': 'Feedback sent successfully.'})
