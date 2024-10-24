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

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from core.models import Cart


User = get_user_model()


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        """
        inputタグにclass属性を追加します。
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        """
        以下のようにfor文でよりスマートに記述することもできます。

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        """

    def save(self):
        """
        ユーザー作成と同時にそのユーザーにカートを持たせるメソッドです。
        [手順]
        1. フォーム入力情報に基づきユーザーオブジェクトを作成（まだデータベースに保存しない）
        2. 新しいカートオブジェクトを作り、ユーザーのカートフィールドに代入
        3. ユーザーオブジェクトをデータベースに保存
        """
        user = super().save(commit=False)   # 親クラスが持つデフォルトのsaveメソッドでユーザーオブジェクトを作成
                                            # (commit=Falseとすることで、この時点ではデータベースに保存されない)
        user.cart = Cart.objects.create() 
        user.save() # ここでデータベースに保存
        return user
    
    class Meta:
        model = User
        fields = ('username',)