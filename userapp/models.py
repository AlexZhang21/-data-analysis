from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
comp_type = [
    ('Trading House', 'Trading House'),
    ('NOC', 'NOC'),
    ('Refinery', 'Refinery'),
    ('End User', 'End User'),
    ('Producer', 'Producer'),
    ('Major', 'Major'),
]

trader = (
    ('Peter', 'Peter'),
    ('Rex', 'Rex'),
    ('Maltin', 'Maltin'),
    ('Bai Zhong', 'Bai Zhong'),
    ('Si Qi', 'Si Qi'),
)

trader2 = (
    ('', 'None'),
    ('Peter', 'Peter'),
    ('Rex', 'Rex'),
    ('Maltin', 'Maltin'),
    ('Bai Zhong', 'Bai Zhong'),
    ('Si Qi', 'Si Qi'),
)

status = (
    ('Complete', 'Complete'),
    ('Processing', 'Processing'),
    ('Unsuccessful', 'Unsuccessful'),
)

buy_sup = (
    ('Buyer', 'Buyer'),
    ('Supplier', 'Supplier'),
    ('Both', 'Both'),
)

product = [
    ('Fuel Oil', 'Fuel Oil'),
    ('Petrochemical', 'Petrochemical'),
    ('Biofuel', 'Biofuel'),
    ('Metal', 'Metal'),
    ('Other', 'Other'),
    ('LPG', 'LPG'),
    ('Crude Oil', 'Crude Oil'),
    ('Bitumen', 'Bitumen'),
]

payment = [
    ('L/C', 'L/C'),
    ('Open Credit', 'Open Credit'),
    ('Prepayment', 'Prepayment'),
]

country = (
    ('Afghanistan', 'Afghanistan'),
    ('Aland Islands', 'Aland Islands'),
    ('Albania', 'Albania'),
    # ... (省略部分国家列表)
    ('Zimbabwe', 'Zimbabwe'),
)

country2 = (
    ('', 'None'),
    ('Afghanistan', 'Afghanistan'),
    ('Aland Islands', 'Aland Islands'),
    ('Albania', 'Albania'),
    # ... (省略部分国家列表)
    ('Zimbabwe', 'Zimbabwe'),
)

bank = [
    ('DBS Bank', 'DBS Bank'),
    ('HSBC', 'HSBC'),
    # ... (省略部分银行列表)
    ('UOB Bank', 'UOB Bank'),
]

User = get_user_model()


class Company_type(models.Model):
    company_type = models.CharField(max_length=100)

    def __str__(self):
        return self.company_type


class Product(models.Model):
    product_type = models.CharField(max_length=100)

    def __str__(self):
        return self.product_type


class Payment(models.Model):
    payment_type = models.CharField(max_length=100)

    def __str__(self):
        return self.payment_type


class Issuing_bank(models.Model):
    bank_name = models.CharField(max_length=1000)

    def __str__(self):
        return self.bank_name


class Receiving_bank(models.Model):
    bank_name = models.CharField(max_length=1000)

    def __str__(self):
        return self.bank_name


class Tt_bank(models.Model):
    bank_name = models.CharField(max_length=1000)

    def __str__(self):
        return self.bank_name


class Company(models.Model):
    company_name = models.CharField(max_length=1000)
    company_type = models.ManyToManyField(Company_type)
    trader = models.CharField(max_length=1000)
    counterparty_onboard_status = models.CharField(max_length=100, null=True, blank=True)
    counterparty_onboard_date = models.DateField(null=True, blank=True)
    buyer_supplier = models.CharField(max_length=100)
    product = models.ManyToManyField(Product)
    payment = models.ManyToManyField(Payment)
    issuing_bank = models.ManyToManyField(Issuing_bank)
    receiving_bank = models.ManyToManyField(Receiving_bank)
    tt_bank = models.ManyToManyField(Tt_bank)
    credit_amount = models.FloatField(null=True, blank=True)
    credit_period = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100)
    serenity_onboard_status = models.CharField(max_length=100, null=True, blank=True)
    serenity_onboard_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=1000)


