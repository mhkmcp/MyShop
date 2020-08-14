from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreatedForm
from cart.cart import Cart
from .tasks import order_created


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
            return render(request, 'orders/order_created.html', {'order': order})

    else:
        form = OrderCreatedForm()

    return render(request, 'orders/order_create.html',
                  {'cart': cart, 'form': form })
