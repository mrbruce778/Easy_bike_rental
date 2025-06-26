from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View 
from django.contrib.auth.models import User
from .forms import RegisterForm
from .forms import BikeBookingForm, PaymentMethodForm, FeedbackForm
from .models import Payment_Calculation, Ride_History, Bike, Station_Availability, Feedback,UserProfile, Gives
from django.shortcuts import get_object_or_404
import uuid
from django.db.models import Prefetch
from django.db.models import Count
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Check if UserProfile already exists
            if not UserProfile.objects.filter(user=user).exists():
                UserProfile.objects.create(
                    user=user,
                    phone_no='',
                    national_id='',
                    membership='standard',
                    balance=500.0  # Initialize with a default balance of 500
                )

            login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/register.html', {'form': form})
    else:
        form = RegisterForm()
        return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            error_message = "Invalid Credentials"
    return render(request,'accounts/login.html',{'error': error_message})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    else:
        return redirect('home')

@login_required
def home_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None  # or handle it some other way
    context = {'profile': user_profile}
    return render(request, 'auth1_app/home.html', context)

@login_required
def stations_availability_view(request):
    stations = Station_Availability.objects.prefetch_related(
        Prefetch('bikes')
    ).annotate(available_bikes=Count('bikes'))
    
    return render(request, 'auth1_app/stations_availablity.html', {'stations': stations})


class AllFeedbackView(LoginRequiredMixin, View):
    def get(self, request):
        # Fetch all feedbacks (user-specific and universal) from the database
        feedbacks = Feedback.objects.all().order_by('-feedback_id')  # Adjust ordering as needed
        
        return render(request, 'auth1_app/all_feedback.html', {'feedbacks': feedbacks})

