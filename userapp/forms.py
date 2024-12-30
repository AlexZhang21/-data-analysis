from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Company,
    CompanyFile,
    Company_type,
    Product,
    Payment,
    Issuing_bank,
    Receiving_bank,
    Tt_bank,
    ProductEntry,  # 新增
)


# 用户表单
class UserForm(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


# 新建用户表单
class CreateNewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CreateNewUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


# 修改密码表单
class changePasswordForm(forms.ModelForm):
    username = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "password")


# 公司表单
class companyForm(forms.ModelForm):
    file_upload = forms.FileField(
        required=False, widget=forms.FileInput(attrs={"class": "form-control-file"})
    )

    def __init__(self, *args, **kwargs):
        super(companyForm, self).__init__(*args, **kwargs)
        self.fields["tt_bank"].label = "TT bank"
        self.fields["issuing_bank"].label = "LC Issuing bank"
        self.fields["receiving_bank"].label = "LC Receiving Bank"

    company_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Name", "class": "form-control"}),
    )
    company_type = forms.ModelMultipleChoiceField(
        queryset=Company_type.objects.all(), widget=forms.SelectMultiple
    )
    trader = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Trader"})
    )
    product = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(), widget=forms.SelectMultiple
    )
    payment = forms.ModelMultipleChoiceField(
        queryset=Payment.objects.all(), required=False, widget=forms.SelectMultiple
    )
    issuing_bank = forms.ModelMultipleChoiceField(
        queryset=Issuing_bank.objects.all(), required=False, widget=forms.SelectMultiple
    )
    receiving_bank = forms.ModelMultipleChoiceField(
        queryset=Receiving_bank.objects.all(), required=False, widget=forms.SelectMultiple
    )
    tt_bank = forms.ModelMultipleChoiceField(
        queryset=Tt_bank.objects.all(), required=False, widget=forms.SelectMultiple
    )

    class Meta:
        model = Company
        exclude = ["counterparty_onboard_date", "serenity_onboard_date"]
        fields = (
            "company_name",
            "company_type",
            "trader",
            "product",
            "payment",
            "issuing_bank",
            "receiving_bank",
            "tt_bank",
            "file_upload",
        )

    def save(self, commit=True):
        extra_field = self.cleaned_data.get("file_upload", None)
        instance = super(companyForm, self).save(commit=commit)
        if commit:
            instance.save()
        return instance


# 筛选表单
class filterForm(forms.ModelForm):
    company_type = forms.ModelMultipleChoiceField(
        queryset=Company_type.objects.all(), widget=forms.SelectMultiple
    )
    trader = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Trader"})
    )
    product = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(), widget=forms.SelectMultiple
    )
    payment = forms.ModelMultipleChoiceField(
        queryset=Payment.objects.all(), widget=forms.SelectMultiple
    )
    issuing_bank = forms.ModelMultipleChoiceField(
        queryset=Issuing_bank.objects.all(), required=False, widget=forms.SelectMultiple
    )
    receiving_bank = forms.ModelMultipleChoiceField(
        queryset=Receiving_bank.objects.all(), required=False, widget=forms.SelectMultiple
    )
    tt_bank = forms.ModelMultipleChoiceField(
        queryset=Tt_bank.objects.all(), required=False, widget=forms.SelectMultiple
    )

    class Meta:
        model = Company
        exclude = ["counterparty_onboard_date", "serenity_onboard_date"]
        fields = (
            "company_type",
            "trader",
            "product",
            "payment",
            "issuing_bank",
            "receiving_bank",
            "tt_bank",
        )


# 产品条目表单
class ProductEntryForm(forms.ModelForm):
    upload_file = forms.FileField(required=False)
    class Meta:
        model = ProductEntry
        fields = [
            "product",
            "product_group",
            "year",
            "origin",
            "quantity",
            "price",
            "tag1",
            "tag2",
            "tag3",
            'uploaded_file',
        ]
        widgets = {
            "product": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "product_group": forms.Select(attrs={"class": "form-select", "required": True}),
            "year": forms.Select(attrs={"class": "form-select", "required": True}),
            "origin": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "quantity": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "price": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "tag1": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "tag2": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "tag3": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
        }
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Define the year field as a dropdown with a range of years
            self.fields["year"].widget = forms.Select(
                choices=[(year, year) for year in range(2000, 2041)]
            )




