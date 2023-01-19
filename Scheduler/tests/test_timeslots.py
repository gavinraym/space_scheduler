from django.test import TestCase
from Scheduler.models import Timeslots, Meetings, Contacts
from datetime import datetime, timezone
# run tests with: python manage.py test

START1 = datetime(2022, 12, 15, 9, 30,tzinfo=timezone.utc)
END1 = datetime(2022, 12, 15, 16, 30,tzinfo=timezone.utc)

START2 = datetime(2022, 12, 16, 9, 30,tzinfo=timezone.utc)
END2 = datetime(2022, 12, 16, 10, 30,tzinfo=timezone.utc)

START3 = datetime(2022, 12, 16, 10,tzinfo=timezone.utc)
END3 = datetime(2022, 12, 16, 11,tzinfo=timezone.utc)

MSTART1 = datetime(2022, 12, 15, 9, 30, tzinfo=timezone.utc)
MEND1 = datetime(2022, 12, 15, 10, tzinfo=timezone.utc)

MSTART2 = datetime(2022, 12, 15, 13,30, tzinfo=timezone.utc)
MEND2 = datetime(2022, 12, 15, 14,30, tzinfo=timezone.utc)

MSTART3 = datetime(2022, 12, 15, 15, 30, tzinfo=timezone.utc)
MEND3 = datetime(2022, 12, 15, 16, 30, tzinfo=timezone.utc)

TOSTRF = lambda dt: dt.strftime("%Y%m%d%H%M")

class TimeslotTestCase(TestCase):
    def setUp(self):
        self.contact = Contacts.create(name="gavin", email="gray15@wgu.edu")
        self.ts = Timeslots.objects.create(start=START1, end=END1)
    
    def test_main(self):
        Timeslots.create(START2, END2)
        assert(Timeslots.objects.filter(start=START1))
        assert(Timeslots.objects.filter(start=START2))
        
        queryset = Timeslots.during_period(datetime(2022,12,15,15), datetime(2022,12,15,16))
        assert(len(queryset) == 1)
        self.assertEqual(queryset[0].start, START1)
        assert(queryset[0].end == END1)
        
        queryset = Timeslots.during_period(datetime(2022,12,15),datetime(2022,12,20))
        assert(len(queryset) == 2)
        assert(queryset[0].start == START1)
        assert(queryset[0].end == END1)
        assert(queryset[1].start == START2)
        self.assertEqual(queryset[1].end, END2)
        
        Timeslots.remove(queryset[0].id)
        queryset = Timeslots.during_period(datetime(2022,12,15),datetime(2022,12,20))
        assert(len(queryset) == 1)
        
        data = queryset[0].to_dict()
        assert("id" in data)
        assert("start" in data)
        assert("end" in data)
        
    def test_contains(self):
        self.assertTrue(Timeslots.contains(MSTART1, MEND1))
        self.assertEqual(Timeslots.contains(MSTART1, MEND1)[0], self.ts)
        self.assertTrue(Timeslots.contains(MSTART2, MEND2))
        self.assertEqual(Timeslots.contains(MSTART2, MEND2)[0], self.ts)
        self.assertTrue(Timeslots.contains(MSTART3, MEND3))
        self.assertEqual(Timeslots.contains(MSTART3, MEND3)[0], self.ts)

        
    def test_open_times1(self):
        # Testing open times when meeting starts at start of timeslot
        Meetings.create(MSTART1, MEND1, 30, "obj",  self.contact)
        open_times = self.ts.open_times()
        self.assertEqual(len(open_times), 2) 
        
    def test_open_times2(self):
        # Testing open times when meeting is completely within timeslot.
        
        m = Meetings.create(MSTART2, MEND2, 60, "obj", self.contact)
        open_times = self.ts.open_times()
        self.assertEqual(len(open_times), 2)      
        
  
        
    def test_create_with_overlap(self):
        # Test timeslot that ends at existing ts start
        start1 = datetime(2022, 12, 15, 8, 30,tzinfo=timezone.utc)
        end1 = datetime(2022, 12, 15, 9, 30,tzinfo=timezone.utc)
        Timeslots.create(start1, end1)
        result = Timeslots.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, start1)
        self.assertEqual(result[0].end, END1)
        
        # Test timeslot that ends after existing ts start
        start2 = datetime(2022, 12, 15, 7, 30,tzinfo=timezone.utc)
        end2 = datetime(2022, 12, 15, 9, 30,tzinfo=timezone.utc)
        Timeslots.create(start2, end2)
        result = Timeslots.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, start2)
        self.assertEqual(result[0].end, END1)
        
        # Test timeslot that overlaps existing ts start and end
        start3 = datetime(2022, 12, 15, 5, 30,tzinfo=timezone.utc)
        end3 = datetime(2022, 12, 16, 9, 30,tzinfo=timezone.utc)
        Timeslots.create(start3, end3)
        result = Timeslots.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, start3)
        self.assertEqual(result[0].end, end3)
        
        # Test timeslot that overlaps extentds existing ts end
        start4 = datetime(2022, 12, 15, 7, 30,tzinfo=timezone.utc)
        end4 = datetime(2022, 12, 16, 9, 30,tzinfo=timezone.utc)
        Timeslots.create(start4, end4)
        result = Timeslots.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, start3)
        self.assertEqual(result[0].end, end4)
        
        # Test timeslot that starts at existing ts end
        start5 = datetime(2022, 12, 16, 9, 30,tzinfo=timezone.utc)
        end5 = datetime(2022, 12, 16, 10, 30,tzinfo=timezone.utc)
        Timeslots.create(start5, end5)
        result = Timeslots.objects.all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, start3)
        self.assertEqual(result[0].end, end5)
  
    