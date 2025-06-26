from django.urls import path
from . import views

urlpatterns = [
    path('',views.home_view,name='home'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('register/',views.register_view,name='register'),
    path('booking-summary/', views.BookingSummaryView.as_view(), name='booking_summary'),
    path('confirm-payment/', views.ConfirmPaymentView.as_view(), name='confirm_payment'),
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    path('ride-history/', views.ride_history_view, name='ride_history'),
    path('stations/', views.stations_availability_view, name='station'),
    path('all-feedback/', views.AllFeedbackView.as_view(), name='all_feedback'), 

]