'''
from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.models import User
from .models import Company,CompanyFile,Company_type,Product,Payment,Issuing_bank,Receiving_bank,Tt_bank,trader,status,buy_sup,country,country2,trader2


class UserForm(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "first_name", 'last_name', "email")

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CreateNewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", 'last_name', "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CreateNewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class changePasswordForm(forms.ModelForm):
    username = forms.CharField(required=True,widget=forms.TextInput(attrs={'readonly':'readonly'}))
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ("username", "password")


class companyForm(forms.ModelForm):
    # Other fields...
    file_upload = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    def __init__(self, *args, **kwargs):
        super(companyForm, self).__init__(*args, **kwargs)
        self.fields['tt_bank'].label = "TT bank"
        self.fields['issuing_bank'].label = "LC Issuing bank"
        self.fields['receiving_bank'].label = "LC Receiving Bank"

    company_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Name', 'class': 'form-control'}))
    company_type = forms.ModelMultipleChoiceField(queryset=Company_type.objects.all(), widget=forms.SelectMultiple)
    trader = forms.CharField(widget=forms.Select(choices=trader, attrs={'class': 'form-control'}))
    counterparty_onboard_status = forms.CharField(widget=forms.Select(choices=status, attrs={'class': 'form-control'}))
    buyer_supplier = forms.CharField(widget=forms.Select(choices=buy_sup, attrs={'class': 'form-control'}))
    product = forms.ModelMultipleChoiceField(queryset=Product.objects.all(), widget=forms.SelectMultiple)
    payment = forms.ModelMultipleChoiceField(queryset=Payment.objects.all(), required=False, widget=forms.SelectMultiple)
    issuing_bank = forms.ModelMultipleChoiceField(queryset=Issuing_bank.objects.all(), required=False, widget=forms.SelectMultiple)
    receiving_bank = forms.ModelMultipleChoiceField(queryset=Receiving_bank.objects.all(), required=False, widget=forms.SelectMultiple)
    tt_bank = forms.ModelMultipleChoiceField(queryset=Tt_bank.objects.all(), required=False, widget=forms.SelectMultiple)
    credit_amount = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'credit amount', 'type': 'number', 'step': '0.01', 'class': 'form-control'}))
    credit_period = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'credit period', 'type': 'number', 'class': 'form-control'}))
    country = forms.CharField(widget=forms.Select(choices=country, attrs={'class': 'form-control'}))
    serenity_onboard_status = forms.CharField(required=False, widget=forms.Select(choices=status, attrs={'class': 'form-control'}))
    remarks = forms.CharField(required=False, max_length=1000, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))

    class Meta:
        model = Company
        exclude = ['counterparty_onboard_date','serenity_onboard_date']
        fields = ("company_name", "company_type","trader", 'counterparty_onboard_status', "buyer_supplier",
                  "product", "payment", 'issuing_bank', "receiving_bank", "tt_bank","credit_amount", "credit_period", 'country',
                  "serenity_onboard_status","file_upload","remarks")
    def save(self,commit=True):
        extra_field = self.cleaned_data.get('file_upload',None)
        instance = super(companyForm,self).save(commit = commit)
        if commit:
            instance.save()
        return instance

class filterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(filterForm, self).__init__(*args, **kwargs)
        self.fields['tt_bank'].label = "TT bank"
        self.fields['issuing_bank'].label = "LC Issuing bank"
        self.fields['receiving_bank'].label = "LC Receiving Bank"

    company_type = forms.ModelMultipleChoiceField( queryset=Company_type.objects.all(),widget=forms.SelectMultiple)
    trader = forms.CharField(widget=forms.Select(choices=trader2, attrs={'class': 'form-control'}))
    product = forms.ModelMultipleChoiceField( queryset=Product.objects.all(),widget=forms.SelectMultiple)
    payment = forms.ModelMultipleChoiceField( queryset=Payment.objects.all(),widget=forms.SelectMultiple)
    issuing_bank = forms.ModelMultipleChoiceField(queryset=Issuing_bank.objects.all(),required=False,widget=forms.SelectMultiple)
    receiving_bank = forms.ModelMultipleChoiceField(queryset=Receiving_bank.objects.all(),required=False, widget=forms.SelectMultiple)
    tt_bank = forms.ModelMultipleChoiceField(queryset=Tt_bank.objects.all(),required=False, widget=forms.SelectMultiple)
    country = forms.CharField(widget=forms.Select(choices=country2,attrs={'class': 'form-control'}))
    class Meta:
        model = Company
        exclude = ['counterparty_onboard_date','serenity_onboard_date']
        fields = ("company_type","trader","product", "payment", 'issuing_bank', "receiving_bank", "tt_bank", 'country')
'''