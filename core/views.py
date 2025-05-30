from django.shortcuts import render, get_object_or_404
from .models import Product, Sale, Shop
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def sell_product(request):
    message = ""

    # Foydalanuvchiga tegishli do'konni olish
    shop = get_object_or_404(Shop, user=request.user)

    # Faqat shu do'kondagi mahsulotlarni olish
    products = Product.objects.filter(shop=shop)

    if request.method == 'POST':
        cart_data = request.POST.get('cart_data')
        if not cart_data:
            message = "Savatingiz bo'sh."
            return render(request, 'core/sell.html', {'products': products, 'message': message})

        try:
            cart = json.loads(cart_data)
        except json.JSONDecodeError:
            message = "Noto'g'ri ma'lumot yuborildi."
            return render(request, 'core/sell.html', {'products': products, 'message': message})

        sales = []
        total = 0
        for item in cart:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)

            # Mahsulotni faqat hozirgi do'kon ichidan qidiramiz
            product = get_object_or_404(Product, id=product_id, shop=shop)
            total += product.price * quantity

            if product.quantity < quantity:
                message = f"Mahsulot '{product.name}' dan omborda yetarli miqdor yo'q."
                return render(request, 'core/sell.html', {'products': products, 'message': message})


        # Hammasi yaxshi, mahsulotlarni kamaytirish va Sale yozish
        for item in cart:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)

            product = Product.objects.get(id=product_id, shop=shop)
            product.quantity -= quantity
            product.save()

            sale = Sale.objects.create(
                product=product,
                quantity_sold=quantity,
                sold_at=timezone.now()
            )
            sales.append(sale)

        return render(request, 'core/receipt.html', {'sales': sales, 'total':total})

    return render(request, 'core/sell.html', {'products': products, 'message': message})

@login_required
def monitoring(request):
    # Foydalanuvchiga tegishli do'konni olish, agar do'kon bo'lmasa 404 chiqarish
    shop = get_object_or_404(Shop, user=request.user)

    products = shop.product_set.all()
    total_sales = 0
    total_income = 0
    remaining_products = []
    sold_products = []

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

        sold_products.append({
            'name': product.name,
            'quantity': sold
        })

    shop_stats = {
        'shop': shop.name,
        'total_sales': total_sales,
        'total_income': total_income,
        'labels_remaining': [p['name'] for p in remaining_products],
        'data_remaining': [p['quantity'] for p in remaining_products],
        'labels_sold': [p['name'] for p in sold_products],
        'data_sold': [p['quantity'] for p in sold_products],
        'chart_id_remaining': f"chart_remaining_{shop.id}",
        'chart_id_sold': f"chart_sold_{shop.id}",
    }

    return render(request, 'core/monitoring.html', {
        'shop_stats': [shop_stats],  # ro'yxat qilib yuboryapmiz, chunki template for loop ishlatadi
    })

@login_required
def sales_history(request):
    sales = Sale.objects.select_related('product').order_by('-sold_at')
    return render(request, 'core/sales_history.html', {'sales': sales})