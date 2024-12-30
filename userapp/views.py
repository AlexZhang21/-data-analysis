from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Prefetch
from django.contrib import messages
from django.conf import settings
from django.forms.models import model_to_dict
from django.core.paginator import Paginator


from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required


from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.views import View
from django.urls import reverse_lazy
from django.core.files.storage import FileSystemStorage

from .forms import UserForm, CreateNewUserForm, changePasswordForm, companyForm, filterForm, ProductEntryForm
from .models import CompanyFile, CompanycreatedRecord, Company, comp_type, product, payment, bank, ProductEntry

from datetime import datetime
from PIL import Image
from pdf2image import convert_from_path
from pytesseract import pytesseract
import pandas as pd
import os
import shutil
import mimetypes
import logging
import pytesseract
import cv2
import json
import tempfile
logger = logging.getLogger(__name__)

@login_required
def content_table(request):
    # Fetch all ProductEntry records
    product_entries = ProductEntry.objects.all()
    return render(request, 'userapp/content_table.html', {'product_entries': product_entries})

def create_new_details(request):
    uploaded_data = None
    uploaded_image_url = None

    if request.method == "POST":
        form = ProductEntryForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES.get("upload_file")

            if uploaded_file:
                file_extension = os.path.splitext(uploaded_file.name)[1].lower()

                # Handle Excel files
                if file_extension in ['.xls', '.xlsx']:
                    try:
                        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                            for chunk in uploaded_file.chunks():
                                temp_file.write(chunk)
                            df = pd.read_excel(temp_file.name)
                        uploaded_data = df.to_html(classes="table table-striped")
                    except Exception as e:
                        messages.error(request, f"Error processing Excel file: {e}")

                # Handle Image files
                elif file_extension in ['.png', '.jpg', '.jpeg']:
                    uploaded_image_url = uploaded_file

                # Handle unsupported file
                else:
                    messages.error(request, "Unsupported file type. Please upload Excel or image files.")

            # Save form data
            form.save()
            messages.success(request, "Record created successfully!")
            return redirect("content_table")
    else:
        form = ProductEntryForm()

    return render(request, "userapp/createnewdetails.html", {
        "form": form,
        "uploaded_data": uploaded_data,
        "uploaded_image_url": uploaded_image_url,
    })
