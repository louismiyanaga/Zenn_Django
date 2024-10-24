"""
MIT License

Copyright © 2024 louismiyanaga

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from django.conf import settings
from django.db import models

"""
---------------------------
ユーザーモデルの読み込み方法３種
---------------------------

1. settingsファイルから取得
from django.conf import settings
User = settings.AUTH_USER_MODEL

2. get_user_modelで取得
from django.contrib.auth import get_user_model
User = get_user_model()

3. 直接インポートして取得
from accounts.models import CustomUser

"""


User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField('カテゴリ名', max_length=10)

    class Meta:
        verbose_name = '商品カテゴリ'
        verbose_name_plural = '商品カテゴリ'
    
    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField('商品名', max_length=100)
    price = models.PositiveIntegerField('価格')
    description = models.TextField('商品説明', blank=True, null=True)
    image = models.ImageField('商品画像', upload_to='item_images/', blank=True, null=True)
    category = models.ForeignKey(to=Category, on_delete=models.SET_DEFAULT, default=1, verbose_name='商品カテゴリ')

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
    
    def __str__(self):
        return self.name


class CartItem(models.Model):
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.PositiveIntegerField('個数', default=1)
    
    class Meta:
        verbose_name = 'カートアイテム'
        verbose_name_plural = 'カートアイテム'
    
    def __str__(self):
        return f"{self.quantity}個の{self.item.name}"
    
    @property
    def total_price(self):
        """
        カートアイテムの合計金額を算出するメソッドです。
        """
        return self.item.price * self.quantity


class Cart(models.Model):
    cart_items = models.ManyToManyField(to=CartItem, blank=True, verbose_name='カートアイテム') # ManyToManyFieldにおいてnull=Trueは無意味のため不要です（右記警告が出ます → core.Cart.cart_items: (fields.W340) null has no effect on ManyToManyField.）
    
    class Meta:
        verbose_name = 'カート'
        verbose_name_plural = 'カート'
    
    def __str__(self):
        # CustomUserモデルのcartフィールドに related_name='cart_user' と指定したことで
        # 以下のように self.cart_user でユーザーオブジェクトを呼び出すことが可能になります
        return f"{self.cart_user.username}のカート"

    def add_cart_item(self, new_cart_item):
        """
        カートアイテムをカートに追加するメソッドです。
        [内容]
        1. すでに商品がカートに存在する場合は、その商品のquantityを増やすだけの処理
        2. そうでなければ、新たにカートアイテムを追加する処理
        """
        # 1. すでに商品がカートに存在する場合
        if new_cart_item.item in [cart_item.item for cart_item in self.cart_items.all()]:
            original_cart_item = self.cart_items.get(item_id=new_cart_item.item.id)
            original_cart_item.quantity += new_cart_item.quantity
            original_cart_item.save()
        # 2. そうでない場合
        else:
            new_cart_item.save()
            self.cart_items.add(new_cart_item) # ManyToManyの場合は忘れずにadd()を行うこと
    
    @property
    def total_price(self):
        """
        カートの中にある全カートアイテムの総額を算出するメソッドです。
        """
        return sum([cart_item.total_price for cart_item in self.cart_items.all()])


class Order(models.Model):
    order_user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='注文ユーザー') # ユーザーが削除されても注文履歴を残したい場合は on_delete=models.SET_NULL にします
    order_items = models.ManyToManyField(to=CartItem, blank=True, verbose_name='注文商品')
    order_price = models.PositiveIntegerField('注文総額')
    ordered_date = models.DateTimeField('注文日', auto_now=True)

    class Meta:
        verbose_name = '注文'
        verbose_name_plural = '注文'
    
    def __str__(self):
        return f"{self.order_user.username}様の注文（{self.ordered_date}）"
    