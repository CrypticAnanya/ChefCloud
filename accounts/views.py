from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .models import *
from .forms import OrderForm,CreateUserForm
from .filters import OrderFilter
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm
from .decoration import unaunthenticated_user,allowed_users,admin_only
# Create your views here.



# View to display and add products
def menu_view(request):
    products = Product.objects.all()
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menu')

    context = {'products': products, 'form': form}
    return render(request, 'accounts/menu.html', context)
@unaunthenticated_user
def registerPage(request):
    # if request.user.is_authenticated:
    #     return redirect('home')
    # else:
    form=CreateUserForm()
    if request.method=="POST":
        form=CreateUserForm(request.POST)
        if form.is_valid():
            user =form.save()
            username=form.cleaned_data.get('username')

            group =Group.objects.get(name='customer')
            user.groups.add(group)
            messages.success(request,'Account was created for'+user)
            return redirect('login')
        else:
            print(form.errors)

    context={'form':form}
    return render(request,'accounts/register.html',context)
@unaunthenticated_user
def loginPage(request):

    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        username=authenticate(request,username=username,password=password)
        if username is not None:
            login(request,username)
            return redirect('home')
        else:
            messages.info(request,"Username or Password is incorrect")
            #return render(request,'accounts/login.html',context)
    context={}
    return render(request,'accounts/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

#@login_required(login_url='login')
# @admin_only
def home(request):
    orders=Order.objects.all()
    customers=Customer.objects.all()

    total_customers=customers.count()

    total_orders=orders.count()
    delivered=orders.filter(status='Delivered').count()
    pending=orders.filter(status='Pending').count()
    context={'orders':orders,'customers':customers,'total_customers':total_customers,'total_orders':total_orders,'delivered':delivered,'pending':pending}
    return render(request,"accounts/dashboard.html",context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders=request.user.customer.order_set.all()
    print('orders',orders)
    context={'orders':orders}
    return render(request,'accounts/user.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def product(request):
    products=Product.objects.all()
    return render(request,"accounts/products.html",{'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk_test):
    customer=Customer.objects.get(id=pk_test)
    orders=customer.order_set.all()
    order_count=orders.count()

    myFilter=OrderFilter(request.GET,queryset=orders)
    orders=myFilter.qs
    context={'customer':customer,'orders':orders,'order_count':order_count,'myFilter':myFilter}
    return render(request,"accounts/customer.html",context)

@login_required(login_url='login')
def index(request):   
    return render(request,'accounts/index.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request,pk):
    OrderFormSet=inlineformset_factory(Customer,Order,fields=('product','status'),extra=10)
    customer=Customer.objects.get(id=pk)
    #form=OrderForm(initial={'customer':customer})
    formset=OrderFormSet(queryset=Order.objects.none(),instance=customer)
    if request.method=="POST":
        #form =OrderForm(request.POST)
        formset=OrderFormSet(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
        
    context={'formset':formset}
    return render(request,'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):
    order=Order.objects.get(id=pk)
    form=OrderForm(instance=order)
    if request.method=="POST":
        form =OrderForm(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context={'form':form}
    return render(request,'accounts/update_order.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order=Order.objects.get(id=pk)
    if request.method=="POST":
        order.delete()
        return redirect('/')
    context={'item':order}
    return render(request,'accounts/delete.html',context)

# @login_required(login_url='login')
# def deleteProduct(request,pk):
#     products=Product.objects.get(id=pk)
#     if request.method=="POST":
#         products.delete()
#         return redirect('/')
#     context={'item': products}
#     return render(request,'accounts/delete.html',context)