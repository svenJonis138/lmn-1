from django.test import TestCase

from django.contrib.auth.models import User
from lmn.forms import NewNoteForm, UserRegistrationForm
import string
import shutil
from PIL import Image 
from django.urls import reverse
import tempfile
import filecmp
import os 

# Test that forms are validating correctly, and don't accept invalid data

class NewNoteFormTests(TestCase):

    def test_missing_title_is_invalid(self):
        form_data = { "text": "blah blah"}
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

        invalid_titles = list(string.whitespace) + ['   ', '\n\n\n', '\t\t\n\t']

        for invalid_title in invalid_titles:
            form_data = { "title" : invalid_title , "text": "blah blah"}
            form = NewNoteForm(form_data)
            self.assertFalse(form.is_valid())


    def test_missing_text_is_invalid(self):
        form_data = { "title" : "blah blah" }
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())

        invalid_texts = list(string.whitespace) + ['   ', '\n\n\n', '\t\t\n\t']

        for invalid_text in invalid_texts:
            form_data = { "title": "blah blah", "text" : invalid_text}
            form = NewNoteForm(form_data)
            self.assertFalse(form.is_valid())



    def test_title_too_long_is_invalid(self):
        # Max length is 200
        form_data = { "title" : "a" * 201 }
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())


    def test_text_too_long_is_invalid(self):
        # Max length is 1000
        form_data = { "title" : "a" * 1001 }
        form = NewNoteForm(form_data)
        self.assertFalse(form.is_valid())


    def test_ok_title_and_length_is_valid(self):
        form_data = { "title": "blah blah", "text" : "blah, blah, blah."}
        form = NewNoteForm(form_data)
        self.assertTrue(form.is_valid())


class RegistrationFormTests(TestCase):

    # missing fields

    def test_register_user_with_valid_data_is_valid(self):
        form_data = { 'username' : 'bob' , 'email' : 'bob@bob.com', 'first_name' : 'bob', 'last_name' : 'whatever', 'password1' : 'q!w$er^ty6ui7op', 'password2' : 'q!w$er^ty6ui7op' }
        form = UserRegistrationForm(form_data)
        self.assertTrue(form.is_valid())


    def test_register_user_with_missing_data_fails(self):
        form_data = { 'username': 'bob', 'email' : 'bob@bob.com', 'first_name' : 'bob', 'last_name' : 'whatever', 'password1' : 'q!w$er^ty6ui7op', 'password2' : 'q!w$er^ty6ui7op' }
        # Remove each key-value from dictionary, assert form not valid
        for field in form_data.keys():
            data = dict(form_data)
            del(data[field])
            form = UserRegistrationForm(data)
            self.assertFalse(form.is_valid())


    def test_register_user_with_password_mismatch_fails(self):
        form_data = { 'username' : 'another_bob' , 'email' : 'bob@bob.com', 'first_name' : 'bob', 'last_name' : 'whatever', 'password1' : 'q!w$er^ty6ui7op', 'password2' : 'dr%$ESwsdgdfh' }
        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())


    def test_register_user_with_email_already_in_db_fails(self):

        # Create a user with email bob@bob.com
        bob = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        bob.save()

        # attempt to create another user with same email
        form_data = { 'username' : 'another_bob' , 'email' : 'bob@bob.com', 'first_name' : 'bob', 'last_name' : 'whatever', 'password1' : 'q!w$er^ty6ui7op', 'password2' : 'q!w$er^ty6ui7op' }
        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())


    def test_register_user_with_username_already_in_db_fails(self):

        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        # attempt to create another user with same username
        form_data = { 'username' : 'bob' , 'email' : 'another_bob@bob.com', 'first_name' : 'bob', 'last_name' : 'whatever', 'password1' : 'q!w$er^ty6ui7op', 'password2' : 'q!w$er^ty6ui7op' }
        form = UserRegistrationForm(form_data)
        self.assertFalse(form.is_valid())


    # TODO make this test pass!
    def test_register_user_with_username_already_in_db_case_insensitive_fails(self):

        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        invalid_username = ['BOB', 'BOb', 'Bob', 'bOB', 'bOb', 'boB']

        for invalid in invalid_username:
            # attempt to create another user with same username
            form_data = { 'username' : invalid , 'email' : 'another_bob@bob.com', 'first_name' : 'bob', 'last_name' : 'whatever', 'password1' : 'q!w$er^ty6ui7op', 'password2' : 'q!w$er^ty6ui7opq!w$er^ty6ui7op' }
            form = UserRegistrationForm(form_data)
            self.assertFalse(form.is_valid())


    # TODO make this test pass!
    def test_register_user_with_email_already_in_db_case_insensitive_fails(self):

        # Create a user with username bob
        bob = User(username='bob', email='bob@bob.com')
        bob.save()

        invalid_email = ['BOB@bOb.com', 'BOb@bob.cOm', 'Bob@bob.coM', 'BOB@BOB.COM', 'bOb@bob.com', 'boB@bob.com']

        for invalid in invalid_email:
            # attempt to create another user with same username
            form_data = { 'username' : 'another_bob' , 'email' : invalid, 'first_name' : 'bob', 'last_name' : 'whatever', 'password1' : 'q!w$er^ty6ui7op', 'password2' : 'q!w$er^ty6ui7op' }
            form = UserRegistrationForm(form_data)
            self.assertFalse(form.is_valid())




class LoginFormTests(TestCase):

    # TODO username not case sensitive - bob and BOB and Bob are the same
   
    pass

# class TestImageUpload(TestCase):
#     fixtures = ['testing_users', 'testing_venues', 'testing_artists', 'testing_shows']

#     def setUp(self):
#         user = User.objects.get(pk=1)
#         self.client.force_login(user)
#         self.MEDIA_ROOT = tempfile.mkdtemp()

#     def tearDown(self):
#         shutil.rmtree(self.MEDIA_ROOT)

#     def create_temp_image_file(self):
#         handle, tmp_img_file = tempfile.mkstemp(suffix='.jpg')
#         img = Image.new('RGB', (10, 10) )
#         img.save(tmp_img_file, format='JPEG')
#         return tmp_img_file

#     def test_upload_image_for_own_note(self):

#         img_file_path = self.create_temp_image_file()

#         with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
#             with open(img_file_path, 'rb') as img_file:
#                 post_data = {
#                     'title': 'note title',
#                     'text': 'note description',
#                     'photo': img_file,
#                     'Rate': 'Good'
#                 }
#                 resp = self.client.post(reverse('new_note', kwargs={'show_pk': 1}), post_data, follow = True )

#                 self.assertEqual(200, resp.status_code)

#                 note_1 = Note.objects.get(pk=1)
#                 img_file_name = os.path.basename(img_file_path)
#                 expected_uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

#                 self.assertTrue(os.path.exists(expected_uploaded_file_path))
#                 self.assertIsNotNone(note_1.photo)
#                 self.assertTrue(filecmp.cmp(img_file_path, expected_uploaded_file_path))

