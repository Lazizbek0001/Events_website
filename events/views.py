from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from django.http import HttpResponseRedirect
from datetime import datetime
from .models import Event, Venue, Video

from django.contrib.auth.models import User

from .forms import VenueForm, EventForm, EventFormAdmin, VideoForm

from django.http import HttpResponse

import csv

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from django.core.paginator import Paginator

from django.contrib import messages

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'events/video_list.html', {'videos' : videos})

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to a view where you list all uploaded videos
    else:
        form = VideoForm()
    return render(request, 'events/upload_video.html', {'form': form})



def show_event(request, event_id):
    event = Event.objects.get(pk=event_id)

    return render(request, 'events/show_event.html', {'event':event})

def venue_events(request, venue_id):
    venue = Venue.objects.get(id= venue_id)
    events = venue.event_set.all()
    if events:
        return render(request, 'events/venue_events.html', {'events': events})
    else:
        messages.success(request, ('That venue holds no events...'))
        return redirect('admin_approval')
        
def admin_approval(request):
    #Get the venues
    venue_list = Venue.objects.all()
    
    # Get counts
    event_count = Event.objects.all().count()
    venue_count = Venue.objects.all().count()
    user_count = User.objects.all().count()
    event_list = Event.objects.all().order_by('-event_date')
    if request.user.is_superuser:
        if request.method == "POST":
            id_list = request.POST.getlist('boxes')
            event_list.update(approved=False)
            
            
            for x in id_list:
                Event.objects.filter(pk=int(x)).update(approved=True)
            
            messages.success(request, ("Your approval has been updated!"))
            return redirect('admin_approval')
        
        else:
            return render(request, 'events/admin_approval.html', {'event_list': event_list,
            'event_count':event_count,
            'venue_count':venue_count,
            'user_count':user_count,
            'venue_list': venue_list})
    else:
        messages.success(request, ('You are not allowed to see this page'))
        return redirect('home')

def search_events(request):
    if request.method == "POST":
        searched=request.POST['searched']
        events = Event.objects.filter(name__contains = searched)
        return render(request, 'events/search_event.html', 
                  {'searched':searched,
                   'events':events})
    else:
        return render(request, 'events/search_event.html', 
                  {})


def my_events(request):
    if request.user.is_authenticated:
        me = request.user.id
        event = Event.objects.filter(attendees=me)
        return render(request, 'events/my_events.html', {'event': event})
    else:
        messages.success(request, ("You aren't autherized to view this page"))
        return redirect('home')
    
def venue_pdf(request):
    buf = io.BytesIO()
    can = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = can.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)
    # lines = ["This line 1","This line 2","This line 3"]
    venue = Venue.objects.all()

    lines = []
    lines.append("                  Venues")
    for venue in venue:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append("===============================")
        lines.append(" ")
        
    for line in lines:
        textob.textLine(line)
        
    can.drawText(textob)
    can.showPage()
    can.save()
    buf.seek(0)
    
    return FileResponse(buf, as_attachment=True, filename='venue.pdf')


def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'
    venues = Venue.objects.all()
    
    writer  = csv.writer(response)
    
    writer.writerow(['Venue Name', 'Address', 'Zip Code', 'Phone', 'Web Address','Email'])
    

    for venue in venues:
        writer.writerow([venue.name,venue.address,venue.zip_code,venue.phone,venue.email_address,venue.web])


    return response




def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=venues.txt'
    venues = Venue.objects.all()
    lines = []
    for venue in venues:
        lines.append(f'{venue.name}\n{venue.address}\n{venue.zip_code}\n{venue.phone}\n{venue.email_address}\n{venue.web}\n\n\n')
        
    
    response.writelines(lines)
    return response

def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')

def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:
        event.delete()
        messages.success(request,("Event deleted"))
        return redirect('list-events')
    else:
        messages.success(request, ("You aren't autherized to delete an event"))
        return redirect('list-events')


def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)

    if form.is_valid():
        form.save()
        return redirect('list-events')
    return render(request, 'events/update_event.html', 
                  {'event' : event,
                   'form':form})

def add_event(request):
    submitted = False
    if request.method == 'POST':
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        
            
        else:
            form = EventFormAdmin(request.POST)
            venue = form.save(commit=False)
            venue.owner = request.user
            venue.save()
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
            
        
    else:
        if request.user.is_superuser:
            
            form = EventFormAdmin
        else:
        
            form = EventForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'events/add_event.html', {'form':form, 'submitted' : submitted})


def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None,request.FILES or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')
    return render(request, 'events/update_venue.html', 
                  {'venue' : venue,
                   'form':form})

def search_venues(request):
    if request.method == "POST":
        searched=request.POST['searched']
        venues = Venue.objects.filter(name__contains = searched)
        return render(request, 'events/search_venues.html', 
                  {'searched':searched,
                   'venues':venues})
    else:
        return render(request, 'events/search_venues.html', 
                  {})
def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    
    events = venue.event_set.all()
    return render(request, 'events/show_venue.html', 
                  {'venue' : venue, 'venue_owner':venue_owner, 'events':events})

def list_venues(request):
    # list_venue = Venue.objects.all().order_by('name')
    list_venue = Venue.objects.all()
    # Pagination
    p = Paginator(Venue.objects.all(), 5)
    page = request.GET.get('page')
    venues = p.get_page(page)
    nums = "a" * venues.paginator.num_pages
    
    return render(request, 'events/venue.html', 
                  {'list_venue' : list_venue, 'venues': venues, 'nums':nums})


def add_venue(request):
    submitted = False
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user.id
            venue.save()
            # form.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
        
        
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True
  
    return render(request, 'events/add_venue.html', {'form':form, 'submitted' : submitted})

def all_events(request):
    event_list = Event.objects.all().order_by('event_date')
    return render(request, 'events/event_list.html', 
                  {'event_list' : event_list,})

def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = 'Laziz'
    # Convert month from str to number
    month = month.capitalize()
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    
    cal = HTMLCalendar().formatmonth(year, month_number)
    now = datetime.now()
    current_year = now.year
    
    event_list = Event.objects.filter(
        event_date__year = year,
        event_date__month = month_number,
    )
    
    time = now.strftime('%I:%M:%p:%D')
    return render(request, 'events/home.html', {
        'name': name,
        'year': year,
        'month':month,
        'month_number': month_number,
        'cal' : cal,
        'current_year': current_year,
        'time':time,
        'event_list':event_list
    })