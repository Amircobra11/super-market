from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserPanelDashBoardView.as_view(), name='user-panel-dashboard'),
    path('change_password/', views.ChangePasswordPage.as_view(), name='change-password-page'),
    path('edit-profile/', views.EditUserProfilePage.as_view(), name='edit-profile-page'),
    path('user-basket/', views.user_basket, name='user-basket-page'),
    path('my-shopping/', views.MyShopping.as_view(), name='user-shopping-page'),
    path('my-shopping-detail/<order_id>', views.my_shopping_detail, name='user-shopping-detail-page'),
    path('remove-order-detail/', views.remove_order_detail, name='remove-order-detail-ajax'),
    path('change-order-detail/', views.change_order_detail_count, name='change-order-detail-count-ajax'),
]
