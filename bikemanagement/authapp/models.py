from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_no = models.CharField(max_length=15)
    national_id = models.CharField(max_length=20)
    membership = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500.0)
    
    def __str__(self):
        return self.user.username

class Station_Availability(models.Model):
    station_id = models.CharField(max_length=10, primary_key=True)
    location = models.CharField(max_length=100)
    available_time = models.CharField(max_length=50)
    position = models.IntegerField()
    
    class Meta:
        db_table = 'station_availability'
    
    def __str__(self):
        return self.station_id

class Bike(models.Model):
    number_plate = models.CharField(max_length=20, primary_key=True)
    current_station = models.ForeignKey(
        Station_Availability, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='bikes'
    )
    milage = models.FloatField()
    design = models.CharField(max_length=50)
    engine_size = models.CharField(max_length=20)
    technology = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'bike'
    
    def __str__(self):
        return self.number_plate

class Gives(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_column='national_id')
    feedback_id = models.ForeignKey('Feedback', on_delete=models.CASCADE, db_column='feedback_id')
    
    class Meta:
        db_table = 'user'
    
    def __str__(self):
        return self.user_profile.user.username

class Payment_Calculation(models.Model):
    payment_id = models.CharField(max_length=20, primary_key=True)
    base_fare = models.FloatField()
    total_amount = models.FloatField()
    payment_method = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'payment_calculation'
    
    def __str__(self):
        return self.payment_id

class Ride_History(models.Model):
    ride_no = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride_date = models.DateTimeField(default=timezone.now)
    start_station = models.ForeignKey(
        Station_Availability,
        on_delete=models.SET_NULL,
        null=True,
        related_name='rides_started_here',
        db_column='start_station_id'
    )
    end_station = models.ForeignKey(
        Station_Availability,
        on_delete=models.SET_NULL,
        null=True,
        related_name='rides_ended_here',
        db_column='end_station_id'
    )
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE, db_column='bike_number_plate')
    payment_id = models.ForeignKey(Payment_Calculation, on_delete=models.CASCADE, db_column='payment_id')
    
    class Meta:
        db_table = 'ride_history'
    
    def __str__(self):
        return str(self.ride_no)

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_name')
    rating = models.IntegerField()
    comments = models.TextField()
    
    class Meta:
        db_table = 'feedback'
    
    def __str__(self):
        return str(self.feedback_id)