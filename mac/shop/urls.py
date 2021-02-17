# Created manually by Srikant

from django.urls import path
from .import views

''' urlpatterns = [
    path('',views.index,name="IndexShop")
] '''

urlpatterns = [
    path('',views.index,name="IndexShop"),
    path('about/',views.about,name="AboutUs"),
    path('contact/',views.contact,name="ContactUs"),
    path('tracker/',views.tracker,name="TrackingStatus"),

    # Fetches the 'id' of the 'QuickView' Button clicked based on its 'button id' and then stores it under the name 'myid'.
    path('products/<int:myid>',views.prodview,name="ProductView"),
    
    path('search/',views.search,name="Search"),
    path('checkout/',views.checkout,name="Checkout"),

    # Endpoint for Paytm Response Page
    path('handlerequest/',views.handlerequest,name="HandleRequest"),
]