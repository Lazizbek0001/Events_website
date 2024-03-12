from django.db import models
from django.contrib.auth.models import User
from datetime import date





class Venue(models.Model):
    name = models.CharField('Venue name', max_length=120)
    address = models.CharField(max_length = 300)
    zip_code = models.CharField('Zip code', max_length = 15)
    phone = models.CharField('Contact Phone', max_length=25, blank = True)
    web = models.URLField('Website Address')
    email_address = models.EmailField('Email Address', blank = True)
    owner = models.IntegerField("Venue Owner", blank=False, default=1)
    venue_image = models.ImageField(null=True, blank=True, upload_to="images/")
    def __str__(self):
        return self.name
    
    
    
class MyClubUsers(models.Model):
    first_name = models.CharField(max_length = 20)
    last_name = models.CharField(max_length= 25)
    email = models.EmailField('User Email')


    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
    
    

class Event(models.Model):
    name = models.CharField('Event name', max_length=100)
    event_date = models.DateTimeField('Event date', )
    venue = models.ForeignKey(Venue, blank = True, null = True, on_delete = models.CASCADE)
    # venue = models.CharField(max_length = 120)
    manager = models.ForeignKey(User, blank = True, null = True, on_delete=models.SET_NULL)
    description = models.TextField(blank = True)
    attendees = models.ManyToManyField(MyClubUsers, blank=True)
    approved = models.BooleanField("Approved", default=False)
    
    def __str__(self):
        return self.name
    
    
    @property
    def Days_till(self):
        today = date.today()
        days_till = self.event_date.date() - today
        days_till_stripped = str(days_till).split(",", 1)[0]
        days = str(days_till_stripped).split(" ", 1)[0]
        days = int(days)

        if days > 0 and days !=0:
            string = f"{days} days left"
        elif days <0 and days != 0:
            string = "You are too late to attend this event"
            
        return string
    
    
    

class Video(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.title