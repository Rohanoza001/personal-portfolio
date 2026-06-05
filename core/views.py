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
            'name': 'Rohan',
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
                'category': 'Frontend',
                'items': [
                    {'name': 'HTML5 & CSS3', 'level': 95},
                    {'name': 'JavaScript (ES6+)', 'level': 90},
                    {'name': 'React / Next.js', 'level': 85},
                    {'name': 'TypeScript', 'level': 80},
                ]
            },
            {
                'category': 'Backend',
                'items': [
                    {'name': 'Python', 'level': 90},
                    {'name': 'Django', 'level': 85},
                    {'name': 'Node.js / Express', 'level': 75},
                    {'name': 'SQL & Databases', 'level': 80},
                ]
            },
            {
                'category': 'Tools & Design',
                'items': [
                    {'name': 'Git & GitHub', 'level': 90},
                    {'name': 'Figma (UI/UX)', 'level': 85},
                    {'name': 'Docker', 'level': 70},
                    {'name': 'AWS / Deployment', 'level': 75},
                ]
            }
        ],
        'projects': [
            {
                'title': 'Homebound Real Estate',
                'desc': 'A premium real estate marketplace featuring interactive property cards, advanced filtering, and instant lead capture.',
                'tech': ['Django', 'Python', 'SQLite', 'Vanilla CSS'],
                'image': 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80',
                'live_url': '#',
                'github_url': '#'
            },
            {
                'title': 'Zenith Analytics Dashboard',
                'desc': 'A beautiful dashboard utilizing glassmorphism styling, interactive charts, and automated daily data reports.',
                'tech': ['React', 'Chart.js', 'Vanilla CSS', 'Node.js'],
                'image': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80',
                'live_url': '#',
                'github_url': '#'
            },
            {
                'title': 'Scribe AI Writing Assistant',
                'desc': 'An AI-powered application that drafts articles, posts, and marketing copy using OpenAI integration.',
                'tech': ['Next.js', 'OpenAI API', 'CSS Modules'],
                'image': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80',
                'live_url': '#',
                'github_url': '#'
            }
        ],
        'experiences': [
            {
                'role': 'Senior Full-Stack Developer',
                'company': 'InnoTech Solutions',
                'period': '2024 - Present',
                'desc': 'Lead the development of client web applications, design RESTful APIs, and mentor junior developers in modern coding standards.'
            },
            {
                'role': 'Web Developer',
                'company': 'PixelPerfect Labs',
                'period': '2022 - 2024',
                'desc': 'Created high-performance UI components, optimized web loading times by 40%, and converted UI designs to responsive templates.'
            },
            {
                'role': 'Junior Developer',
                'company': 'LaunchPad Devs',
                'period': '2020 - 2022',
                'desc': 'Built and maintained client sites, wrote unit tests, and integrated third-party REST APIs into web applications.'
            }
        ],
        'testimonials': [
            {
                'quote': 'Rohan translated a complex product idea into a polished experience that felt simple, fast, and genuinely enjoyable to use.',
                'name': 'Anika Sharma',
                'initials': 'AS',
                'role': 'Product Lead',
                'company': 'Northstar Labs'
            },
            {
                'quote': 'The attention to detail was exceptional. Our new platform looks sharper, performs better, and has made our team more confident.',
                'name': 'Marcus Chen',
                'initials': 'MC',
                'role': 'Founder',
                'company': 'Frame Analytics'
            },
            {
                'quote': 'Clear communication, thoughtful decisions, and dependable delivery from start to finish. Rohan felt like part of our internal team.',
                'name': 'Priya Mehta',
                'initials': 'PM',
                'role': 'Design Director',
                'company': 'Studio Current'
            }
        ]
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
