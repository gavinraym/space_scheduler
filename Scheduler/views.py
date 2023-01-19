from rest_framework.decorators import api_view
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import path, include
from Scheduler.models import Meetings, Contacts, Timeslots
from django.http import HttpResponse
import json
from datetime import datetime, timedelta
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie, requires_csrf_token, csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
import pytz


CONTENT_TYPE = "application/json"
DATE_STRF = "%b %d, %Y at %H:%M %p"

EMAIL = 'gavinraycoding@gmail.com'



# # Helper Functions

##################################
#PUBLIC, NOT SECURE API ENDPOINTS#
##################################

@api_view(["GET"])
def public_access_page(request):
    # For retrieving public facing scheduling page template
    context = {}
    return render(request, "public_access_page.html", context)

@api_view(["GET"])
def post_meeting(request):
    #"You've made an appointment with Gavin Ray. You should receive a confirmation email shortly."
    # For scheduling a meeting, requires name, email, objective, date, time, duration
    data = {}
    try:
        contact = Contacts.create(request.GET.get("name"),request.GET.get("email"))
    except ValidationError as err:
        print(err.message)
        data = {"result":False, "msg":"There is an issue with the username and/or email provided. Please check them and try again."}
        return HttpResponse( json.dumps(data), content_type=CONTENT_TYPE)
    start = datetime.fromisoformat(request.GET.get("start"))
    end = start + timedelta(minutes=int(request.GET.get("duration")))
    
    try:
        Meetings.create( start=start, end=end, 
                        duration=int(request.GET.get("duration")),
                        objective=request.GET.get("objective"),
                        contact=contact, 
                        )
        data = {"result":True, "msg":"You've made an appointment with Gavin Ray. You should receive a confirmation email shortly."}
    except Exception as err:
        data = { "result":False, "msg":str(err)}    
    
    send_mail(
    "Meeting booked.",
    render_to_string( "emails/book_meeting.html",
        {
            "utc":start.strftime(DATE_STRF),
            "est":start.astimezone(pytz.timezone('US/Eastern')).strftime(DATE_STRF),
            "pst":start.astimezone(pytz.timezone('US/Pacific')).strftime(DATE_STRF),
        }),
        
    EMAIL,
    [contact.email],
    fail_silently=False
    )
    
        
        
        
    return HttpResponse( json.dumps(data), content_type=CONTENT_TYPE)
    

    
@api_view(["GET"]) 
def get_available_times(request):
    # Returns times for all future available meeting times.
    data = []
    # Returned time segments take the form: [start, end, start, end, etc...]
    # where start and end are datetimes that can be parsed into time segments.
    for timeslot in Timeslots.objects.filter(start__gte=datetime.now()):
        data += timeslot.open_times()
    return HttpResponse(json.dumps(data), content_type=CONTENT_TYPE)
    
    
    
    
##########################
#PRIVATE, MUST BE SECURED#
##########################

# Page for me to access scheduler info
@api_view(["GET"])
@ensure_csrf_cookie
def private_access_page(request):
    # For retrieving private dashboard template.
    if not request.user.is_authenticated:
        return redirect("login/")
    return render(request, "private_access_page.html")

@api_view(["GET"])  
def get_timeslots(request):
    start = datetime.fromisoformat(request.GET["start"])
    end = datetime.fromisoformat(request.GET["end"])
    # Retrieves all registered timeslots for a specific time frame.
    data = [_.to_dict() for _ in Timeslots.during_period(start, end)]
    return HttpResponse(json.dumps(data), content_type=CONTENT_TYPE)

 
@api_view(["POST"])
def add_timeslot(request):
    # Adds a new available timeslot
    start = datetime.fromisoformat(request.POST.get("start"))
    end = datetime.fromisoformat(request.POST.get("end"))
    
    # If timeslot overlaps another timeslot(s), they will be combined.
    data = {}
    try:
        Timeslots.create(start, end)
        data["result"] = "success"
    except:
        data["result"] = "error"
    return HttpResponse(json.dumps(data), content_type="application/json")
        

@api_view(["POST"])
def delete_timeslot(request):
    # Removes a timeslot, Requires id
    print("removing timeslot")
    print(request.POST["id"])
    data = dict()
    data["result"] = Timeslots.remove(request.POST["id"])
    return HttpResponse(json.dumps(data), content_type=CONTENT_TYPE)

@api_view(["POST"])
def get_meetings(request):
    # Retrieves summary info on all active meetings.
    # Returns id, name, email, date, and time.
    # (Active meetings are meetings that have not been archived)
    meetings = Meetings.objects.exclude(status = "a")  
    data = [_.to_dict(summary=True) for _ in meetings]
    return HttpResponse(json.dumps(data), content_type=CONTENT_TYPE)



