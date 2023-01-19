from django.test import TestCase
from Scheduler.models import Meetings, Contacts, Timeslots

from datetime import datetime, timezone
TS_START = datetime(2022, 12, 25, 3, tzinfo=timezone.utc)
TS_END = datetime(2022,12,25,8, tzinfo=timezone.utc)

START1 = datetime(2022,12,25,3, tzinfo=timezone.utc)
END1 = datetime(2022, 12,25,4,30, tzinfo=timezone.utc)

START2 = datetime(2022,12,25,5, tzinfo=timezone.utc)
END2 = datetime(2022, 12,25,5,30, tzinfo=timezone.utc)

START3 = datetime(2022,12,25,7, tzinfo=timezone.utc)
END3 = datetime(2022, 12,25,8, tzinfo=timezone.utc)

INVALID_START = datetime(2022, 12, 1, tzinfo=timezone.utc)
INVALID_END = datetime(2022, 12, 1, 2, tzinfo=timezone.utc)

class MeetingTestCase(TestCase):
    def setUp(self):
        self.contact = Contacts.objects.create(name="gavin", email="gray15@wgu.edu")
        self.timeslot = Timeslots.objects.create( start=TS_START, end=TS_END)
        
    def test_create(self):
        # Add new meeting with same start time as timeslot
        self.assertFalse(Meetings.during_period(START1, START2))
        self.assertTrue(Meetings.create(START1, END1, 90,"objective", self.contact))
        self.assertTrue(Meetings.objects.filter(start=START1))
        
        # Add invalid meetings
        self.assertFalse(Meetings.during_period(INVALID_START, INVALID_END))
        # These tests should return assertion errors
        self.assertRaises(AssertionError, Meetings.create,START1, END1, 90,"objective", self.contact)
        self.assertRaises(AssertionError, Meetings.create, INVALID_START, INVALID_END, 30,"objective", self.contact)
        self.assertRaises(AssertionError, Meetings.create, START2, END2, -45,"objective", self.contact)
        self.assertRaises(AssertionError, Meetings.create, START2, END2, 45,"objective", self.contact)
        self.assertRaises(AssertionError, Meetings.create, END2, START2, 30,"objective", self.contact)

        # Add second meeting within timeslot
        self.assertTrue(Meetings.create(START2, END2, 30, "obj", self.contact))
         
        # Test during period
        period = Meetings.during_period(TS_START, TS_END)
        self.assertTrue(period)
        self.assertEqual(len(period), 2)
        self.assertEqual(str(period[0].start), str(START1))
        self.assertEqual(str(period[0].end), str(END1))
        self.assertEqual(str(period[1].start), str(START2))
        self.assertEqual(str(period[1].end), str(END2))
        
        # Creates meeting with same end time as timeslot
        self.assertTrue(Meetings.create(START3, END3, 60, "obj", self.contact))
        
        
    