"""Test for voting system."""
import datetime
from html import escape

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from polls.models import Question
from django.urls import reverse


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
    return Question.objects.create(question_text=question_text, pub_date=timezone.now(), end_date=time)


class VotingSystemTest(TestCase):
    """Test for voting system."""

    def setUp(self):
        """Create test user and question for testing."""
        self.test_user_password = "testPassword1"
        self.test_username = "test"
        self.test_user = User.objects.create_user(username=self.test_username, password=self.test_user_password)
        self.test_question = create_question("rmtirnte", 12)
        self.test_choice_1 = self.test_question.choice_set.create(choice_text="Choice 1")
        self.test_choice_2 = self.test_question.choice_set.create(choice_text="Choice 2")
        self.vote_url = reverse("polls:vote", args=[self.test_question.id])

    def test_voting_without_login(self):
        """Attempting to vote without login will fail."""
        login_url = f"{reverse('login')}?next={self.vote_url}"
        response = self.client.post(self.vote_url, data={"choice": self.test_choice_1.id})
        self.assertRedirects(response, login_url)

    def test_voting_with_logged(self):
        """Voting will increase vote by one."""
        self.login()
        self.client.post(self.vote_url, data={"choice": self.test_choice_1.id})
        self.assertEqual(self.test_choice_1.votes, 1)

    def login(self):
        """Login using test username and password."""
        self.client.login(username=self.test_username, password=self.test_user_password)

    def test_voting_with_same_choice(self):
        """Voting with same choice will not increase the vote."""
        self.login()
        # Attempt to vote 3 times
        for _ in range(3):
            self.client.post(self.vote_url, data={"choice": self.test_choice_1.id})
        self.assertEqual(self.test_choice_1.votes, 1)

    def test_voting_with_different_choice(self):
        """Voting different choice will change vote.

        The previous vote will be changed to the new one.
        """
        self.login()
        self.client.post(self.vote_url, data={"choice": self.test_choice_1.id})
        self.client.post(self.vote_url, data={"choice": self.test_choice_2.id})
        self.assertEqual(self.test_choice_1.votes, 0)
        self.assertEqual(self.test_choice_2.votes, 1)

    def test_voting_invalid_choice(self):
        """Voting with invalid choice wil lead to an error message."""
        self.login()
        response = self.client.post(self.vote_url, data={"choice": 123})
        # HTML Escape is required as some characters are escaped.
        self.assertContains(response, escape("You didn't select a choice."))