def delete_product_entry(request, pk):
    if request.method == "POST":
        product_entry = get_object_or_404(ProductEntry, pk=pk)
        product_entry.delete()
        return JsonResponse({"success": True, "message": "Entry deleted successfully!"})
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)
def edit_product_entry(request, pk):
    product_entry = get_object_or_404(ProductEntry, pk=pk)
    uploaded_image_url = None

    if request.method == 'POST':
        form = ProductEntryForm(request.POST, request.FILES, instance=product_entry)
        if form.is_valid():
            if 'upload_file' in request.FILES:
                # Delete the old file if a new one is uploaded
                if product_entry.uploaded_file:
                    product_entry.uploaded_file.delete(save=False)

                uploaded_file = request.FILES['upload_file']
                file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

                # Save the new file locally
                with open(file_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                # Save the new file to the model
                product_entry.uploaded_file = uploaded_file

                # Optional: Process the new file (image or PDF)
                try:
                    if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image = Image.open(file_path)
                        text = pytesseract.image_to_string(image)
                    elif uploaded_file.name.lower().endswith('.pdf'):
                        images = convert_from_path(file_path)
                        text = ''.join([pytesseract.image_to_string(page) for page in images])
                    else:
                        text = ''
                    # You can process the extracted text as needed
                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")

                uploaded_image_url = os.path.join(settings.MEDIA_URL, uploaded_file.name)

            form.save()
            messages.success(request, "Product entry updated successfully!")
            return redirect('content_table')
        else:
            messages.error(request, "There were errors in the form. Please correct them.")
    else:
        form = ProductEntryForm(instance=product_entry)
        if product_entry.uploaded_file:
            uploaded_image_url = product_entry.uploaded_file.url

    return render(request, 'userapp/create_new_details.html', {
        'form': form,
        'editing': True,
        'uploaded_image_url': uploaded_image_url,
    })# 用户登录视图
def loginPage(request):
    if request.method == 'POST':
        usrnme = request.POST.get('username')
        pwd = request.POST.get('password')
        user = authenticate(request, username=usrnme, password=pwd)
        if user is not None:
            request.session['user'] = {
                'usrname': user.get_username(),
                'fullname': user.get_full_name(),
                'admin': user.is_superuser,
            }
            login(request, user)
            return redirect('/content_table')
        else:
            messages.error(request, 'Username or password is incorrect')
    return render(request, 'userapp/index.html')


# 主页视图
def homePage(request):
    # 确保用户已登录
    if request.user.is_anonymous:
        messages.error(request, 'You must be logged in to view this page!')
        return redirect('/')

    # 获取所有产品数据
    products_list = ProductEntry.objects.all()

    # 分页逻辑
    paginator = Paginator(products_list, 20)  # 每页显示 20 行
    page_number = request.GET.get('page')  # 从 URL 获取当前页码
    page_obj = paginator.get_page(page_number)  # 获取当前页数据

    # 渲染页面
    return render(request, 'userapp/content_table.html', {'page_obj': page_obj})




# 用户详情页面
def userPage(request, pk):
    if request.user.is_anonymous:
        messages.error(request, 'Please log in to access this page.')
        return redirect('/')
    if request.user.id != pk and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('Home')

    user = get_object_or_404(User, id=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User details updated successfully.')
            return redirect('Home' if not request.user.is_superuser else 'Ad_User_details')
    else:
        form = UserForm(instance=user)
    return render(request, 'userapp/user_details.html', {'form': form, 'base': 'userapp/base.html'})


def company_file(request, pk):
    if request.user.is_anonymous:
        messages.error(request, 'You must log in to view this page.')
        return redirect('/')

    company = get_object_or_404(Company, id=pk)
    files = CompanyFile.objects.filter(company_id=pk)
    return render(request, 'userapp/company_file.html', {
        'company': company,
        'files': files,
        'base': 'userapp/base.html',
    })

# 管理员用户页面
def aduserPage(request):
    if request.user.is_anonymous:
        messages.error(request, 'You must be logged in to access this page!')
        return redirect('/')
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can view this page.')
        logout(request)
        return redirect('/')
    all_users = User.objects.values().order_by('id')
    return render(request, 'userapp/admin_user_details.html', {'userlist': all_users, 'base': 'userapp/base.html'})


# 创建新用户
def create_product_entry(request):
    if request.user.is_anonymous:
        messages.error(request, "You must log in to create a product entry.")
        return redirect('/login')

    if request.method == "POST":
        form = ProductEntryForm(request.POST)
        if form.is_valid():
            product_entry = form.save(commit=False)
            product_entry.upload_user_id = request.user  # 假设产品条目关联到当前用户
            product_entry.upload_time = timezone.now()
            product_entry.save()
            messages.success(request, "Product entry created successfully!")
            return redirect('Home')  # 替换为实际的主页名称
        else:
            messages.error(request, "Invalid form submission. Please correct the errors.")
    else:
        form = ProductEntryForm()

    return render(request, 'userapp/create_product_entry.html', {'form': form})

def product_list(request):
    if request.user.is_anonymous:
        messages.error(request, "You must log in to view the product list.")
        return redirect('/login')

    products = ProductEntry.objects.all()  # 假设你的模型名为 ProductEntry
    return render(request, 'userapp/product_list.html', {'products': products})
def create_new_user(request):
    if request.method == "POST":
        form = CreateNewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "User added successfully!")
            return redirect("Ad_User_details")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = CreateNewUserForm()
    return render(request, 'userapp/create_new_user.html', {'form': form, 'base': 'userapp/base.html'})

def companyPage(request,pk):
    if request.user.is_anonymous:
        print('lol not again')
        messages.error(request, 'Invalid to go without Login !!!')
        return redirect('/')

    com_record = CompanycreatedRecord.objects.select_related('company').filter(company_id=pk)
    compan = Company.objects.get(id=pk)
    # print(com_record.values())
    com_name = str(compan.company_name)
    # print(model_to_dict(com_record))
    # print(com_record.company.company_name)
    print('Company page')
    return render(request, 'userapp/company_details.html', {'comp_record': com_record,'com_name':com_name, 'base': 'userapp/base.html'})

# 删除用户
def del_user(request, username):
    try:
        u = User.objects.get(username=username)
        if u.is_superuser and u.id == request.user.id:
            messages.error(request, 'Cannot delete your own account!')
        else:
            u.delete()
            messages.success(request, "The user has been deleted.")
    except User.DoesNotExist:
        messages.error(request, "User doesn't exist.")
    except Exception as e:
        messages.error(request, str(e))
    return redirect("Ad_User_details")


# 修改密码
def changePassword(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.user.is_anonymous:
        messages.error(request, 'You must log in to access this page.')
        return redirect('/')
    if request.method == 'POST':
        form = changePasswordForm(request.POST, instance=user)
        if form.is_valid():
            user.set_password(request.POST.get('password'))
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully.')
            return redirect('Ad_User_details')
    else:
        form = changePasswordForm(instance=user)
    return render(request, 'userapp/change_password.html', {'form': form, 'base': 'userapp/base.html'})


# 创建公司页面
@login_required
def create_company_form(request):
    uploaded_image_url = None
    auto_filled_data = {}

    if request.method == 'POST':
        form = ProductEntryForm(request.POST, request.FILES)
        if form.is_valid():
            product_entry = form.save(commit=False)

            # Handle file upload
            if 'upload_file' in request.FILES:
                uploaded_file = request.FILES['upload_file']
                file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

                # Save file locally
                with open(file_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                # Extract data from file (image or PDF)
                try:
                    if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image = Image.open(file_path)
                        text = pytesseract.image_to_string(image)
                    elif uploaded_file.name.lower().endswith('.pdf'):
                        images = convert_from_path(file_path)
                        text = ''.join([pytesseract.image_to_string(page) for page in images])
                    else:
                        text = ''

                    # Process extracted text (mock example)
                    auto_filled_data = {
                        "TEST": "Density at 15 Deg",
                        "METHOD": "ASTM D 1298",
                        "Guarantee": "0.96"
                    }

                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")

                uploaded_image_url = os.path.join(settings.MEDIA_URL, uploaded_file.name)
                product_entry.uploaded_file = uploaded_file  # Save file to model

            # Save ProductEntry to DB
            product_entry.upload_user_id = request.user
            product_entry.save()

            messages.success(request, "Record added successfully!")
            return redirect('content_table')
        else:
            messages.error(request, "There were errors in the form. Please correct them.")

    else:
        form = ProductEntryForm()

    return render(request, 'userapp/create_new_details.html', {
        'form': form,
        'uploaded_image_url': uploaded_image_url,
        'auto_filled_data': auto_filled_data,
    })
'''
def create_company_form(request):
    uploaded_image_url = None
    auto_filled_data = {}

    if request.method == 'POST':
        form = ProductEntryForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form
            product_entry = form.save(commit=False)
            if 'upload_file' in request.FILES:
                uploaded_file = request.FILES['upload_file']
                file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

                # Save the file locally
                with open(file_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                # Extract data from file (image or PDF)
                if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image = Image.open(file_path)
                    text = pytesseract.image_to_string(image)
                elif uploaded_file.name.lower().endswith('.pdf'):
                    images = convert_from_path(file_path)
                    text = ''.join([pytesseract.image_to_string(page) for page in images])
                else:
                    text = ''

                # Process extracted text (mock example)
                auto_filled_data = {
                    "TEST": "Density at 15 Deg",
                    "METHOD": "ASTM D 1298",
                    "Guarantee": "0.96"
                }

                uploaded_image_url = os.path.join(settings.MEDIA_URL, uploaded_file.name)

            # Save ProductEntry to DB
            product_entry.upload_user_id = request.user
            product_entry.save()

            return render(request, 'userapp/content_table.html', {'message': 'Record added successfully!'})
        else:
            return render(request, 'userapp/create_new_details.html', {
                'form': form,
                'uploaded_image_url': uploaded_image_url,
                'auto_filled_data': auto_filled_data,
            })
    else:
        form = ProductEntryForm()
    return render(request, 'userapp/create_new_details.html', {'form': form})
'''

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        uploaded_file_url = fs.url(filename)

        # Add any additional processing here if needed

        messages.success(request, 'File uploaded successfully!')
        return render(request, 'userapp/upload_file.html', {'uploaded_file_url': uploaded_file_url})

    return render(request, 'userapp/upload_file.html')


def view_uploaded_files(request):
    fs = FileSystemStorage()
    files = fs.listdir(fs.location)[1]  # Get all files in the storage directory
    file_urls = [fs.url(file) for file in files]

    return render(request, 'userapp/view_uploaded_files.html', {'file_urls': file_urls})
def delete_uploaded_file(request, pk):
    """
    Deletes an uploaded file based on the primary key.
    """
    fs = FileSystemStorage()
    files = fs.listdir(fs.location)[1]  # List all files
    try:
        file_to_delete = files[pk]  # Access the file by index (pk here acts as an index)
        file_path = os.path.join(fs.location, file_to_delete)
        if os.path.exists(file_path):
            os.remove(file_path)  # Delete the file
            return redirect('view_uploaded_files')  # Redirect to view uploaded files
        else:
            return redirect('view_uploaded_files')  # Redirect with no deletion
    except IndexError:
        return redirect('view_uploaded_files')  # Handle index out of bounds gracefully
'''
def create_company_form(request):
    if request.method == 'POST':
        form = ProductEntryForm(request.POST)
        if form.is_valid():
            product_entry = form.save(commit=False)
            product_entry.upload_user_id = request.user
            product_entry.save()
            messages.success(request, "New product entry added successfully!")
            return redirect('content_table')
        else:
            print(form.errors)  # Log form errors to the console for debugging
            messages.error(request, "There were errors in the form. Please correct them.")
    else:
        form = ProductEntryForm()
    return render(request, 'userapp/create_new_details.html', {'form': form})
  
'''




# 编辑公司信息
def edit_Company(request, pk):
    company = get_object_or_404(Company, id=pk)
    if request.method == 'POST':
        form = companyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company details updated successfully.')
            return redirect('Home')
    else:
        form = companyForm(instance=company)
    return render(request, 'userapp/edit_company_details.html', {'form': form, 'base': 'userapp/base.html'})


# 文件相关视图 (上传、删除、下载)
def delete_file(request, pk):
    file = get_object_or_404(CompanyFile, id=pk)
    if os.path.exists(file.filepath):
        os.remove(file.filepath)
        file.delete()
        messages.success(request, 'File deleted successfully.')
    return redirect('Company_file', pk=file.company_id)


def download_file(request, pk):
    file = get_object_or_404(CompanyFile, id=pk)
    with open(file.filepath, 'rb') as f:
        response = HttpResponse(f, content_type=mimetypes.guess_type(file.filepath)[0])
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file.filepath)}"'
    return response

def del_item(request, pk):
    try:
        item = Company.objects.get(id=pk)
        companyname = str(item.company_name)
        companyname = companyname.replace(" ", "_")
        locdir = os.path.join(settings.MEDIA_ROOT, companyname)
        print(item)
        print(locdir)
        item.delete()
        messages.success(request, "Company record deleted")
    except Exception as e:
        messages.error(request,e)
        return redirect("Home")
    try:
        if os.path.exists(locdir):
            shutil.rmtree(locdir)
            messages.success(request, "Folder record deleted")
        else:
            messages.error(request, "Folder record not found")
            return redirect("Home")
    except Exception as e:
        messages.error(request, e)
        return redirect("Home")
    return redirect("Home")
# 登出
def logoutAction(request):
    logout(request)
    messages.success(request, 'You have logged out!')
    return redirect('/')


def analyze_image(request, pk):
    product_entry = get_object_or_404(ProductEntry, pk=pk)

    extracted_data = []  # Main table for extracted data
    extracted_data_row = []  # Row-based custom table
    search_results = []  # Store filtered search results

    # Define keywords for filtering
    keywords = [
        "Density", "Color", "Distillation", "IBP", "Recovered",
        "Final Boiling Point", "Recovery", "Residue", "Vapor Pressure",
        "Paraffines", "iso-Paraffins", "n-Paraffins", "Olefins",
        "Naphthens", "Aromatics", "Total Sulfur", "Hydrogen Sulfide",
        "Mercaptan Sulfur", "PB Content"
    ]

    if product_entry.uploaded_file:
        file_path = product_entry.uploaded_file.path
        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            # Process Excel files
            if file_extension in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path, engine="openpyxl")
                extracted_data = df.fillna("").values.tolist()  # Convert DataFrame to list
                extracted_data_row = [[str(row)] for row in df.apply(lambda x: ' '.join(map(str, x)), axis=1)]

            # Process PDF files
            elif file_extension == '.pdf':
                images = convert_from_path(file_path)
                text = "".join([pytesseract.image_to_string(page) for page in images])
                lines = text.split("\n")
                for line in lines:
                    columns = line.split()
                    if columns:
                        extracted_data.append(columns)
                extracted_data_row = [[line.strip()] for line in lines if line.strip()]

            # Process Image files
            elif file_extension in ['.png', '.jpg', '.jpeg']:
                text = pytesseract.image_to_string(file_path)
                lines = text.split("\n")
                for line in lines:
                    columns = line.split()
                    if columns:
                        extracted_data.append(columns)
                extracted_data_row = [[line.strip()] for line in lines if line.strip()]

            else:
                messages.error(request, "Unsupported file format. Please upload Excel, PDF, or image files.")

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")

    # Filter rows containing any of the keywords
    search_results = [
        row for row in extracted_data if any(keyword.lower() in " ".join(map(str, row)).lower() for keyword in keywords)
    ]

    if request.method == "POST":
        # Capture and handle edited data from the frontend
        table_data_main = request.POST.get("table_data_main")
        table_data_row = request.POST.get("table_data_row")
        filtered_data = request.POST.get("filtered_data")  # For the filtered results table

        try:
            main_data = json.loads(table_data_main) if table_data_main else []
            row_data = json.loads(table_data_row) if table_data_row else []
            updated_filtered_data = json.loads(filtered_data) if filtered_data else []

            # Example of saving or processing data
            # Update extracted data or filtered data in the database
            print("Main Data Updated:", main_data)
            print("Row Data Updated:", row_data)
            print("Filtered Data Updated:", updated_filtered_data)

            messages.success(request, "Table data updated successfully!")
        except json.JSONDecodeError:
            messages.error(request, "Failed to update table data.")

        return redirect("content_table")

    return render(request, "userapp/analyze_image.html", {
        "product_entry": product_entry,
        "extracted_data": extracted_data,
        "extracted_data_row": extracted_data_row,
        "search_results": search_results,
    })

