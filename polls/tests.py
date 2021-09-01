from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
import datetime

from .models import Question


def create_question(question_text, days):
    """
    Create a question with given `question_text` and published
    `days` days after it was created.
    Args:
        question_text (str): Question text
        days (int): Day difference from now
    Returns:
        Question: Created question with specified question and pub_date
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


# Create your tests here.

class QuestionModelTest(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() return False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() return False for question whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question  = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_publised_recently_with_recent_question(self):
        """
        was_published_recently() return True for question whose pub_date
        is within 1 day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTest(TestCase):
    def test_no_question(self):
        """If there is no question, there is an appropriate message."""
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """Past questions are displayed on the index."""
        question = create_question(question_text="Past question", days=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_future_question(self):
        """Future questions are not displayed on the index."""
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            []
        )

    def test_past_and_future_question(self):
        """If both past and future questions are present, only past ones are displayed."""
        create_question(question_text="Past question", days=-20)
        future_question = create_question(question_text="Future question", days=20)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [future_question]
        )

    def test_two_past_questions(self):
        """The index page should be able to display multiple questions."""
        question_1 = create_question(question_text="Past question 1", days=-2)
        question_2 = create_question(question_text="Past question 2", days=-3)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question_1, question_2]
        )
