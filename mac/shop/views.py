from django.shortcuts import render
from django.http import HttpResponse
from .models import Product , Contact , Orders ,OrderUpdate
from math import ceil
import json                                     # Importing for using json.dumps functionality
from django.views.decorators.csrf import csrf_exempt    # Importing this decorator for bypassing CSRF token for handlerequest() function
from PayTm import Checksum                    # Importing for ChecksumHash Functionality
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5';            # Test Merchant Key provided by PayTm      
# Create your views here.

def index(request):
    allProds=[]                                                # Empty List created which would later be passed onto 'index.html' file for controlling various Carousels 
    catprods = Product.objects.values('category','id')         # 'catprods' variable stores the value from 'Product' class variables namely 'id' and 'category'
    cats = {item['category'] for item in catprods}             # Since we have accepted both the values in 'catprods' we use a set comprehension only to consider 'category' values and then we use a 'for' loop
    for cat in cats:                                           # 'cat' here refers a variable which iterates through the category value received in 'cats'
        prod = Product.objects.filter(category=cat)            # Here we pass the 'Product' class's variable i.e category for filtering and we store the final category value after filtering in 'prod'.
        n = len(prod)                                          # We then calculate length of 'prod'
        nSlides = n//4 + ceil((n/4) - (n//4))                  # Slide Logic which helps us to decide how many slides would be created based on the no of products.
        allProds.append([prod , range(1,nSlides), nSlides])    # Then, we append 'allProds' list with our current 'prod' values + provide a range to it along with nSlides.

    ''' Creating Carousel and using Slide Logic '''
    # params ={'no_of_slides': nSlides,'range': range(1,nSlides),'product': products}

    params ={'allProds':allProds}                              # The 'allProds' list is then passed as 'params' to the 'render' function.
    return render(request,'shop/index.html',params)        # No need to add 'templates' folder in argument because each folder has its own template folder and we refer it within referring the file..i.e 'shop' here is the template folder

# Function which tests whether the entered 'query' variable value matches the corresponding database 'attribute'.
# '.lower()'is used to prevent Only LowerCase from being searched.
# Also it takes in the 'query' received from the 'search' function of 'views.py' file and it takes in a local variable named 'item' which corresponds to the 'Product' model Attribute.
def searchMatch(query,item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    elif query in item.desc.capitalize() or query in item.product_name.capitalize() or query in item.category.capitalize():
        return True
    elif query in item.desc.upper() or query in item.product_name.upper() or query in item.category.upper():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')                        # Whatever We pass into the Search Box is then stored in 'query' variable.
    # Same logic as that of 'index' file
    allProds=[]                                  
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)

        # First item gets searched into categories and then the 'searchMatch' function is called
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nSlides = n//4 + ceil((n/4) - (n//4))

        # 'if' written so that whenever our 'search' fails then instead of 'Bootstrap' getting messed up..a blank page appears
        if len(prod)!= 0:
            allProds.append([prod , range(1,nSlides), nSlides])

    # If user enters correct data only the product is to be shown so NO 'msg' is passed over here.
    params ={'allProds':allProds}

    # If User searches wrong data i.e if 'allProds' length remains 0 or if user searches only 3 letters in the search box the following 'msg' is passed through the 'params' dict and displayed on the page
    if len(allProds) == 0 or len(query)<4 :
        params = {'msg': "Please Enter Relevant Data capable of being searched"}

    return render(request,'shop/search.html',params)        # No need to add 'templates' folder in argument because each folder has its own template folder and we refer it within referring the file..i.e 'shop' here is the template folder


def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.method=="POST":                                                # Execute On 'POST' method getting called..
        name = request.POST.get('name','')                                    # request.POST.get() is used to fetch the values sent through the POST method of the form.
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        print(name,email,phone,desc)
        contact = Contact(name=name,email=email,phone=phone,desc=desc)        # Here the first field is of DB and second field is of the value that we fetched in the above lines.
        contact.save()                                                        # Save the changes made in the database
    return render(request,'shop/contact.html')                                # Return back to 'contact.html' page.

def tracker(request):
    if request.method=="POST":                                                # On submission of the details in 'tracker.html' page
        orderId = request.POST.get('orderId', '')                             # Fetch the orderid entered by its 'id' mentioned in the form field over there
        email = request.POST.get('email', '')                                 # Fetch the email entered by its 'id' mentioned over there in the form field
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)      # From 'Orders' DB va;lidate on the basis of email and Order id
            if len(order)>0:                                                  # If order exists
                update = OrderUpdate.objects.filter(order_id=orderId)         # Once validation is done then filter order on the basis of orderid and store its data as mentioned in 'OrderUpdate' DB in a variable called 'update'
                updates = []                                                  # Create a blank list which would display all the data related to a particular order.
                for item in update:                                           # Iterate through the OrderUpdate DB
                    updates.append({'text': item.update_desc, 'time': item.timestamp})  # Append the text present in that corresponding OrderUpdate Record in 'updates' list
                    
                    # Here the value of 'updates' which stores the data that is successfully fetched from the DB is displayed + we also refer to the order currently addressed using 'items_json' attribute of the 'Order' model.
                    response = json.dumps({'status':'success','updates': updates,'itemsJson': order[0].items_json},default=str) # 'default=str' added in order to prevent JSON Serializable Exception from occuring 
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    return render(request, 'shop/tracker.html')