class CompanyFile(models.Model):
    filename = models.CharField(max_length=1000)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    filepath = models.FileField(
        max_length=1000, upload_to="files/", null=True, verbose_name=""
    )
    uploaded_date = models.DateField()


class CompanycreatedRecord(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    done_by = models.CharField(max_length=1000)
    date = models.DateField()
    remark = models.CharField(max_length=1000)


# 新增的 ProductEntry 模型
PRODUCT_GROUP_CHOICES = [
    ('LPG', 'LPG'),
    ('Naphtha', 'Naphtha'),
    ('Fueloil', 'Fueloil'),
    ('Gasoil', 'Gasoil'),
    ('Gasoline', 'Gasoline'),
    ('Bitumen', 'Bitumen'),
    ('Crude', 'Crude'),
    ('Others', 'Others'),
]

YEAR_CHOICES = [(year, year) for year in range(2000, 2041)]


class ProductEntry(models.Model):
    product = models.CharField(max_length=255)  # 产品名称
    product_group = models.CharField(
        max_length=50, choices=PRODUCT_GROUP_CHOICES
    )  # 产品组
    year = models.IntegerField(choices=YEAR_CHOICES)  # 年份
    origin = models.CharField(max_length=255, default="Unknown")  # 原产地，默认值为 "Unknown"
    quantity = models.CharField(max_length=100)  # 数量
    price = models.CharField(max_length=100)  # 价格
    tag1 = models.CharField(max_length=255, null=True, blank=True)  # 标签 1
    tag2 = models.CharField(max_length=255, null=True, blank=True)  # 标签 2
    tag3 = models.CharField(max_length=255, null=True, blank=True)  # 标签 3
    uploaded_file = models.FileField(
        upload_to="uploaded_files/", blank=True, null=True
    )  # 上传文件字段，支持Excel、PDF等
    upload_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="uploaded_products"
    )  # 上传用户
    upload_time = models.DateTimeField(auto_now_add=True)  # 上传时间
    extracted_text = models.TextField(null=True, blank=True)  # OCR提取的文本内容

    def __str__(self):
        return f"{self.product} ({self.product_group}, {self.year})"



