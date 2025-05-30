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
        products = shop.product_set.all()
        total_sales = 0
        total_income = 0
        remaining_products = []

        for product in products:
            sales = product.sale_set.values_list('quantity_sold', flat=True)
            sold = sum(s or 0 for s in sales)
            income = sold * product.price
            total_sales += sold
            total_income += income

            remaining_products.append({
                'name': product.name,
                'quantity': product.quantity
            })

        labels = [p['name'] for p in remaining_products]
        data = [p['quantity'] for p in remaining_products]

        shop_stats.append({
            'shop': shop.name,
            'total_sales': total_sales,
            'total_income': total_income,
            'labels': labels,
            'data': data,
            'chart_id': f"chart_{shop.id}"
        })

    return render(request, 'core/monitoring.html', {
        'shop_stats': shop_stats,
    })