@api_view(["POST"])
def get_meeting_details(request):
    # Retrieves info about a particular meeting.
    # Requires meeting id, returns objective, note, and all previous meetings with the user.
    #https://docs.djangoproject.com/en/3.0/topics/http/shortcuts/#get-object-or-404
    meeting = get_object_or_404(Meetings, pk= int(request.POST["id"]))
    return HttpResponse(json.dumps(meeting.to_dict(with_prev=True)), content_type=CONTENT_TYPE)
    

@api_view(["POST"])
def confirm_meeting(request):
    # Requires meeting id. Will send email to contact confirming meeting.
    
    meeting = get_object_or_404(Meetings, pk= int(request.POST.get("id")))
    meeting.status = "c"
    meeting.save()
    
    send_mail(
    "Meeting confirmation.",
    render_to_string( "emails/confirm_meeting.html",
        {
            "utc":meeting.start.strftime(DATE_STRF),
            "est":meeting.start.astimezone(pytz.timezone('US/Eastern')).strftime(DATE_STRF),
            "pst":meeting.start.astimezone(pytz.timezone('US/Pacific')).strftime(DATE_STRF),
        }),
        
    EMAIL,
    [meeting.contact.email],
    fail_silently=False
    )
    return HttpResponse(json.dumps({"result":"Meeting has been confirmed."}))

@api_view(["POST"])
def reschedule_meeting(request):
    # Requires meeting id. Removes meeting from DB, sends email asking to reschedule.
    meeting = get_object_or_404(Meetings, pk= int(request.POST.get("id")))
    meeting.status = "r"
    meeting.save()
    
    send_mail(
    "Meeting cancellation.",
    render_to_string( "emails/reschedule_meeting.html",
        {
            "utc":meeting.start.strftime(DATE_STRF),
            "est":meeting.start.astimezone(pytz.timezone('US/Eastern')).strftime(DATE_STRF),
            "pst":meeting.start.astimezone(pytz.timezone('US/Pacific')).strftime(DATE_STRF),
        }),
        
    EMAIL,
    [meeting.contact.email],
    fail_silently=False
    )
    return HttpResponse(json.dumps({"result":"Request to reschedule has been sent."}))


@api_view(["POST"])
def delete_meeting(request):
    # Requires meeting id. Will send email to contact confirming meeting.
    meeting = get_object_or_404(Meetings, pk= int(request.POST.get("id")))
    meeting.delete()
    return HttpResponse(json.dumps({"result":"Meeting has been deleted."}))

@api_view(["POST"])
def archive_meeting(request):
    # Requires meeting id. Removes meeting from DB, and sends sorry email to contact.
    print(request.POST.get("id"))
    meeting = get_object_or_404(Meetings, pk= int(request.POST.get("id")))
    meeting.status = 'a'
    meeting.save()
    return HttpResponse(json.dumps({"result":"Meeting has been archived."}))

@api_view(["POST"])
def get_report(request):
    # Requires report name. Returns the report as png.
    name = request.POST.get("name")
    if name == "archive":
        data = Meetings.objects.filter(status="a")
    if name == "active":
        data = Meetings.objects.exclude(status="a")
    data = [_.to_dict() for _ in data]
    return HttpResponse(json.dumps(data), content_type=CONTENT_TYPE)
    

@api_view(["POST"])
def update_note(request):
    # Updates a meeting's note in the DB.
    # Requires meeting id and note.
    meeting = get_object_or_404(Meetings, pk= int(request.POST.get("id")))
    meeting.note = request.POST.get("note")
    meeting.save()
    return HttpResponse("done")

url_patterns = [
    # Django provided urls
    path("scheduler/", include("django.contrib.auth.urls")),
    
    # Public urls
    path('scheduler', public_access_page, name="scheduler"),
    path('scheduler/get_available_times', get_available_times, name="scheduler-get-times"),
    path('scheduler/post_meeting', post_meeting, name="scheduler-post-meeting" ),
    
    # Private (protected) urls
    path('scheduler/dashboard', private_access_page, name="scheduler-dashboard"),
    path('scheduler/add_timeslot', add_timeslot, name="scheduler-add-timeslot"),
    path('scheduler/get_timeslots', get_timeslots, name="scheduler-get-timeslot"),
    path('scheduler/delete_timeslot', delete_timeslot, name="scheduler-delete-timeslot"),
    path('scheduler/get_meetings', get_meetings, name="scheduler-get-meetings"),
    path('scheduler/get_meeting_details', get_meeting_details, name="scheduler-get-meeting-details"),
    path('scheduler/update_note', update_note, name="scheduler-update-note"),
    path('scheduler/confirm_meeting', confirm_meeting, name="scheduler-confirm-meeting"),
    path('scheduler/reschedule_meeting', reschedule_meeting, name="scheduler-reschedule-meeting"),
    path('scheduler/archive_meeting', archive_meeting, name="scheduler-archive-meeting"),
    path('scheduler/delete_meeting', delete_meeting, name="scheduler-delete-meeting"),
    path('scheduler/get_report/', get_report, name="scheduler-get-report")
    
]
