"""Tests for poll application."""
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
import datetime

from polls.models import Question


def create_question(question_text, days):
    """
    Create a question with given `question_text` and published `days` days after it was created.

    Args:
        question_text (str): Question text
        days (int): Day difference from now for publication date
    Returns:
        Question: Created question with specified question and pub_date
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time, end_date=time)


# Create your tests here.

class QuestionModelTest(TestCase):
    """Tests for question model."""

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() return False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() return False for question whose pub_date is older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() return True for question whose pub_date is within 1 day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_published_question(self):
        """is_published() returns True when the current time passes the publication date."""
        time = timezone.now() - datetime.timedelta(days=2)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.is_published(), True)

    def test_is_published_with_future_question(self):
        """is_published() returns False when the current time does not pass the publication date."""
        time = timezone.now() + datetime.timedelta(hours=23)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.is_published(), False)

    def test_can_vote_with_question_after_end_date_question(self):
        """can_vote() returns False when the current time passes the end date."""
        pub_date = timezone.now() - datetime.timedelta(days=30)
        end_date = timezone.now() - datetime.timedelta(days=1)
        ended_question = Question(pub_date=pub_date, end_date=end_date)
        self.assertIs(ended_question.can_vote(), False)

    def test_can_vote_with_question_during_pub_date_and_end_date(self):
        """can_vote() returns True when the current time is in the voting period."""
        pub_date = timezone.now()
        end_date = timezone.now() + datetime.timedelta(days=1)
        available_question = Question(pub_date=pub_date, end_date=end_date)
        self.assertIs(available_question.can_vote(), True)

    def test_can_vote_with_future_question(self):
        """can_vote() returns False when the question is in the future."""
        pub_date = timezone.now() + datetime.timedelta(days=1)
        end_date = timezone.now() + datetime.timedelta(days=10)
        future_question = Question(pub_date=pub_date, end_date=end_date)
        self.assertIs(future_question.can_vote(), False)


class QuestionIndexViewTest(TestCase):
    """Tests for questions index view."""

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
        past_question = create_question(question_text="Past question", days=-20)
        create_question(question_text="Future question", days=20)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [past_question]
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

    def test_redirection(self):
        """/ should redirect to /polls path."""
        response = self.client.get('/', follow=True)
        self.assertRedirects(response, reverse('polls:index'), status_code=301)

    def test_more_than_five_questions(self):
        """The index page should display all available questions."""
        question_list = [create_question(question_text=f"Question {i}", days=-i) for i in range(10)]
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            question_list
        )


class QuestionDetailViewTest(TestCase):
    """Tests for questions detail view."""

    def test_future_question(self):
        """It should redirect to the homepage with an error message."""
        future_question = create_question(question_text="Future question", days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('polls:index'))
        self.assertContains(response, "Question not found")

    def test_past_question(self):
        """It should display past question."""
        past_question = create_question(question_text="Past question", days=-1)
        past_question.end_date = timezone.now() + datetime.timedelta(days=30)
        past_question.save()
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_ended_question(self):
        """It should not allow user to vote and redirect to the result."""
        ended_question = create_question(question_text="Ended question", days=-30)
        ended_question.end_date = ended_question.end_date - timezone.timedelta(days=-30)
        ended_question.save()
        url = reverse('polls:detail', args=(ended_question.id,))
        redirected_url = reverse('polls:results', args=(ended_question.id,))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, redirected_url)


class QuestionResultViewTest(TestCase):
    """It should have same behavior with the detail view."""

    def test_future_question(self):
        """It should redirect to the homepage with an error message."""
        future_question = create_question(question_text="Future question", days=30)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, reverse('polls:index'))
        self.assertContains(response, "Question not found")

    def test_past_question(self):
        """It should display past question."""
        past_question = create_question(question_text="Past question", days=-1)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
