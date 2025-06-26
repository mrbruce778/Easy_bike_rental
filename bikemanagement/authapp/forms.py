from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Ride_History
from .models import Payment_Calculation
from .models import Bike, Station_Availability
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    phone_no = forms.CharField(max_length=15, label='Must be connected with Bkash/rocket/nagad')
    national_id = forms.CharField(max_length=20)
    MEMBERSHIP_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ]
    membership = forms.ChoiceField(choices=MEMBERSHIP_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm','phone_no', 'national_id', 'membership']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
    
    def save(self, commit=True):
        # Save the User instance
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            # Create a linked UserProfile
            UserProfile.objects.create(
                user=user,
                phone_no=self.cleaned_data['phone_no'],
                national_id=self.cleaned_data['national_id'],
                membership=self.cleaned_data['membership']
            )
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_no', 'national_id', 'membership']
        labels = {
            'phone_no': 'Phone No',
            'national_id': 'National ID',
            'membership': 'Membership Type',
        }
        widgets = {
            'phone_no': forms.TextInput(attrs={'placeholder': 'e.g. 019***', 'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'placeholder': 'e.g. 123456789', 'class': 'form-control'}),
            'membership': forms.TextInput(attrs={'placeholder': 'e.g. Premium', 'class': 'form-control'}),
        }
class RideHistoryForm(forms.ModelForm):
    class Meta:
        model = Ride_History
        fields = ['user', 'start_station', 'end_station']
        labels = {
            'start_station':'Start Station',
            'end_station' :'End Station',
        }
        widgets = {
            'start_station': forms.Select(attrs={'class': 'form-control'}),
            'end_station': forms.Select(attrs={'class': 'form-control'}),
        }
class PaymentCalculationForm(forms.ModelForm):
    class Meta:
        model = Payment_Calculation  # Use the imported model
        fields = [
            'payment_id',   
            'base_fare',  
            'total_amount', 
            'payment_method'
        ]
        widgets = {
            'payment_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Credit Card, Cash'
            }),
        }
class BikeBookingForm(forms.Form):
    bike = forms.ModelChoiceField(queryset=Bike.objects.all(), label="Select a Bike")
    start_station = forms.ModelChoiceField(queryset=Station_Availability.objects.all())
    end_station = forms.ModelChoiceField(queryset=Station_Availability.objects.all())
class PaymentMethodForm(forms.Form):
    PAYMENT_CHOICES = [
        ('bkash', 'Bkash'),
        ('nagad', 'Nagad'),
        ('rocket', 'Rocket'),  # Optional
        ('cash', 'Cash on Delivery')  # Optional
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        label="Select Payment Method"
    )
class FeedbackForm(forms.Form):
    transaction_id = forms.CharField(label="Transaction ID", max_length=30)
    rating = forms.IntegerField(min_value=1, max_value=5)
    comments = forms.CharField(widget=forms.Textarea)