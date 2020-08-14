from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import OrderItem, Order
from .forms import OrderCreatedForm
from cart.cart import Cart
from .tasks import order_created


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/order_detail.html',
                  {'order': order})


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreatedForm(request.POST)
        if form.is_valid():
            order = form.save()

            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # clear cart
            cart.clear()
            # launch asynchronous task
            order_created.delay(order.id)
            # set the order in session
            request.session['order_id'] = order.id
            # redirect fot payment
            return redirect(reverse('payment:process'))
            # return render(request, 'orders/order_created.html', {'order': order})

    else:
        form = OrderCreatedForm()

    return render(request, 'orders/order_create.html',
                  {'cart': cart, 'form': form })