'''
from django.db import models
from django.contrib.auth import get_user_model

comp_type = [
    ('Trading House','Trading House'),
    ('NOC','NOC'),
    ('Refinery','Refinery'),
    ('End User','End User'),
    ('Producer','Producer'),
    ('Major','Major'),
]

trader = (
    ('Peter','Peter'),
    ('Rex','Rex'),
    ('Maltin','Maltin'),
    ('Bai Zhong','Bai Zhong'),
    ('Si Qi','Si Qi'),
)

trader2 = (
    ('','None'),
    ('Peter','Peter'),
    ('Rex','Rex'),
    ('Maltin','Maltin'),
    ('Bai Zhong','Bai Zhong'),
    ('Si Qi', 'Si Qi'),
)


status = (
    ('Complete','Complete'),
    ('Processing','Processing'),
    ('Unsuccessful','Unsuccessful'),
)

buy_sup = (
    ('Buyer','Buyer'),
    ('Supplier','Supplier'),
    ('Both','Both'),
)

product = [
    ('Fuel Oil','Fuel Oil'),
    ('Petrochemical','Petrochemical'),
    ('Biofuel','Biofuel'),
    ('Metal','Metal'),
    ('Other','Other'),
    ('LPG','LPG'),
    ('Crude Oil', 'Crude Oil'),
    ('Bitumen', 'Bitumen'),
]

payment = [
    ('L/C','L/C'),
    ('Open Credit','Open Credit'),
    ('Prepayment','Prepayment'),
]

country = (
 ('Afghanistan', 'Afghanistan'),
 ('Aland Islands', 'Aland Islands'),
 ('Albania', 'Albania'),
 ('Algeria', 'Algeria'),
 ('American Samoa', 'American Samoa'),
 ('Andorra', 'Andorra'),
 ('Angola', 'Angola'),
 ('Anguilla', 'Anguilla'),
 ('Antarctica', 'Antarctica'),
 ('Antigua and Barbuda', 'Antigua and Barbuda'),
 ('Argentina', 'Argentina'),
 ('Armenia', 'Armenia'),
 ('Aruba', 'Aruba'),
 ('Australia', 'Australia'),
 ('Austria', 'Austria'),
 ('Azerbaijan', 'Azerbaijan'),
 ('Bahamas', 'Bahamas'),
 ('Bahrain', 'Bahrain'),
 ('Bangladesh', 'Bangladesh'),
 ('Barbados', 'Barbados'),
 ('Belarus', 'Belarus'),
 ('Belgium', 'Belgium'),
 ('Belize', 'Belize'),
 ('Benin', 'Benin'),
 ('Bermuda', 'Bermuda'),
 ('Bhutan', 'Bhutan'),
 ('Botswana', 'Botswana'),
 ('Bouvet Island', 'Bouvet Island'),
 ('Brazil', 'Brazil'),
 ('Brunei Darussalam', 'Brunei Darussalam'),
 ('Bulgaria', 'Bulgaria'),
 ('Burkina Faso', 'Burkina Faso'),
 ('Burundi', 'Burundi'),
 ('Cambodia', 'Cambodia'),
 ('Cameroon', 'Cameroon'),
 ('Canada', 'Canada'),
 ('Cape Verde', 'Cape Verde'),
 ('Cayman Islands', 'Cayman Islands'),
 ('Chad', 'Chad'),
 ('Chile', 'Chile'),
 ('China', 'China'),
 ('Christmas Island', 'Christmas Island'),
 ('Cocos (Keeling) Islands', 'Cocos (Keeling) Islands'),
 ('Colombia', 'Colombia'),
 ('Comoros', 'Comoros'),
 ('Congo', 'Congo'),
 ('Cook Islands', 'Cook Islands'),
 ('Costa Rica', 'Costa Rica'),
 ("Côte d'Ivoire", "Côte d'Ivoire"),
 ('Croatia', 'Croatia'),
 ('Cuba', 'Cuba'),
 ('Curaçao', 'Curaçao'),
 ('Cyprus', 'Cyprus'),
 ('Czech Republic', 'Czech Republic'),
 ('Denmark', 'Denmark'),
 ('Djibouti', 'Djibouti'),
 ('Dominica', 'Dominica'),
 ('Dominican Republic', 'Dominican Republic'),
 ('Ecuador', 'Ecuador'),
 ('Egypt', 'Egypt'),
 ('El Salvador', 'El Salvador'),
 ('Equatorial Guinea', 'Equatorial Guinea'),
 ('Eritrea', 'Eritrea'),
 ('Estonia', 'Estonia'),
 ('Ethiopia', 'Ethiopia'),
 ('Falkland Islands (Malvinas)', 'Falkland Islands (Malvinas)'),
 ('Faroe Islands', 'Faroe Islands'),
 ('Fiji', 'Fiji'),
 ('Finland', 'Finland'),
 ('France', 'France'),
 ('French Guiana', 'French Guiana'),
 ('French Polynesia', 'French Polynesia'),
 ('Gabon', 'Gabon'),
 ('Gambia', 'Gambia'),
 ('Georgia', 'Georgia'),
 ('Germany', 'Germany'),
 ('Ghana', 'Ghana'),
 ('Gibraltar', 'Gibraltar'),
 ('Greece', 'Greece'),
 ('Greenland', 'Greenland'),
 ('Grenada', 'Grenada'),
 ('Guadeloupe', 'Guadeloupe'),
 ('Guam', 'Guam'),
 ('Guatemala', 'Guatemala'),
 ('Guernsey', 'Guernsey'),
 ('Guinea', 'Guinea'),
 ('Guinea-Bissau', 'Guinea-Bissau'),
 ('Guyana', 'Guyana'),
 ('Haiti', 'Haiti'),
 ('Honduras', 'Honduras'),
 ('Hong Kong', 'Hong Kong'),
 ('Hungary', 'Hungary'),
 ('Iceland', 'Iceland'),
 ('India', 'India'),
 ('Indonesia', 'Indonesia'),
 ('Iran, Islamic Republic of', 'Iran, Islamic Republic of'),
 ('Iraq', 'Iraq'),
 ('Ireland', 'Ireland'),
 ('Isle of Man', 'Isle of Man'),
 ('Israel', 'Israel'),
 ('Italy', 'Italy'),
 ('Jamaica', 'Jamaica'),
 ('Japan', 'Japan'),
 ('Jersey', 'Jersey'),
 ('Jordan', 'Jordan'),
 ('Kazakhstan', 'Kazakhstan'),
 ('Kenya', 'Kenya'),
 ('Kiribati', 'Kiribati'),
 ("Korea","Korea"),
 ('Kuwait', 'Kuwait'),
 ('Kyrgyzstan', 'Kyrgyzstan'),
 ('Latvia', 'Latvia'),
 ('Lebanon', 'Lebanon'),
 ('Lesotho', 'Lesotho'),
 ('Liberia', 'Liberia'),
 ('Libya', 'Libya'),
 ('Liechtenstein', 'Liechtenstein'),
 ('Lithuania', 'Lithuania'),
 ('Luxembourg', 'Luxembourg'),
 ('Macao', 'Macao'),
 ('Madagascar', 'Madagascar'),
 ('Malawi', 'Malawi'),
 ('Malaysia', 'Malaysia'),
 ('Maldives', 'Maldives'),
 ('Mali', 'Mali'),
 ('Malta', 'Malta'),
 ('Marshall Islands', 'Marshall Islands'),
 ('Martinique', 'Martinique'),
 ('Mauritania', 'Mauritania'),
 ('Mauritius', 'Mauritius'),
 ('Mayotte', 'Mayotte'),
 ('Mexico', 'Mexico'),
 ('Monaco', 'Monaco'),
 ('Mongolia', 'Mongolia'),
 ('Montenegro', 'Montenegro'),
 ('Montserrat', 'Montserrat'),
 ('Morocco', 'Morocco'),
 ('Mozambique', 'Mozambique'),
 ('Myanmar', 'Myanmar'),
 ('Namibia', 'Namibia'),
 ('Nauru', 'Nauru'),
 ('Nepal', 'Nepal'),
 ('Netherlands', 'Netherlands'),
 ('New Caledonia', 'New Caledonia'),
 ('New Zealand', 'New Zealand'),
 ('Nicaragua', 'Nicaragua'),
 ('Niger', 'Niger'),
 ('Nigeria', 'Nigeria'),
 ('Niue', 'Niue'),
 ('Norfolk Island', 'Norfolk Island'),
 ('Norway', 'Norway'),
 ('Oman', 'Oman'),
 ('Pakistan', 'Pakistan'),
 ('Palau', 'Palau'),
 ('Palestine', 'Palestine'),
 ('Panama', 'Panama'),
 ('Papua New Guinea', 'Papua New Guinea'),
 ('Paraguay', 'Paraguay'),
 ('Peru', 'Peru'),
 ('Philippines', 'Philippines'),
 ('Pitcairn', 'Pitcairn'),
 ('Poland', 'Poland'),
 ('Portugal', 'Portugal'),
 ('Puerto Rico', 'Puerto Rico'),
 ('Qatar', 'Qatar'),
 ('Réunion', 'Réunion'),
 ('Romania', 'Romania'),
 ('Russian Federation', 'Russian Federation'),
 ('Rwanda', 'Rwanda'),
 ('Saint Barthélemy', 'Saint Barthélemy'),
 ('Saint Lucia', 'Saint Lucia'),
 ('Saint Martin (French part)', 'Saint Martin (French part)'),
 ('Saint Pierre and Miquelon', 'Saint Pierre and Miquelon'),
 ('Samoa', 'Samoa'),
 ('San Marino', 'San Marino'),
 ('Sao Tome and Principe', 'Sao Tome and Principe'),
 ('Saudi Arabia', 'Saudi Arabia'),
 ('Senegal', 'Senegal'),
 ('Serbia', 'Serbia'),
 ('Seychelles', 'Seychelles'),
 ('Sierra Leone', 'Sierra Leone'),
 ('Singapore', 'Singapore'),
 ('Solomon Islands', 'Solomon Islands'),
 ('Somalia', 'Somalia'),
 ('South Africa', 'South Africa'),
 ('Spain', 'Spain'),
 ('Sri Lanka', 'Sri Lanka'),
 ('Sudan', 'Sudan'),
 ('Suriname', 'Suriname'),
 ('South Sudan', 'South Sudan'),
 ('Svalbard and Jan Mayen', 'Svalbard and Jan Mayen'),
 ('Swaziland', 'Swaziland'),
 ('Sweden', 'Sweden'),
 ('Switzerland', 'Switzerland'),
 ('Syrian Arab Republic', 'Syrian Arab Republic'),
 ('Taiwan', 'Taiwan'),
 ('Tajikistan', 'Tajikistan'),
 ('Thailand', 'Thailand'),
 ('Timor-Leste', 'Timor-Leste'),
 ('Togo', 'Togo'),
 ('Tokelau', 'Tokelau'),
 ('Tonga', 'Tonga'),
 ('Trinidad and Tobago', 'Trinidad and Tobago'),
 ('Tunisia', 'Tunisia'),
 ('Turkey', 'Turkey'),
 ('Turkmenistan', 'Turkmenistan'),
 ('Tuvalu', 'Tuvalu'),
 ('Uganda', 'Uganda'),
 ('Ukraine', 'Ukraine'),
 ('United Arab Emirates', 'United Arab Emirates'),
 ('United Kingdom', 'United Kingdom'),
 ('United States', 'United States'),
 ('Uruguay', 'Uruguay'),
 ('Uzbekistan', 'Uzbekistan'),
 ('Vanuatu', 'Vanuatu'),
 ('VietNam', 'VietNam'),
 ('Yemen', 'Yemen'),
 ('Zambia', 'Zambia'),
 ('Zimbabwe', 'Zimbabwe')
)

country2 = (
 ('','None'),
 ('Afghanistan', 'Afghanistan'),
 ('Aland Islands', 'Aland Islands'),
 ('Albania', 'Albania'),
 ('Algeria', 'Algeria'),
 ('American Samoa', 'American Samoa'),
 ('Andorra', 'Andorra'),
 ('Angola', 'Angola'),
 ('Anguilla', 'Anguilla'),
 ('Antarctica', 'Antarctica'),
 ('Antigua and Barbuda', 'Antigua and Barbuda'),
 ('Argentina', 'Argentina'),
 ('Armenia', 'Armenia'),
 ('Aruba', 'Aruba'),
 ('Australia', 'Australia'),
 ('Austria', 'Austria'),
 ('Azerbaijan', 'Azerbaijan'),
 ('Bahamas', 'Bahamas'),
 ('Bahrain', 'Bahrain'),
 ('Bangladesh', 'Bangladesh'),
 ('Barbados', 'Barbados'),
 ('Belarus', 'Belarus'),
 ('Belgium', 'Belgium'),
 ('Belize', 'Belize'),
 ('Benin', 'Benin'),
 ('Bermuda', 'Bermuda'),
 ('Bhutan', 'Bhutan'),
 ('Botswana', 'Botswana'),
 ('Bouvet Island', 'Bouvet Island'),
 ('Brazil', 'Brazil'),
 ('Brunei Darussalam', 'Brunei Darussalam'),
 ('Bulgaria', 'Bulgaria'),
 ('Burkina Faso', 'Burkina Faso'),
 ('Burundi', 'Burundi'),
 ('Cambodia', 'Cambodia'),
 ('Cameroon', 'Cameroon'),
 ('Canada', 'Canada'),
 ('Cape Verde', 'Cape Verde'),
 ('Cayman Islands', 'Cayman Islands'),
 ('Chad', 'Chad'),
 ('Chile', 'Chile'),
 ('China', 'China'),
 ('Christmas Island', 'Christmas Island'),
 ('Cocos (Keeling) Islands', 'Cocos (Keeling) Islands'),
 ('Colombia', 'Colombia'),
 ('Comoros', 'Comoros'),
 ('Congo', 'Congo'),
 ('Cook Islands', 'Cook Islands'),
 ('Costa Rica', 'Costa Rica'),
 ("Côte d'Ivoire", "Côte d'Ivoire"),
 ('Croatia', 'Croatia'),
 ('Cuba', 'Cuba'),
 ('Curaçao', 'Curaçao'),
 ('Cyprus', 'Cyprus'),
 ('Czech Republic', 'Czech Republic'),
 ('Denmark', 'Denmark'),
 ('Djibouti', 'Djibouti'),
 ('Dominica', 'Dominica'),
 ('Dominican Republic', 'Dominican Republic'),
 ('Ecuador', 'Ecuador'),
 ('Egypt', 'Egypt'),
 ('El Salvador', 'El Salvador'),
 ('Equatorial Guinea', 'Equatorial Guinea'),
 ('Eritrea', 'Eritrea'),
 ('Estonia', 'Estonia'),
 ('Ethiopia', 'Ethiopia'),
 ('Falkland Islands (Malvinas)', 'Falkland Islands (Malvinas)'),
 ('Faroe Islands', 'Faroe Islands'),
 ('Fiji', 'Fiji'),
 ('Finland', 'Finland'),
 ('France', 'France'),
 ('French Guiana', 'French Guiana'),
 ('French Polynesia', 'French Polynesia'),
 ('Gabon', 'Gabon'),
 ('Gambia', 'Gambia'),
 ('Georgia', 'Georgia'),
 ('Germany', 'Germany'),
 ('Ghana', 'Ghana'),
 ('Gibraltar', 'Gibraltar'),
 ('Greece', 'Greece'),
 ('Greenland', 'Greenland'),
 ('Grenada', 'Grenada'),
 ('Guadeloupe', 'Guadeloupe'),
 ('Guam', 'Guam'),
 ('Guatemala', 'Guatemala'),
 ('Guernsey', 'Guernsey'),
 ('Guinea', 'Guinea'),
 ('Guinea-Bissau', 'Guinea-Bissau'),
 ('Guyana', 'Guyana'),
 ('Haiti', 'Haiti'),
 ('Honduras', 'Honduras'),
 ('Hong Kong', 'Hong Kong'),
 ('Hungary', 'Hungary'),
 ('Iceland', 'Iceland'),
 ('India', 'India'),
 ('Indonesia', 'Indonesia'),
 ('Iran, Islamic Republic of', 'Iran, Islamic Republic of'),
 ('Iraq', 'Iraq'),
 ('Ireland', 'Ireland'),
 ('Isle of Man', 'Isle of Man'),
 ('Israel', 'Israel'),
 ('Italy', 'Italy'),
 ('Jamaica', 'Jamaica'),
 ('Japan', 'Japan'),
 ('Jersey', 'Jersey'),
 ('Jordan', 'Jordan'),
 ('Kazakhstan', 'Kazakhstan'),
 ('Kenya', 'Kenya'),
 ('Kiribati', 'Kiribati'),
 ("Korea","Korea"),
 ('Kuwait', 'Kuwait'),
 ('Kyrgyzstan', 'Kyrgyzstan'),
 ('Latvia', 'Latvia'),
 ('Lebanon', 'Lebanon'),
 ('Lesotho', 'Lesotho'),
 ('Liberia', 'Liberia'),
 ('Libya', 'Libya'),
 ('Liechtenstein', 'Liechtenstein'),
 ('Lithuania', 'Lithuania'),
 ('Luxembourg', 'Luxembourg'),
 ('Macao', 'Macao'),
 ('Madagascar', 'Madagascar'),
 ('Malawi', 'Malawi'),
 ('Malaysia', 'Malaysia'),
 ('Maldives', 'Maldives'),
 ('Mali', 'Mali'),
 ('Malta', 'Malta'),
 ('Marshall Islands', 'Marshall Islands'),
 ('Martinique', 'Martinique'),
 ('Mauritania', 'Mauritania'),
 ('Mauritius', 'Mauritius'),
 ('Mayotte', 'Mayotte'),
 ('Mexico', 'Mexico'),
 ('Monaco', 'Monaco'),
 ('Mongolia', 'Mongolia'),
 ('Montenegro', 'Montenegro'),
 ('Montserrat', 'Montserrat'),
 ('Morocco', 'Morocco'),
 ('Mozambique', 'Mozambique'),
 ('Myanmar', 'Myanmar'),
 ('Namibia', 'Namibia'),
 ('Nauru', 'Nauru'),
 ('Nepal', 'Nepal'),
 ('Netherlands', 'Netherlands'),
 ('New Caledonia', 'New Caledonia'),
 ('New Zealand', 'New Zealand'),
 ('Nicaragua', 'Nicaragua'),
 ('Niger', 'Niger'),
 ('Nigeria', 'Nigeria'),
 ('Niue', 'Niue'),
 ('Norfolk Island', 'Norfolk Island'),
 ('Norway', 'Norway'),
 ('Oman', 'Oman'),
 ('Pakistan', 'Pakistan'),
 ('Palau', 'Palau'),
 ('Palestine', 'Palestine'),
 ('Panama', 'Panama'),
 ('Papua New Guinea', 'Papua New Guinea'),
 ('Paraguay', 'Paraguay'),
 ('Peru', 'Peru'),
 ('Philippines', 'Philippines'),
 ('Pitcairn', 'Pitcairn'),
 ('Poland', 'Poland'),
 ('Portugal', 'Portugal'),
 ('Puerto Rico', 'Puerto Rico'),
 ('Qatar', 'Qatar'),
 ('Réunion', 'Réunion'),
 ('Romania', 'Romania'),
 ('Russian Federation', 'Russian Federation'),
 ('Rwanda', 'Rwanda'),
 ('Saint Barthélemy', 'Saint Barthélemy'),
 ('Saint Lucia', 'Saint Lucia'),
 ('Saint Martin (French part)', 'Saint Martin (French part)'),
 ('Saint Pierre and Miquelon', 'Saint Pierre and Miquelon'),
 ('Samoa', 'Samoa'),
 ('San Marino', 'San Marino'),
 ('Sao Tome and Principe', 'Sao Tome and Principe'),
 ('Saudi Arabia', 'Saudi Arabia'),
 ('Senegal', 'Senegal'),
 ('Serbia', 'Serbia'),
 ('Seychelles', 'Seychelles'),
 ('Sierra Leone', 'Sierra Leone'),
 ('Singapore', 'Singapore'),
 ('Solomon Islands', 'Solomon Islands'),
 ('Somalia', 'Somalia'),
 ('South Africa', 'South Africa'),
 ('Spain', 'Spain'),
 ('Sri Lanka', 'Sri Lanka'),
 ('Sudan', 'Sudan'),
 ('Suriname', 'Suriname'),
 ('South Sudan', 'South Sudan'),
 ('Svalbard and Jan Mayen', 'Svalbard and Jan Mayen'),
 ('Swaziland', 'Swaziland'),
 ('Sweden', 'Sweden'),
 ('Switzerland', 'Switzerland'),
 ('Syrian Arab Republic', 'Syrian Arab Republic'),
 ('Taiwan', 'Taiwan'),
 ('Tajikistan', 'Tajikistan'),
 ('Thailand', 'Thailand'),
 ('Timor-Leste', 'Timor-Leste'),
 ('Togo', 'Togo'),
 ('Tokelau', 'Tokelau'),
 ('Tonga', 'Tonga'),
 ('Trinidad and Tobago', 'Trinidad and Tobago'),
 ('Tunisia', 'Tunisia'),
 ('Turkey', 'Turkey'),
 ('Turkmenistan', 'Turkmenistan'),
 ('Tuvalu', 'Tuvalu'),
 ('Uganda', 'Uganda'),
 ('Ukraine', 'Ukraine'),
 ('United Arab Emirates', 'United Arab Emirates'),
 ('United Kingdom', 'United Kingdom'),
 ('United States', 'United States'),
 ('Uruguay', 'Uruguay'),
 ('Uzbekistan', 'Uzbekistan'),
 ('Vanuatu', 'Vanuatu'),
 ('VietNam', 'VietNam'),
 ('Yemen', 'Yemen'),
 ('Zambia', 'Zambia'),
 ('Zimbabwe', 'Zimbabwe')
)

bank = [('DBS Bank', 'DBS Bank'),
 ('HSBC', 'HSBC'),
 ('Citibank', 'Citibank'),
 ('SPD Bank', 'SPD Bank'),
 ('RHB Bank', 'RHB Bank'),
 ('SCBSL', 'SCBSL'),
 ('CIMB Bank', 'CIMB Bank'),
 ('OCBC Bank', 'OCBC Bank'),
 ('BOC', 'BOC'),
 ('COMMHKHH', 'COMMHKHH'),
 ('ADBC', 'ADBC'),
 ('MUFG Bank', 'MUFG Bank'),
 ('Credit Agricole', 'Credit Agricole'),
 ('Deutsche Bank', 'Deutsche Bank'),
 ('Everbright Bank', "Everbright Bank"),
 ("CITIC Bank", "CITIC Bank"),
 ("ING Bank", "ING Bank"),
 ("Sumitomo Mitsui", "Sumitomo Mitsui"),
 ("CTBC Bank", "CTBC Bank"),
 ("UOB Bank", "UOB Bank"),
]

User = get_user_model()
#
class Company_type(models.Model):
    company_type = models.CharField(max_length=100)

    def __str__(self):
        return self.company_type

class Product(models.Model):
    product_type = models.CharField(max_length=100)
    def __str__(self):
        return self.product_type

class Payment(models.Model):
    payment_type = models.CharField(max_length=100)
    def __str__(self):
        return self.payment_type

class Issuing_bank(models.Model):
    bank_name = models.CharField(max_length=1000)
    def __str__(self):
        return self.bank_name

class Receiving_bank(models.Model):
    bank_name = models.CharField(max_length=1000)
    def __str__(self):
        return self.bank_name

class Tt_bank(models.Model):
    bank_name = models.CharField(max_length=1000)
    def __str__(self):
        return self.bank_name

class Company(models.Model):
    company_name = models.CharField(max_length=1000)
    company_type = models.ManyToManyField(Company_type)
    trader = models.CharField(max_length=1000)
    counterparty_onboard_status = models.CharField(max_length=100,null=True,blank=True)
    counterparty_onboard_date = models.DateField(null=True,blank=True)
    buyer_supplier = models.CharField(max_length=100)
    product = models.ManyToManyField(Product)
    payment = models.ManyToManyField(Payment)
    issuing_bank = models.ManyToManyField(Issuing_bank)
    receiving_bank = models.ManyToManyField(Receiving_bank)
    tt_bank = models.ManyToManyField(Tt_bank)
    credit_amount = models.FloatField(null=True,blank=True)
    credit_period = models.IntegerField(null=True,blank=True)
    country = models.CharField(max_length=100)
    serenity_onboard_status = models.CharField(max_length=100,null=True,blank=True)
    serenity_onboard_date = models.DateField(null=True,blank=True)
    remarks = models.CharField(max_length=1000)

class CompanyFile(models.Model):
    filename = models.CharField(max_length=1000)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    filepath = models.FileField(max_length=1000,upload_to='files/', null=True, verbose_name="")
    uploaded_date = models.DateField()

class CompanycreatedRecord(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    done_by = models.CharField(max_length=1000)
    date = models.DateField()
    remark = models.CharField(max_length=1000)
'''