def prodview(request,myid):

    # Fetching the Product using the id 
    # 'myid' is used to refer to the 'button' which was clicked, by function 'prodview' in 'views.py' file due to which it takes 'myid' also as a parameter.
    product = Product.objects.filter(id=myid)

    # On filtering by 'id' we COMPULSORILY mention dictionary i.e 'product' value as product[0] because only 1 item can be fetched at a time... If not mentioned..then display would be left blank 
    return render(request,'shop/prodview.html',{'product': product[0]})

def checkout(request):
    if request.method=="POST":                            # Receive the 'POST' request from the form in 'checkout.html'
        items_json = request.POST.get('itemsJson','')     # The value obtained after submitting the form is stored in 'id' named 'ItemJson' and it is passed over here in this function's variable named 'items_json'
        name = request.POST.get('name','')
        amount = request.POST.get('amount','')
        email = request.POST.get('email','')
        address = request.POST.get('address1','') + " " + request.POST.get('address2','') # Accepting data entered in 2 address fields and concatenating them together and storing them in the DB
        city = request.POST.get('city','')
        state = request.POST.get('state','')
        zip_code = request.POST.get('zip_code','')
        phone = request.POST.get('phone','')

        # First is the Database attribute name and second is the variable name as defined in the function 'checkout'
        order = Orders(items_json=items_json,name=name,email=email,address=address,city=city,state=state,zip_code=zip_code,phone=phone,amount=amount)
        order.save()     # Save the changes to the database

        update = OrderUpdate(order_id=order.order_id,update_desc="The Order has been placed")
        update.save()

        thank = True            # 'thank' variable created here with value 'True' which is referenced in 'checkout.html'
        id = order.order_id     # 'id' is obtained based on the current id of the product as mentioned in the database.This too is referenced in 'checkout.html'        
        # return render(request,'shop/checkout.html', {'thank':thank,'id':id})
        
        # Request Paytm to transfer the amount to your account after payment by user.
        param_dict = {
            'MID':'WorldP64425807474247',
            'ORDER_ID':str(order.order_id),           # For making it iterable we convert it to 'str' type
            'TXN_AMOUNT':str(amount),                 # For making ititerable we convert it to 'str' type
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',                   # 'WEBSTAGING' written for testing
            'CHANNEL_ID':'WEB',
            
            # CALLBACK_URL is the URL where PayTm would send us a request.
	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
        }

        # Generating checksum For secure transaction...
        # We initially import Checksum from PayTm directory over here.
        # Then we use the generate_checksum method which takes in 2 arguments i.e (param_dict and Merchant Key) 
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict,MERCHANT_KEY)

        # The user then redirects to paytm.html after the payment procedure along with 'param_dict' values.
        return render(request, 'shop/paytm.html', {'param_dict' : param_dict})

    return render(request,'shop/checkout.html')

@csrf_exempt                                  # CSRF Exempt Section begins here
def handlerequest(request):                   # Function named handlerequest
    
    form = request.POST                       #Paytm will send you post request
    response_dict = {}                        # An empty dictionary which is referred by a variable named 'response_dict' is created
    for i in form.keys():                     # 
        response_dict[i] = form[i]            # All the Keys from the POST Request would be fetched and stored in 'response_dict' dictionary
        if i == 'CHECKSUMHASH':               # We check if any key in the dictionary is equal to CHECKSUMHASH or not
            checksum = form[i]                # If yes then the corresponding checksum data is stored in a variable called 'checksum'

    # A function called verify_checksum is then created which is an built-in function of Checksum.py file and it takes in 3 parameters
    # The parameters are response_dict which stores the keys,MERCHANT_KEY which refers to the merchant key of the Service Provider (Here, MyAwesomeCart) and 'checksum' refers to the checksum obtained after matching with CHECKSUMHASH
    verify = Checksum.verify_checksum(response_dict,MERCHANT_KEY, checksum)
    if verify:

        # If RESPCODE received from 'response_dict' is 01 then Order is successful
        if response_dict['RESPCODE'] == '01':
            print("Order Successful")
        else:
            # If Order is unsuccessful then print about it and display RESPMSG displaying the error.
            print('Order Was not successful because' + response_dict['RESPMSG'] )

    # Send Status of the above operation to 'paymentstatus.html' page along with the 'response_dict' data
    return render(request, 'shop/paymentstatus.html', {'response':response_dict})

    pass