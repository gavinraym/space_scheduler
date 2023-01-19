from django.db import models
from django.core.validators import validate_email
from datetime import datetime, timedelta

# Create your models here.
class Contacts(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=25)
    email = models.EmailField(max_length=254)
    
    @staticmethod
    def create(name, email):
        validate_email(email) 
        existing_contact = Contacts.objects.filter(email=email)
        # If the contact is already in DB, and a name is given, that is different from 
        # the name in the DB, then name is updated.
        if existing_contact:
            if name and existing_contact[0].name != name:
                existing_contact[0].name = name
                existing_contact[0].save(update_fields=["name"])
            return existing_contact[0]            
        else:
            return Contacts.objects.create(name=name, email=email)
        
    

class Meetings(models.Model):
    contact = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.IntegerField()
    objective = models.CharField(max_length=280)
    note = models.CharField(max_length=500, default="")
    #Status values: u=unconfirmed, c=confirmed, r=rescheduled, a=archived
    status = models.CharField(max_length=1, default="u")
    valid_durations = [15,30,45,60,90,120]
    
    @staticmethod
    def during_period(start, end):
        # Returns all meetings that start and end within the given datetimes
        return Meetings.objects.filter(start__lte=end, end__gte=start)    
    
    @staticmethod
    def create(start, end, duration, objective, contact):
        # Creates meeting, ensuring no other meetings exist at same time
        assert duration in Meetings.valid_durations, "Meeting duration not valid"
        assert (end - start).seconds/60 == duration, "Meeting times do not match duration"
        assert Timeslots.contains(start, end), "There is no timeslot open for meeting's time."
        assert not Meetings.during_period(start, end), "I'm sorry, but the meeting time you selected has been taken. Let me refresh the times for you..."
        return Meetings.objects.create(
                contact=contact, start=start, end=end, duration=duration, objective=objective)
        
    def to_dict(self, summary=False, with_prev=False):
        # Adding basic summary data
        summary_data = {
                "id": self.id,
                "name":self.contact.name,
                "email":self.contact.email,
                "start":self.start.isoformat(),
                "duration": self.duration
            }
        # If summary is designated, return data

        if summary: return summary_data

        # Adding meeting full details
        data = summary_data | {
            "end": self.end.isoformat(),
            "objective": self.objective,
            "note" : self.note or "null",
            "status" : self.status,
        }
        
        # If with_prev designated, adds details of previous meetings with contact
        if with_prev:
            data["previous_meetings"] = [_.to_dict() for _ in Meetings.objects.filter(
                contact=self.contact) if _.id != self.id ]
  
        return data
        


class Timeslots(models.Model):

    start = models.DateTimeField()
    end = models.DateTimeField()
    
    @staticmethod
    def during_period(start, end):
        # Finds any timeslots start and end within the given datetimes
        return Timeslots.objects.filter(start__lte=end, end__gte=start)

    @staticmethod
    def create(start, end):
        # Adds a timeslot to the database that starts and ends at the times given.
        assert( type(start) == datetime and type(end) == datetime)
        # If Timeslot exists within the timeslot, they will be combined.
        for overlapping_timeslot in Timeslots.during_period(start=start, end=end):
            if overlapping_timeslot.start < start: start = overlapping_timeslot.start
            if overlapping_timeslot.end > end: end = overlapping_timeslot.end
            overlapping_timeslot.delete()
        return Timeslots.objects.create(start=start, end=end)
        
    @staticmethod
    def remove(id):
        # Completely removes any timeslot by id
        ts = Timeslots.objects.get(pk=id)
        if ts: 
            ts.delete()
            return True
        else:
            return False
        
    @staticmethod
    def contains(start, end):
        # Returns timeslots that contain the start and end datetimes
        return Timeslots.objects.filter(start__lte=start, end__gte=end)
    
    def to_dict(self):
        return {
            "id" : self.id,
            "start" : self.start.isoformat(),
            "end" : self.end.isoformat()
        }
        
    def open_times(self):
        # Returns list of [open,close] times that a meeting can be scheduled between
        # First record 
        result = [[self.start, self.end]]
        for meeting in Meetings.during_period(self.start, self.end):
            if meeting.start <= result[-1][1]:
                result[-1][1] = meeting.start
                if meeting.end < self.end:
                    result.append([meeting.end + timedelta(minutes=15), self.end])

        # Must convert to lists because sets are not json serializable.
        result = [[start.isoformat(), end.isoformat()] for start,end in result]
        return result
        
    
        
    
    
    