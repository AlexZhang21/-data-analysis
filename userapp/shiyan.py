'''
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Prefetch
from django.contrib import messages
from django.conf import settings
from django.forms.models import model_to_dict

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.views import View
from django.urls import reverse_lazy
from django.core.files.storage import FileSystemStorage

from .forms import UserForm, CreateNewUserForm, changePasswordForm, companyForm, filterForm
from .models import CompanyFile, CompanycreatedRecord, Company, comp_type, product, payment, bank
from datetime import datetime

import os, shutil, mimetypes

# 用户登录视图
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
            messages.error(request, 'username OR password incorrect')
    return render(request, 'userapp/index.html')

# 主页视图
def homePage(request):
    fs = FileSystemStorage()
    if request.user.is_anonymous:
        messages.error(request, 'Invalid to go without Login !!!')
        return redirect('/')

    form = filterForm()
    form.fields['company_type'].choices = comp_type
    form.fields['product'].choices = product
    form.fields['payment'].choices = payment
    form.fields['issuing_bank'].choices = bank
    form.fields['receiving_bank'].choices = bank
    form.fields['tt_bank'].choices = bank
    all_details = Company.objects.all().prefetch_related()
    return render(request, 'userapp/content_table.html', {'form': form, 'company_list': all_details, 'base': 'userapp/base2.html'})

# 创建公司视图，包含文件上传
def create_company_form(request):
    if request.user.is_anonymous:
        messages.error(request, 'Invalid to go without Login !!!')
        return redirect('/')
    if request.method == 'POST':
        form = companyForm(request.POST, request.FILES)
        if form.is_valid():
            changes = form.save(commit=False)
            companyname = request.POST.get('company_name')
            counter_onboard = request.POST.get('counterparty_onboard_status')
            serenity_onboard = request.POST.get('serenity_onboard_status')
            checkcompany_name = Company.objects.filter(company_name=companyname).values()
            if len(checkcompany_name) > 0:
                messagess = 'Duplicated name in company name!'
                return render(request, 'userapp/create_new_details.html', {'form': form, 'messages': messagess, 'base': 'userapp/base.html'})
            if counter_onboard == 'Complete':
                changes.counterparty_onboard_date = datetime.today()
            if serenity_onboard == 'Complete':
                changes.serenity_onboard_date = datetime.today()
            changes.save()
            form.save_m2m()

            # 获取新上传的公司详情记录
            getimport = Company.objects.filter(company_name=companyname).values()
            if len(getimport) == 0:
                messagess = 'Something wrong with database! No company name here'
                return render(request, 'userapp/create_new_details.html', {'form': form, 'messages': messagess, 'base': 'userapp/base.html'})
            if len(getimport) != 1:
                messagess = 'Duplicated name in company name! Please contact admin!'
                return render(request, 'userapp/create_new_details.html', {'form': form, 'messages': messagess, 'base': 'userapp/base.html'})

            # 保存公司创建记录
            saverecordobj = CompanycreatedRecord()
            saverecordobj.company_id = int(getimport[0]['id'])
            saverecordobj.done_by = request.user.get_full_name()
            saverecordobj.date = datetime.today()
            saverecordobj.remark = companyname + ' created by ' + request.user.get_full_name()
            saverecordobj.save()

            newcmpname = companyname.replace(" ", "_")
            locdir = os.path.join(settings.MEDIA_ROOT, newcmpname)
            # 检查目录是否存在
            if os.path.exists(locdir):
                shutil.rmtree(locdir)
            os.mkdir(locdir)

            if len(request.FILES) > 0:
                for a in request.FILES.getlist('file_upload'):
                    with open(os.path.join(locdir, a.name), 'wb+') as destination:
                        for chunks in a.chunks():
                            destination.write(chunks)
                    saveobj = CompanyFile()
                    saveobj.filename = a.name
                    saveobj.filepath = os.path.join(locdir, a.name)
                    saveobj.company_id = int(getimport[0]['id'])
                    saveobj.uploaded_date = datetime.today()
                    saveobj.save()

                    # 保存文件上传记录
                    saverecordobj = CompanycreatedRecord()
                    saverecordobj.company_id = int(getimport[0]['id'])
                    saverecordobj.done_by = request.user.get_full_name()
                    saverecordobj.date = datetime.today()
                    saverecordobj.remark = request.user.get_full_name() + ' uploaded file ' + a.name
                    saverecordobj.save()

            form = companyForm()
            return redirect('Home')
        else:
            return render(request, 'userapp/create_new_details.html', {'form': form, 'base': 'userapp/base.html'})
    else:
        form = companyForm()
    return render(request, 'userapp/create_new_details.html', {'form': form, 'base': 'userapp/base.html'})

# 其他视图函数...


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

def userPage(request, pk):
    print('User page')
    if request.user.is_anonymous:
        print('lol not again')
        messages.error(request, 'Invalid to go without Login !!!')
        return redirect('/')
    if request.user.id != pk and not request.user.is_superuser:
        messages.error(request,'You are not the user!!')
        return redirect('Home')
    try:
        certain_user = User.objects.get(id=pk)
    except:
        messages.error(request,'User not existed!!!')
        return redirect('Home')
    if request.method == 'POST':
        form = UserForm(request.POST, instance=certain_user)
        # print(form)
        if form.is_valid():
            form.save()
            if request.user.is_superuser:
                return redirect('Ad_User_details')
            else:
                return redirect('Home')
    else:
        form = UserForm(instance=certain_user)
    return render(request,'userapp/user_details.html', {'form': form, 'base': 'userapp/base.html'})

def edit_Company(request, pk):
    print('Edit company page')
    comp_item = Company.objects.all().prefetch_related().get(id=pk)
    if request.user.is_anonymous:
        print('lol not again')
        messages.error(request, 'Invalid to go without Login !!!')
        return redirect('/')
    if request.method == 'POST':
        form = companyForm(request.POST, instance=comp_item)
        # print(form)
        if form.is_valid():
            changes = form.save(commit=False)
            # declare here
            check = Company.objects.get(id=pk)

            changes_dict = {}
            for intech in form.changed_data:
                if intech == 'company_type':
                    norm = [new.company_type for new in check.company_type.all()]
                elif intech == 'payment':
                    norm = [new.payment_type for new in check.payment.all()]
                elif intech == 'product':
                    norm = [new.product_type for new in check.product.all()]
                elif intech == 'issuing_bank':
                    norm = [new.bank_name for new in check.issuing_bank.all()]
                elif intech == 'receiving_bank':
                    norm = [new.bank_name for new in check.receiving_bank.all()]
                elif intech == 'tt_bank':
                    norm = [new.bank_name for new in check.tt_bank.all()]
                else:
                    norm = Company.objects.values_list(intech,flat=True).filter(id=pk)
                norm = list(norm)
                norm = [str(new) for new in norm]
                # print(norm)
                norm_str = ','.join(norm)
                if len(norm_str) == 0:
                    norm_str = 'empty'
                # print(norm_str)
                changes_dict[intech] = norm_str
            # print(form.has_changed())
            # print(form.changed_data)

            counter_onboard = request.POST.get('counterparty_onboard_status')
            serenity_onboard = request.POST.get('serenity_onboard_status')
            if counter_onboard == 'Complete':
                if check.counterparty_onboard_status != 'Complete':
                    changes.counterparty_onboard_date = datetime.today()
            if serenity_onboard == 'Complete':
                if check.serenity_onboard_status != 'Complete':
                    changes.serenity_onboard_date = datetime.today()
            changes.save()
            form.save_m2m()

            # refind again
            checkagn = Company.objects.get(id=pk)
            for item in changes_dict.keys():
                if item == 'company_type':
                    norm = [new.company_type for new in checkagn.company_type.all()]
                elif item == 'payment':
                    norm = [new.payment_type for new in checkagn.payment.all()]
                elif item == 'product':
                    norm = [new.product_type for new in checkagn.product.all()]
                elif item == 'issuing_bank':
                    norm = [new.bank_name for new in checkagn.issuing_bank.all()]
                elif item == 'receiving_bank':
                    norm = [new.bank_name for new in checkagn.receiving_bank.all()]
                elif item == 'tt_bank':
                    norm = [new.bank_name for new in checkagn.tt_bank.all()]
                else:
                    norm = Company.objects.values_list(item,flat=True).filter(id=pk)
                norm = list(norm)
                norm = [str(new) for new in norm]
                norm_str = ','.join(norm)
                if len(norm_str) == 0:
                    norm_str = 'empty'

                saverecordobj = CompanycreatedRecord()
                saverecordobj.company_id = pk
                saverecordobj.done_by = request.user.get_full_name()
                saverecordobj.date = datetime.today()
                saverecordobj.remark = request.user.get_full_name() + ' edited '+ item +' record from ' + changes_dict[item] + ' into ' + norm_str
                saverecordobj.save()
            return redirect('Home')
    else:
        form = companyForm(instance=comp_item)
    return render(request,'userapp/edit_company_details.html', {'form': form, 'base': 'userapp/base.html'})

def company_file(request,pk):
    if request.user.is_anonymous:
        print('lol not again')
        messages.error(request, 'Invalid to go without Login !!!')
        return redirect('/')
    print('Company file page')
    comp_file = CompanyFile.objects.filter(company_id=pk)
    compan = Company.objects.get(id=pk)
    com_name = str(compan.company_name)
    if request.method == 'POST':
        if len(request.FILES) > 0:
            newcmpname = com_name.replace(" ", "_")
            locdir = os.path.join(settings.MEDIA_ROOT, newcmpname)

            if not os.path.exists(locdir):
                # make record
                saverecordobj = CompanycreatedRecord()
                saverecordobj.company_id = pk
                saverecordobj.done_by = request.user.get_full_name()
                saverecordobj.date = datetime.today()
                saverecordobj.remark = 'Directory '+ newcmpname + ' has missing. Rebuild'
                saverecordobj.save()
                os.mkdir(locdir)
            # check if directory exist or not
            for a in request.F    form = companyForm()
    return render(request, 'userapp/company_file.html',
                  {'comp_file': comp_file, 'com_name': com_name,'form':form,'prim':pk, 'base': 'userapp/base.html'})

def delete_file(request,pk):
    print('delete file')
    comp_file = CompanyFile.objects.get(id=pk)
    file_path = str(comp_file.filepath)
    filename = str(comp_file.filename)
    comp_id = int(comp_file.company_id)
    if os.path.exists(file_path):
        # make record
        saverecordobj = CompanycreatedRecord()
        saverecordobj.company_id = comp_id
        saverecordobj.done_by = request.user.get_full_name()
        saverecordobj.date = datetime.today()
        saverecordobj.remark = request.user.get_full_name() + ' deleted file ' + filename
        saverecordobj.save()
        os.remove(file_path)
        # delete record
        comp_file.delete()
    return redirect('Company_file', pk=comp_id)

def download_file(request,pk):
    getpath = CompanyFile.objects.get(id=pk)
    path = str(getpath.filepath)
    filename = path.split('\\')[-1]
    filepath = open(path, 'rb')
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(path)
    # Set the return value of the HttpResponse
    response = HttpResponse(filepath, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response


def changePassword(request, pk):
    print('Change password')
    certain_user = User.objects.get(id=pk)
    # print(len(certain_user))
    # if request.user.is_authenticated:
    if request.user.is_anonymous:
        print('lol not again')
        messages.error(request, 'Invalid to go without Login !!!')
        return redirect('/')
    if request.method == 'POST':
        form = changePasswordForm(request.POST, instance=certain_user)
        # print(form)
        if form.is_valid():
            certain_user.set_password(request.POST.get('password'))
            certain_user.save()
            update_session_auth_hash(request, certain_user)
            return redirect('Ad_User_details')
    else:
        form = changePasswordForm(instance=certain_user)
    return render(request,'userapp/change_password.html', {'form': form, 'base': 'userapp/base.html'})


def aduserPage(request):
    # if request.user.is_authenticated:
    if request.user.is_anonymous:
        messages.error(request, 'Invalid to go without Login !!!')
        return redirect('/')ILES.getlist('file_upload'):
                print(a.name)
                with open(os.path.join(locdir, a.name), 'wb+') as destination:
                    for chunks in a.chunks():
                        destination.write(chunks)
                saveobj = CompanyFile()
                saveobj.filename = a.name
                saveobj.filepath = os.path.join(locdir, a.name)
                saveobj.company_id = pk
                saveobj.uploaded_date = datetime.today()
                saveobj.save()

                # make record
                saverecordobj = CompanycreatedRecord()
                saverecordobj.company_id = pk
                saverecordobj.done_by = request.user.get_full_name()
                saverecordobj.date = datetime.today()
                saverecordobj.remark = request.user.get_full_name() + ' uploaded file ' + a.name
                saverecordobj.save()
        else:
            messages.error(request, 'Form not valid!!')
        comp_file = CompanyFile.objects.filter(company_id=pk)
        compan = Company.objects.get(id=pk)
        com_name = str(compan.company_name)
'''


