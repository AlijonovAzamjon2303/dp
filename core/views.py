from django.shortcuts import render, get_object_or_404
from .models import Product, Sale, Shop
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

@login_required
def sell_product(request):
    message = ""
    products = Product.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = get_object_or_404(Product, id=product_id)

        if product.quantity >= quantity:
            product.quantity -= quantity
            product.save()

            sale = Sale.objects.create(
                product=product,
                quantity_sold=quantity,
                sold_at=timezone.now()
            )

            return render(request, 'core/receipt.html', {'sale': sale})
        else:
            message = "Omborda yetarli mahsulot mavjud emas."

    return render(request, 'core/sell.html', {'products': products, 'message': message})

@login_required
def monitoring(request):
    shops = Shop.objects.all()
    shop_stats = []

    for shop in shops:
        total_sales = 0
        total_income = Decimal('0.00')
        remaining_products = []

        for product in shop.product_set.all():
            sold_data = product.sale_set.aggregate(total=Sum('quantity_sold'))
            sold = sold_data['total'] or 0

            try:
                price = Decimal(product.price)
            except (InvalidOperation, TypeError, ValueError):
                price = Decimal('0.00')

            income = Decimal(sold) * price
            total_sales += sold
            total_income += income

            remaining_products.append({
                'name': product.name,
                'quantity': product.quantity
            })

        shop_stats.append({
            'shop': shop.name,
            'total_sales': total_sales,
            'total_income': round(total_income, 2),
            'products': remaining_products
        })

    return render(request, 'core/monitoring.html', {'shop_stats': shop_stats})