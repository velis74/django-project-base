from django.test import TestCase

from django_project_base.notifications.base.phone_number_parser import PhoneNumberParser


class IsPhoneNumberValidTest(TestCase):
    def test_is_phone_number_valid(self):
        self.assertFalse(PhoneNumberParser.is_allowed("0903028"))
        self.assertFalse(PhoneNumberParser.is_allowed("1919"))
        self.assertTrue(PhoneNumberParser.is_allowed("03897234"))
        self.assertTrue(PhoneNumberParser.is_allowed("0038631697001"))
        self.assertTrue(PhoneNumberParser.is_allowed("+38676234567"))
