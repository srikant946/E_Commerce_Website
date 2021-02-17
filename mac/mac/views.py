from django.shortcuts import render

                                                     # The 'index' function here gets called from 'urls.py' file of 'mac'
def index(request):                                  
    return render(request,'index.html')              # Function named 'index' created here which redirects to 'index.html' present in 'templates' folder of 'mac' file and displays it