'''
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
'''


'''
{% extends "userapp/base.html" %}

{% block content %}
<div class="container">
    <h2>Analyze File for {{ product_entry.product }}</h2>

    <!-- Display uploaded file -->
    {% if product_entry.uploaded_file %}
    <div class="row">
        <div class="col-md-6">
            <h4>Uploaded File:</h4>
            <img src="{{ product_entry.uploaded_file.url }}" class="img-fluid" alt="Uploaded File">
        </div>
    </div>
    {% endif %}

    <!-- Search and Filter -->
    <div class="row mt-4">
        <div class="col-md-6">
            <h4>Search:</h4>
            <input type="text" id="searchInput" class="form-control" placeholder="Enter keyword...">
        </div>
        <div class="col-md-6">
            <h4>Sort:</h4>
            <select id="sortColumn" class="form-control">
                <option value="">Sort By Column</option>
                <option value="0">Column 1</option>
                <option value="1">Column 2</option>
                <option value="2">Column 3</option>
                <option value="3">Column 4</option>
                <option value="4">Column 5</option>
            </select>
        </div>
    </div>

    <!-- Editable Filtered Table -->
    <div class="row mt-4">
        <div class="col-md-12">
            <h4>Filtered Results (Editable):</h4>
            <div id="editableTable" class="traditional-table"></div>
        </div>
    </div>

    <!-- Hidden input to store table data -->
    <form method="POST" id="filteredForm">
        {% csrf_token %}
        <input type="hidden" name="filtered_data" id="filteredData">
        <div class="row mt-4">
            <div class="col-md-12">
                <button type="submit" class="btn btn-primary">Save Changes</button>
                <a href="{% url 'content_table' %}" class="btn btn-secondary">Cancel</a>
            </div>
        </div>
    </form>
</div>

<!-- Include Handsontable -->
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.css"
/>
<script src="https://cdn.jsdelivr.net/npm/handsontable/dist/handsontable.full.min.js"></script>

<!-- Custom Styles for Traditional Table Look -->
<style>
    .traditional-table .htCore {
        border-collapse: collapse;
        width: 100%;
    }
    .traditional-table .htCore th,
    .traditional-table .htCore td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .traditional-table .htCore th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .traditional-table .ht_master {
        overflow: visible !important;
    }
</style>

<script>
    document.addEventListener("DOMContentLoaded", function () {
        const container = document.getElementById("editableTable");

        // Initialize Handsontable with editable columns
        const hot = new Handsontable(container, {
            data: {{ search_results|safe }},
            rowHeaders: false,
            colHeaders: ["Column 1", "Column 2", "Column 3", "Column 4", "Column 5"],
            columns: [
                { data: 0, editor: "text" }, // Enable editing for Column 1
                { data: 1, editor: "text" }, // Enable editing for Column 2
                { data: 2, editor: "text" }, // Enable editing for Column 3
                { data: 3, editor: "text" }, // Enable editing for Column 4
                { data: 4, editor: "text" }, // Enable editing for Column 5
            ],
            contextMenu: true, // Enables right-click context menu for advanced operations
            manualRowResize: true,
            manualColumnResize: true,
            allowInsertColumn: true,
            allowInsertRow: true,
            allowRemoveColumn: true,
            allowRemoveRow: true,
            licenseKey: "non-commercial-and-evaluation",
            className: "traditional-table", // Apply custom styles
        });

        // Search functionality
        document.getElementById("searchInput").addEventListener("input", function () {
            const query = this.value.toLowerCase();
            const filteredData = {{ search_results|safe }}.filter(row =>
                row.some(cell => cell?.toString().toLowerCase().includes(query))
            );
            hot.loadData(filteredData);
        });

        // Sorting functionality
        document.getElementById("sortColumn").addEventListener("change", function () {
            const columnIndex = parseInt(this.value);
            if (!isNaN(columnIndex)) {
                const sortedData = [...hot.getData()].sort((a, b) =>
                    (a[columnIndex] || "").toString().localeCompare((b[columnIndex] || "").toString())
                );
                hot.loadData(sortedData);
            }
        });

        // Save table data on form submission
        const form = document.getElementById("filteredForm");
        form.addEventListener("submit", function (e) {
            const tableData = hot.getData();
            document.getElementById("filteredData").value = JSON.stringify(tableData);
        });
    });
</script>
{% endblock %}
'''