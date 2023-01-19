from django.test import TestCase
from Scheduler.models import Contacts
from django.core.exceptions import ValidationError
from datetime import date as dt, time as tm

class ContactTestCase(TestCase):
    def test_create(self):
        # Add contact
        contact = Contacts.create("gavin", "gray15@wgu.edu")
        self.assertEqual(contact.name, "gavin")
        self.assertEqual(contact.email, "gray15@wgu.edu")
        self.assertEqual(len(Contacts.objects.all()), 1)
        
        # Try to add contact with invalid email
        self.assertRaises(ValidationError, Contacts.create, "dave", "davewgu.edu")
        self.assertFalse(Contacts.objects.filter(name="dave"))
        
        # Change name of contact
        contact = Contacts.create("gavin ray", "gray15@wgu.edu")
        self.assertEqual(contact.name, "gavin ray")
        self.assertEqual(contact.email, "gray15@wgu.edu")
        self.assertEqual(len(Contacts.objects.all()), 1)
        
        # Name is not required
        contact = Contacts.create("", "gray15@wgu.edu")
        self.assertEqual(contact.name, "gavin ray")
        self.assertEqual(contact.email, "gray15@wgu.edu")
        self.assertEqual(len(Contacts.objects.all()), 1)
    

        
        
        