def enhanced_table_view(request, pk):
    # 获取产品条目
    product_entry = get_object_or_404(ProductEntry, pk=pk)
    extracted_data = []  # 用于存储提取的数据

    # 确保有上传文件
    if product_entry.uploaded_file:
        file_path = product_entry.uploaded_file.path
        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            # 处理 Excel 文件
            if file_extension in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path, engine="openpyxl")
                extracted_data = df.fillna("").values.tolist()  # 转换 DataFrame 为列表

            # 处理 PDF 文件
            elif file_extension == '.pdf':
                images = convert_from_path(file_path)
                text = "".join([pytesseract.image_to_string(page) for page in images])
                lines = text.split("\n")
                for line in lines:
                    columns = line.split()
                    if columns:
                        extracted_data.append(columns)

            # 处理图片文件
            elif file_extension in ['.png', '.jpg', '.jpeg']:
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
                lines = text.split("\n")
                for line in lines:
                    columns = line.split()
                    if columns:
                        extracted_data.append(columns)

            else:
                return JsonResponse({"error": "Unsupported file format"}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Error processing file: {str(e)}"}, status=500)

    # 处理搜索请求
    search_query = request.GET.get('search', '').strip()
    sort_column = request.GET.get('sort_column', None)
    sort_order = request.GET.get('sort_order', 'asc')

    # 搜索数据
    if search_query:
        extracted_data = [
            row for row in extracted_data
            if any(search_query.lower() in str(cell).lower() for cell in row)
        ]

    # 排序数据
    if sort_column is not None:
        try:
            sort_column = int(sort_column)  # 确保列索引是整数
            extracted_data.sort(key=lambda x: x[sort_column], reverse=(sort_order == 'desc'))
        except (IndexError, ValueError):
            return JsonResponse({"error": "Invalid sort column"}, status=400)

    # 返回数据给前端
    return JsonResponse({
        "data": extracted_data
    })
def enhanced_table_view(request, pk):
    # 获取产品条目
    product_entry = get_object_or_404(ProductEntry, pk=pk)
    extracted_data = []  # 用于存储提取的数据

    # 确保有上传文件
    if product_entry.uploaded_file:
        file_path = product_entry.uploaded_file.path
        file_extension = os.path.splitext(file_path)[1].lower()

        try:
            # 处理 Excel 文件
            if file_extension in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path, engine="openpyxl")
                extracted_data = df.fillna("").values.tolist()  # 转换 DataFrame 为列表

            # 处理 PDF 文件
            elif file_extension == '.pdf':
                images = convert_from_path(file_path)
                text = "".join([pytesseract.image_to_string(page) for page in images])
                lines = text.split("\n")
                for line in lines:
                    columns = line.split()
                    if columns:
                        extracted_data.append(columns)

            # 处理图片文件
            elif file_extension in ['.png', '.jpg', '.jpeg']:
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
                lines = text.split("\n")
                for line in lines:
                    columns = line.split()
                    if columns:
                        extracted_data.append(columns)

            else:
                return JsonResponse({"error": "Unsupported file format"}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Error processing file: {str(e)}"}, status=500)

    # 处理搜索请求
    search_query = request.GET.get('search', '').strip()
    sort_column = request.GET.get('sort_column', None)
    sort_order = request.GET.get('sort_order', 'asc')

    # 搜索数据
    if search_query:
        extracted_data = [
            row for row in extracted_data
            if any(search_query.lower() in str(cell).lower() for cell in row)
        ]

    # 排序数据
    if sort_column is not None:
        try:
            sort_column = int(sort_column)  # 确保列索引是整数
            extracted_data.sort(key=lambda x: x[sort_column], reverse=(sort_order == 'desc'))
        except (IndexError, ValueError):
            return JsonResponse({"error": "Invalid sort column"}, status=400)

    # 返回数据给前端
    return JsonResponse({
        "data": extracted_data
    })



def preprocess_image(image_path):
    """
    Preprocess the image: Grayscale and thresholding.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)
    return binary


def extract_table(image_path):
    """
    Detect table structure and extract text.
    """
    # Preprocess the image
    binary = preprocess_image(image_path)

    # Find contours of the table
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_data = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 20:  # Filter noise
            roi = binary[y:y + h, x:x + w]
            # Use PaddleOCR to extract text
            result = ocr.ocr(roi)
            cell_text = ' '.join([line[1][0] for line in result[0]])
            table_data.append((x, y, cell_text))

    # Sort rows and columns
    table_data = sorted(table_data, key=lambda x: (x[1], x[0]))
    return table_data


# Example usage
image_path = "path_to_table_image.jpg"
table = extract_table(image_path)
print(table)
