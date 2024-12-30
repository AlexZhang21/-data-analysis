from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.loginPage, name='Login'),
    path('admin_user_details/', views.aduserPage, name='Ad_User_details'),
    path('create_new_user/', views.create_new_user, name='New_User_details'),
    path('user_details/<int:pk>/', views.userPage, name='User_details'),
    path('company_file/<int:pk>/', views.company_file, name='Company_file'),
    path('download_file/<int:pk>/', views.download_file, name='Download_File'),
    path('edit_company_details/<int:pk>/', views.edit_Company, name='Edit_Company'),
    path('change_password/<int:pk>/', views.changePassword, name='Change_Password'),
    path('delete_user/<str:username>/', views.del_user, name='Delete_User'),
    path('delete_comp_record/<int:pk>/', views.del_item, name='Delete_Company_Record'),
    path('delete_file/<int:pk>/', views.delete_file, name='Delete_File'),
    path('content_table/', views.homePage, name='Home'),
    path('content_table/', views.homePage, name='content_table'),
    path('create_company/', views.create_company_form, name='create_company_form'),
    path('company_details/<int:pk>', views.companyPage, name='Comp_details'),
    path('Logout/', views.logoutAction, name='Logout'),
    path('edit_product_entry/<int:pk>/', views.edit_product_entry, name='edit_product_entry'),
    path('delete_product_entry/<int:pk>/', views.delete_product_entry, name='delete_product_entry'),

    # 新增的路径
    path('create/', views.create_product_entry, name='create_product_entry'),  # 创建产品条目
    path('products/', views.product_list, name='product_list'),  # 查看产品列表

    # 新增文件上传与查看路径
    path('upload_file/', views.upload_file, name='upload_file'),  # 上传文件
    path('view_uploaded_files/', views.view_uploaded_files, name='view_uploaded_files'),  # 查看上传的文件
    path('delete_uploaded_file/<int:pk>/', views.delete_uploaded_file, name='delete_uploaded_file'),  # 删除上传的文件
    path('analyze_image/<int:pk>/', views.analyze_image, name='analyze_image'),
    path('enhanced-table/<int:pk>/', views.enhanced_table_view, name='enhanced_table'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


