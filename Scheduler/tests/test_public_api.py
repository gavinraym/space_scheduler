from django.test import TestCase
from Scheduler.models import Meetings, Contacts, Timeslots
from django.urls import reverse
import json



from datetime import datetime, timezone

TS_START1 = datetime(2025, 12, 25, 3, tzinfo=timezone.utc)
TS_END1 = datetime(2025,12,25,8, tzinfo=timezone.utc)

START1 = datetime(2025,12,25,5, tzinfo=timezone.utc)
END1 = datetime(2025, 12,25,5,30, tzinfo=timezone.utc)
dur1=30

TS_START2 = datetime(2025, 12, 26, 5, tzinfo=timezone.utc)
TS_END2 = datetime(2025,12,26,18, tzinfo=timezone.utc)

START2 = datetime(2025,12,26,7, tzinfo=timezone.utc)
END2 = datetime(2025, 12,26,8, tzinfo=timezone.utc)
dur2 = 60



class PublicApiTest(TestCase):
    def setUp(self):
        self.contact = Contacts.create(name="gavin", email="gray15@wgu.edu")
        self.timeslot1 = Timeslots.create( start=TS_START1, end=TS_END1)
        self.timeslot2 = Timeslots.create(start=TS_START2, end=TS_END2)
        self.meeting1 = Meetings.create(START1, END1, dur1, "obj", self.contact)
        self.meeting2 = Meetings.create(START2, END2, dur2, "obj", self.contact)
        
        
    def test_get_times(self):
        response = self.client.get(reverse('scheduler-get-times'))
        data = eval(response.content)
        self.assertEqual(len(data), 4)

        

        

    