# Readme
## Gavin Ray's Scheduler

- [Readme](#readme)
  - [Gavin Ray's Scheduler](#gavin-rays-scheduler)
- [1. Introduction](#1-introduction)
- [2. Accessibility](#2-accessibility)
- [3. Security](#3-security)
- [4. Documentation](#4-documentation)
    - [API ENDPOINTS](#api-endpoints)
    - [DATABASE MODELS](#database-models)
      - [**Contacts**](#contacts)
      - [**Meetings**](#meetings)
      - [**Timeslots**](#timeslots)
- [5. INSTALL INSTRUCTIONS](#5-install-instructions)
# 1. Introduction
This project was started as a capstone project representing knowledge I gained while studying at WGU, as well as experience I built working with Python and Django prior to my time at WGU. I hope it will give you a good idea of my abilities with these amazing tools. Building this program has been a great experience for me. I started working on the initial prototype in November 2022. It included a web page built with JS, CSS, and html that simulated a meeting scheduler. Starting in early December, I start to transform this prototype into a full-stack application using the RAD methodology. It is now January 4, 2023, and the program is ready to be placed into production.

In the future I will host this program on Heroku and use it for managing my day-to-day meeting schedule. I also have plans to build a second app into the site that will act as an "about me" page with links to my resume, etc. After that, who knows! I might add more apps for other projects as they come up.
# 2. Accessibility

All images have alt value.

I also used the "sr-only" bootstrap class to provide additional instructions to individuals who use screen readers. For example, I was worried that selecting a meeting time would be confusing without the ability to actually see how the times are updated. By including an sr-only div just before the time-list, I am able to provide additional instructions that are only visible to screen readers.

"< h1 class="sr-only">The following day-list includes all the days in which I have availability for the selected duration.</h1>" --templates/public_access_page.html, line 51

# 3. Security

Django is configured to provide several security features:

--By using the ORM layer, django will prevent sql injections. Check out [StackHawk blog](https://www.stackhawk.com/blog/sql-injection-prevention-django/) for more information. 

--User authentication is being accomplished with Django's built-in User model. All POST uri's will require a user to be logged in to access them. If a user is not logged in, they are prompted to provide a username and password that can be matched with a record in the User table of the database. Creating Users can be done via the command line, or directly to the database with SQL. Users only have to log in once, after which a validating token is stored in a cookie on their machine. For now, this token does not expire.

--Session validation and tracking is done with CSRF cookies. This prevents cross site request forgery attacks.

--Automatic redirect to HTTPS if user tries to connect with HTTP is done by setting HTTPS only in mysite/settings.


# 4. Documentation

### API ENDPOINTS
All endpoints for the scheduler are located in Scheduler/views.py. URL patterns can be found at the bottom of the page. They are as follows:

**scheduler** [GET] This is a publicly accessible entrypoint to the scheduler. The scheduler can be used to schedule meetings with me.

**scheduler/get_available_times** [GET] This endpoint returns a list of [start, end] datetimes that represent potential meeting times that can be booked by the end-user.

**scheduler/post_meeting** [GET] Once an end-user has selected a start date and time, as well as inputted a valid email address, this endpoint allows for the actual booking of the meeting. Name and meeting objective can also be provided but are not required.

**scheduler/dashboard** [GET] This is the entry point for accessing the scheduler's dashboard. The dashboard is used to create available meeting times (timeslots), review upcoming meetings, and update the status of meetings, among other things. Accessing this dashboard requires a valid username and password.

**scheduler/add_timeslot** [POST] Used to add availability to my schedule. Requires start and end datetimes in iso format representing a period of time in which meetings can be scheduled.

**scheduler/get_timeslots** [GET] Returns a list of of [start, end] datetimes for every timeslot within a one week period. Requires a date in iso format that will be used as the beginning of the one week period to query.

**scheduler/delete_timeslot** [POST] When supplied with a timeslot ID, that timeslot will be removed from the database.

**scheduler/get_meetings** [POST] Returns summaries for all active meetings. An active meeting is one that does not have a status of "a" (archived). 

**scheduler/get_meeting_details** [POST] When supplied with a valid meeting ID, returns meeting information (non-summarized), including data on all other meetings that have been scheduled by the same end-user.

**scheduler/update_note** [POST] Requires meeting ID and a string to be used to update the note field for the meeting.

**scheduler/confirm_meeting** [POST] Used to change the status of a meeting from "u" (unconfirmed) to "c" (confirmed). Also triggers an email to be sent to the end-user notifying them that the meeting has been confirmed.

**scheduler/reschedule_meeting** [POST] Used to change the status of a meeting to "r" (rescheduled), effectively cancelling the meeting. An email is also sent to the end-user notifying them that the meeting is cancelled.

**scheduler/archive_meeting** [POST] Used to change the status of a meeting to "a" (archived). This can be done after a meeting takes place, and prevents that meeting from showing when the dashboard is first loaded.

**scheduler/delete_meeting** [POST] This endpoint will remove a meeting entirely from the database. No emails are sent, and no record of the meeting is kept. This endpoint should only be used if an end-user cancels, and the meeting time needs to be freed up for another user.

**scheduler/get_report/** [POST] This endpoint allows access to CSV formatted meeting data. As of now, only two reports are available. If parameter name=="archive", all archived meetings will be included. If name=="active", all non-archived meetings will be sent.

### DATABASE MODELS

The Scheduler/models.py file includes 3 custom models which define 3 sql tabels. This is in addition to the Django default tables that are made. The only Django table used by this program is "Users".

#### **Contacts**
Contacts are people who schedule appointments through the site. No authentication is necessary to become a contact, although an email is necessary to receive confirmation and zoom link for the meeting.

Attributes / Fields:
- created_on: *DateTimeField* Records the datetime that the contact first appeared in the database.
- updated_on: *DateTimeField* Records the datetime for the most recent update made to the contact.
- name: *CharField* The contacts name.
- email: *EmailField* The contacts email address.
  
Static Methods:
- create(name, email): Will create a new contact, or update 'name' on existing contact with the given email.

#### **Meetings**
Meetings store information about all meetings, including date time, objectives, and status, etc.

Attributes / Fields:
- contact: *ForeignKey(Contacts)* On delete CASCADE
- start: *DateTimeField* Starting date and time for the meeting, stored as UTC.
- end: *DateTimeField* Ending date and time for the meeting, stored as UTC.
- duration: *IntegerField* Number of minutes the meeting is planned to take.
- objective: *CharField* Contacts can provide objectives for the meeting.
- note: *CharField* Every meeting can be given a description by a SuperUser.
- status: *CharField* Supports "u" (unconfirmed), "c" (confirmed), "r" (rescheduled), "a" (archived).

Static Attributes
- valid_durations: [15,30,45,60,90,120] Used to limit meetings to these durations.

Static Methods:
- during_period(start, end): Returns all meetings that start and end within the given datetimes.
- create(start, end, duration, objective, contact): Creates meeting, ensuring no other meetings exist at same time
  
Instance Methods:
- to_dict(summary=False, with_prev=False): Returns a serializable version of the meeting as either a summary, full data, or with all previous meetings that this meeting's Contact has made. 
  
#### **Timeslots**
Timeslots are date and time periods that a SuperUser has designated as available for scheduling. Only times within a Timeslot can be scheduled by Contacts.

Attributes / Fields:
- start: *DateTimeField* Starting datetime for the timeslot.
- end: *DateTimeField* Ending datetime for the timeslot.

Static Methods:
- during_period(start, end): Finds any timeslots start and end within the given datetimes
- create(start, end): Adds a timeslot to the database that starts and ends at the times given. If a Timeslot already exists within the period, they will be combined.
- remove(id): Completely removes any timeslot by id. This does not affect any meetings scheduled during the timeslot, but will prevent additional meetings.
- contains(start, end): Returns all timeslots that exist during the start and end datetimes args.
  
Instance Methods:
- to_dict(): Returns serializable data by converting datetimes to iso formatted strings.
- open_times(): Returns list of [open,close] times that a meeting can be scheduled between. It does this by looking at all meetings that have been scheduled during this timeslot, and then determining what time periods are still available.

# 5. INSTALL INSTRUCTIONS
This repo is configured to be run on Heroku. However, during development I ran it locally with a mysql database. It can easily be turned back into a local development server by following these steps.


1. run command: pip install -r requirements.txt
   --Installs Python dependencies from requirements.txt.
2. In mysite/settings, comment out lines 93-102. Comment in lines 85-90. This will switch from postgresql to mysql.
3. run command: python manage.py migrate 
   --Creates the database tables necessary for the program
4. run command: python manage.py createsuperuser
   --When prompted, input credentials. These credentials will be needed for accessing the scheduling dashboard.
5. run command: python manage.py collectstatic
   --This will compress all static files into staticfiles dir at root. 
6. run command: python manage.py runserver
   --Starts the web server locally.