@login_required
def ride_history_view(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None  # or handle this case appropriately

    rides = Ride_History.objects.filter(user=request.user).order_by('-ride_date')

    context = {
        'user_profile': user_profile,
        'rides': rides,
    }
    return render(request, 'auth1_app/ride_history.html', context)

class BookingSummaryView(LoginRequiredMixin, View):
    def get(self, request):
        form = BikeBookingForm()
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        return render(request, 'registration/booking_summary.html', {
            'form': form,
            'user_profile': user_profile
        })

    def post(self, request):
        form = BikeBookingForm(request.POST)
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        if form.is_valid():
            bike = form.cleaned_data['bike']
            start_station = form.cleaned_data['start_station']
            end_station = form.cleaned_data['end_station']

            if bike.current_station != start_station:
                messages.error(request, f"The selected bike {bike.number_plate} is not available at the chosen start station.")
                return render(request, 'registration/booking_summary.html', {
                    'form': form,
                    'user_profile': user_profile
                })

            hops = abs(start_station.position - end_station.position)
            price_per_hop = 20.0
            total_amount = hops * price_per_hop

            if user_profile.balance < Decimal(str(total_amount)):
                messages.error(request, f"Insufficient balance. You need {total_amount} but have {user_profile.balance}.")
                return render(request, 'registration/booking_summary.html', {
                    'form': form,
                    'user_profile': user_profile
                })

            # ✅ Just save booking data to session, NOT to the database yet
            request.session['booking_data'] = {
                'bike_id': bike.number_plate,
                'start_station_id': start_station.station_id,
                'end_station_id': end_station.station_id,
                'price_per_hop': float(price_per_hop),
                'total_amount': float(total_amount)
            }

            return redirect('confirm_payment')  # now go to confirmation page

        return render(request, 'registration/booking_summary.html', {
            'form': form,
            'user_profile': user_profile
        })


from django.db import transaction

class ConfirmPaymentView(LoginRequiredMixin, View):
    def get(self, request):
        # If no session data, redirect to booking summary
        booking = request.session.get('booking_data')
        if not booking:
            return redirect('booking_summary')

        bike = get_object_or_404(Bike, number_plate=booking['bike_id'])
        start_station = get_object_or_404(Station_Availability, station_id=booking['start_station_id'])
        end_station = get_object_or_404(Station_Availability, station_id=booking['end_station_id'])
        
        context = {
            'bike': bike,
            'start_station': start_station,
            'end_station': end_station,
            'total_amount': booking['total_amount'],
            'price_per_hop': booking['price_per_hop']
        }
        return render(request, 'registration/confirmpayment.html', context)

    def post(self, request):
        booking = request.session.get('booking_data')
        if not booking:
            return redirect('booking_summary')

        form = PaymentMethodForm(request.POST)
        user_profile = get_object_or_404(UserProfile, user=request.user)

        if form.is_valid():
            bike = get_object_or_404(Bike, number_plate=booking['bike_id'])
            start_station = get_object_or_404(Station_Availability, station_id=booking['start_station_id'])
            end_station = get_object_or_404(Station_Availability, station_id=booking['end_station_id'])
            total_amount = Decimal(str(booking['total_amount']))

            # Check if the user has enough balance
            if user_profile.balance < total_amount:
                messages.error(request, f"Insufficient balance. You need {total_amount} but have {user_profile.balance}.")
                return redirect('booking_summary')

            # Create Payment_Calculation object
            payment = Payment_Calculation.objects.create(
                payment_id=f"PAY-{uuid.uuid4().hex[:8].upper()}",
                base_fare=booking['price_per_hop'],
                total_amount=booking['total_amount'],
                payment_method=form.cleaned_data['payment_method']
            )

            try:
                # Use a transaction to ensure atomicity of operations
                with transaction.atomic():
                    # Create the Ride_History entry
                    ride = Ride_History.objects.create(
                        user=request.user,
                        bike=bike,
                        start_station=start_station,
                        end_station=end_station,
                        payment_id=payment,
                        ride_date=timezone.now()
                    )

                    # *** Update bike's station to end_station ***
                    bike.station = end_station
                    bike.save()

                    # Deduct balance
                    user_profile.balance -= total_amount
                    user_profile.save()

                    # Save ride and payment data in session
                    request.session['ride_id'] = ride.ride_no
                    request.session['current_payment_pk'] = payment.pk

                return redirect('feedback')

            except Exception as e:
                payment.delete()
                form.add_error(None, f"Error processing booking: {str(e)}")
        
        # If form is invalid
        bike = get_object_or_404(Bike, number_plate=booking['bike_id'])
        start_station = get_object_or_404(Station_Availability, station_id=booking['start_station_id'])
        end_station = get_object_or_404(Station_Availability, station_id=booking['end_station_id'])

        context = {
            'bike': bike,
            'start_station': start_station,
            'end_station': end_station,
            'total_amount': booking['total_amount'],
            'price_per_hop': booking['price_per_hop'],
            'payment_form': form
        }
        return render(request, 'registration/confirmpayment.html', context)

class FeedbackView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'registration/feedback.html', {'form': FeedbackForm()})

    def post(self, request):
        form = FeedbackForm(request.POST)
        if form.is_valid():
            transaction_id = form.cleaned_data['transaction_id']
            rating = form.cleaned_data['rating']
            comments = form.cleaned_data['comments']

            payment_pk = request.session.get('current_payment_pk')  # ✅ Use payment PK
            if not payment_pk:
                form.add_error(None, "Session expired. Cannot find payment.")
                return render(request, 'registration/feedback.html', {'form': form})

            try:
                # Get the Payment_Calculation object via PK
                payment = Payment_Calculation.objects.get(pk=payment_pk)

                # ✅ Replace temporary payment_id with actual transaction ID
                payment.payment_id = transaction_id
                payment.save()

                # Create the Feedback object
                feedback = Feedback.objects.create(
                    user=request.user,
                    rating=rating,
                    comments=comments
                )

                # Ensure UserProfile exists
                user_profile, created = UserProfile.objects.get_or_create(user=request.user)

                # Link feedback to user via Gives model
                Gives.objects.create(
                    user_profile=user_profile,
                    feedback_id=feedback
                )

                # Optionally clean up session keys
                request.session.pop('current_payment_pk', None)
                request.session.pop('ride_id', None)

                messages.success(request, "Payment confirmed and feedback submitted! Thank you for using.")
                return redirect('home')

            except Payment_Calculation.DoesNotExist:
                form.add_error(None, "Payment record not found.")

        # If form is invalid or error occurred
        return render(request, 'registration/feedback.html', {'form': form})
