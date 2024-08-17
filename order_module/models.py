from django.db import models
from account_module.models import User
from product_module.models import Product


class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='کاربر')
    is_paid = models.BooleanField(default=False,
                                  verbose_name='نهایی شده / نشده')
    payment_date = models.DateTimeField(null=True,
                                        blank=True,
                                        verbose_name='تاریخ پرداخت')

    def __str__(self):
        return str(self.user)

    def calculate_total_price(self):
        total_amount = 0
        if self.is_paid:
            for order_detail in self.orderdetail_set.all():
                total_amount += order_detail.final_price * order_detail.count
        else:
            for order_detail in self.orderdetail_set.all():
                total_amount += order_detail.product.price * order_detail.count

        return total_amount

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبد های خرید کاربران'


class OrderDetail(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              verbose_name='سبد خرید')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                verbose_name='محصول')
    # final_price = models.IntegerField(null=True,
    #                                   blank=True,
    #                                   verbose_name='قیمت نهایی تکی محصول')
    count = models.IntegerField(verbose_name='تعداد')

    @property
    def final_price(self):
        return self.product.price * self.count


def __str__(self):
    return str(self.order)


class Meta:
    verbose_name = 'جزییات سبد خرید'
    verbose_name_plural = 'لیست جزییات سبدهای خرید'
