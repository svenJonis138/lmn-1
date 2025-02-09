from django.test import TestCase

from django.contrib.auth.models import User
from lmn.forms import NewNoteForm, UserRegistrationForm, ProfileForm
import string
from datetime import datetime
from lmn.models import Artist, Venue, Show


# Test that forms are validating correctly, and don't accept invalid data

class NewNoteFormTests(TestCase):

    def test_missing_title_is_invalid(self):
        form_data = {"text": "blah blah"}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

        invalid_titles = list(string.whitespace) + ['   ', '\n\n\n', '\t\t\n\t']

        for invalid_title in invalid_titles:
            form_data = {"title": invalid_title, "text": "blah blah"}
            form = NewNoteForm(form_data)
            self.assertFalse(form.is_valid())

    def test_missing_text_is_invalid(self):
        form_data = {"title": "blah blah"}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

        invalid_texts = list(string.whitespace) + ['   ', '\n\n\n', '\t\t\n\t']

        for invalid_text in invalid_texts:
            form_data = {"title": "blah blah", "text": invalid_text}
            form = NewNoteForm(form_data)
            self.assertFalse(form.is_valid())

    def test_title_too_long_is_invalid(self):
        # Max length is 200
        form_data = {"title": "a" * 201}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

    def test_text_too_long_is_invalid(self):
        # Max length is 1000
        form_data = {"title": "a" * 1001}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

    def test_ok_title_and_length_is_valid(self):
        form_data = {'title': 'blah blah', 'text': 'blah, blah, blah.', 'rate': 'Great'}
        form = NewNoteForm(form_data)
        self.assertTrue(form.is_valid())


class RegistrationFormTests(TestCase):

    # missing fields

    def test_register_user_with_valid_data_is_valid(self):
        form_data = {'username': 'bob', 'email': 'bob@bob.com', 'first_name': 'bob', 'last_name': 'whatever',
                     'password1': 'q!w$er^ty6ui7op', 'password2': 'q!w$er^ty6ui7op'}
        form = UserRegistrationForm(form_data)
        self.assertTrue(form.is_valid())

    def test_register_user_with_missing_data_fails(self):
        form_data = {'username': 'bob', 'email': 'bob@bob.com', 'first_name': 'bob', 'last_name': 'whatever',
                     'password1': 'q!w$er^ty6ui7op', 'password2': 'q!w$er^ty6ui7op'}
        # Remove each key-value from dictionary, assert form not valid
        for field in form_data.keys():
            data = dict(form_data)
            del (data[field])
            form = UserRegistrationForm(data)
            self.assertFalse(form.is_valid())

    def test_register_user_with_password_mismatch_fails(self):
        form_data = {'username': 'another_bob', 'email': 'bob@bob.com', 'first_name': 'bob', 'last_name': 'whatever',
                     'password1': 'q!w$er^ty6ui7op', 'password2': 'dr%$ESwsdgdfh'}
        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_user_with_email_already_in_db_fails(self):

        # Create a user with email bob@bob.com
        bob = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        bob.save()

        # attempt to create another user with same email
        form_data = {'username': 'another_bob', 'email': 'bob@bob.com', 'first_name': 'bob', 'last_name': 'whatever',
                     'password1': 'q!w$er^ty6ui7op', 'password2': 'q!w$er^ty6ui7op'}
        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())

    def test_register_user_with_username_already_in_db_fails(self):

        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        # attempt to create another user with same username
        form_data = {'username': 'bob', 'email': 'another_bob@bob.com', 'first_name': 'bob', 'last_name': 'whatever',
                     'password1': 'q!w$er^ty6ui7op', 'password2': 'q!w$er^ty6ui7op'}
        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())

    # TODO make this test pass! DONE
    def test_register_user_with_username_already_in_db_case_insensitive_fails(self):

        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        invalid_username = ['BOB', 'BOb', 'Bob', 'bOB', 'bOb', 'boB']

        for invalid in invalid_username:
            # attempt to create another user with same username
            form_data = {'username': invalid, 'email': 'another_bob@bob.com', 'first_name': 'bob',
                         'last_name': 'whatever', 'password1': 'q!w$er^ty6ui7op',
                         'password2': 'q!w$er^ty6ui7opq!w$er^ty6ui7op'}
            form = UserRegistrationForm(form_data)
            self.assertFalse(form.is_valid())

    # TODO make this test pass! DONE
    def test_register_user_with_email_already_in_db_case_insensitive_fails(self):

        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        invalid_email = ['BOB@bOb.com', 'BOb@bob.cOm', 'Bob@bob.coM', 'BOB@BOB.COM', 'bOb@bob.com', 'boB@bob.com']

        for invalid in invalid_email:
            # attempt to create another user with same username
            form_data = {'username': 'another_bob', 'email': invalid, 'first_name': 'bob', 'last_name': 'whatever',
                         'password1': 'q!w$er^ty6ui7op', 'password2': 'q!w$er^ty6ui7op'}
            form = UserRegistrationForm(form_data)
            self.assertFalse(form.is_valid())


class LoginFormTests(TestCase):
    # TODO username not case sensitive - bob and BOB and Bob are the same

    pass


class ProfileFormTests(TestCase):
    def test_user_can_add_empty_data(self):
        user = User(username='fakeuser', email='fake@email.address')
        user.save()

        form_data = { 'twitter_username' : None, 'bio': None, 'favorite_artist' : None, 'favorite_show' : None }
        form = ProfileForm(form_data)

        self.assertTrue(form.is_valid())


    def test_user_can_add_filled_data(self):
        user = User(username='fakeuser', email='fake@email.address')
        user.save()
        artist = Artist(name='Nym', hometown='Place', description='A Band')
        artist.save()
        venue = Venue(name='Arena', address='123 Location')
        venue.save()
        show = Show(show_date=datetime.now(), artist=artist, venue=venue)
        show.save()

        form_data = { 'twitter_username' : 'fakeusername', 'bio': 'Fake biography.', 'favorite_artist' : artist, 'favorite_show' : show }
        form = ProfileForm(form_data)

        self.assertTrue(form.is_valid())


    def test_twitter_username_must_be_under_15_characters(self):
        user = User(username='fakeuser', email='fake@email.address')
        user.save()

        form_data = { 'thisis==15chars' : None, 'bio': None, 'favorite_artist' : None, 'favorite_show' : None }
        form = ProfileForm(form_data)

        self.assertTrue(form.is_valid())

        form_data = { 'thisis==sixteen!' : None, 'bio': None, 'favorite_artist' : None, 'favorite_show' : None }
        form = ProfileForm(form_data)

        self.assertTrue(form.is_valid())
