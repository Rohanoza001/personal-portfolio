from django.test import TestCase
from django.urls import reverse


class PortfolioViewTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('portfolio'))
        self.content = self.response.content.decode()

    def test_portfolio_page_renders(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'portfolio.html')

    def test_main_sections_are_present_once(self):
        for section_id in (
            'about',
            'experience',
            'projects',
            'testimonials',
            'feedback',
            'contact',
        ):
            self.assertEqual(self.content.count(f'id="{section_id}"'), 1)

    def test_current_skills_heading_replaces_legacy_heading(self):
        self.assertContains(self.response, 'My <span class="title-highlight">Skills</span>', html=True)
        self.assertNotContains(self.response, 'Crafting Digital')

    def test_removed_testimonial_preview_and_footer_feedback_link_stay_removed(self):
        self.assertNotContains(self.response, 'testimonial-preview')
        self.assertNotContains(self.response, 'Give feedback')
        self.assertNotContains(self.response, 'View all testimonials')

    def test_feedback_form_has_client_details_and_rating(self):
        self.assertContains(self.response, 'name="designation"')
        self.assertContains(self.response, 'name="company"')
        self.assertContains(self.response, 'name="feedback-rating"', count=5)

    def test_expected_portfolio_content_is_supplied(self):
        self.assertEqual(len(self.response.context['projects']), 3)
        self.assertEqual(len(self.response.context['experiences']), 3)
        self.assertEqual(len(self.response.context['testimonials']), 3)
        self.assertNotIn('services', self.response.context)
