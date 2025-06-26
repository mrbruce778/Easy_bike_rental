from django.contrib import admin
from .models import UserProfile, Station_Availability, Bike, Ride_History, Payment_Calculation, Feedback, Gives

admin.site.register(UserProfile)
admin.site.register(Station_Availability)
admin.site.register(Bike)
admin.site.register(Ride_History)
admin.site.register(Payment_Calculation)
admin.site.register(Feedback)
admin.site.register(Gives)
