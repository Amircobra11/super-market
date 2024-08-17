import time
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
import requests
import json

from .models import Order, OrderDetail
from product_module.models import Product

# تعریف URL‌های زرین‌پال بر اساس تنظیمات sandbox
sandbox = 'sandbox' if settings.SANDBOX else 'www'
ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

amount = 1000  # ریال / ضروری
description = "نهایی کردن خرید شما از سایت ما"  # ضروری
phone = ''  # اختیاری
CallbackURL = 'http://localhost:8000/order/verify-payment/'  # باید برای سرور واقعی ویرایش شود

def add_product_to_order(request: HttpRequest):
    product_id = int(request.GET.get('product_id'))
    count = int(request.GET.get('count'))
    if count < 1:
        return JsonResponse({
            'status': 'invalid_count',
            'text': 'مقدار وارد شده معتبر نمی‌باشد',
            'confirm_button_text': 'مرسی از شما',
            'icon': 'warning'
        })

    if request.user.is_authenticated:
        product = Product.objects.filter(pk=product_id, is_active=True, is_delete=False).first()
        if product is not None:
            current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
            current_order_detail = current_order.orderdetail_set.filter(product_id=product_id).first()
            if current_order_detail is not None:
                current_order_detail.count += count
                current_order_detail.save()
            else:
                new_detail = OrderDetail(order_id=current_order.id, product_id=product_id, count=count)
                new_detail.save()
            return JsonResponse({
                'status': 'success',
                'text': 'محصول مورد نظر با موفقیت به سبد خرید شما اضافه شد',
                'confirm_button_text': 'باشه ممنونم',
                'icon': 'success'
            })
        else:
            return JsonResponse({
                'status': 'not_found',
                'text': 'محصول مورد نظر یافت نشد',
                'confirm_button_text': 'باشه ممنونم',
                'icon': 'error'
            })
    else:
        return JsonResponse({
            'status': 'not_auth',
            'text': 'برای افزودن محصول به سبد خرید ابتدا باید وارد سایت شوید',
            'confirm_button_text': 'ورود به سایت',
            'icon': 'error'
        })


@login_required
def request_payment(request: HttpRequest):
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_order.calculate_total_price()
    if total_price == 0:
        return redirect(reverse('user-basket-page'))

    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": total_price * 10,
        "Description": description,
        "Phone": phone,
        "CallbackURL": CallbackURL,
    }
    data = json.dumps(data)
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    try:
        response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)
        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                return redirect(ZP_API_STARTPAY + response["Authority"])
            else:
                return JsonResponse({'status': False, 'code': str(response['Status'])})
        return JsonResponse({'status': False, 'code': 'unexpected_error'})

    except requests.exceptions.Timeout:
        return JsonResponse({'status': False, 'code': 'timeout'})
    except requests.exceptions.ConnectionError:
        return JsonResponse({'status': False, 'code': 'connection_error'})


@login_required
def verify_payment(request: HttpRequest):
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_order.calculate_total_price()
    data = {
        "MerchantID": settings.MERCHANT,
        "Amount": total_price * 10,
        "Authority": request.GET.get('Authority'),
    }
    data = json.dumps(data)
    headers = {'content-type': 'application/json', 'content-length': str(len(data))}
    response = requests.post(ZP_API_VERIFY, data=data, headers=headers)
    if response.status_code == 100 or 200:
        response = response.json()
        if response['Status'] == 100:
            current_order.is_paid = True
            current_order.payment_date = datetime.now()
            current_order.save()
            return render(request, 'order_module/payment_result.html', {
                'success': f'تراکنش شما با کد پیگیری {response["RefID"]} با موفقیت انجام شد',
            })
        elif response['Status'] == 101:
            return render(request, 'order_module/payment_result.html', {
                'info': 'این تراکنش قبلا ثبت شده است',
            })
        else:
            return render(request, 'order_module/payment_result.html', {
                'error': "پرداخت با موفقیت ناموفق شد"
            })
    else:
        return render(request, 'order_module/payment_result.html', {
            'error': 'کاربر با خطا مواجه شد / کاربر از پرداخت ممانعت کرد.'
        })
