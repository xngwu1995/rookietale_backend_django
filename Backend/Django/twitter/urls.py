"""twitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from accounts.api.views import UserProfileViewSet, UserViewSet, AccountViewSet
from chatgpt.api.views import ChatgptViewSet
from inbox.api.views import NotificationViewSet
from orders.api.views import MenuViewSet, OrderViewSet, SessionViewSet
from stocks.api.views import StockViewSet, StrategyStockViewSet, TradeRecordViewSet, AIAnalysisViewSet
from taskmanager.api.views import TaskmanagerViewSet
from tweets.api.views import TweetViewSet
from friendships.api.views import FriendshipViewSet
from newsfeeds.api.views import NewsFeedViewSet
from comments.api.views import CommentViewSet
from likes.api.views import LikeViewSet
from rest_framework_simplejwt.views import TokenRefreshView
import debug_toolbar

router = routers.DefaultRouter()
router.register(r'api/users', UserViewSet)
router.register(r'api/accounts', AccountViewSet, basename = 'accounts')
router.register(r'api/tweets', TweetViewSet, basename = 'tweets')
router.register(r'api/friendships', FriendshipViewSet, basename = 'friendships')
router.register(r'api/newsfeeds', NewsFeedViewSet, basename = 'newsfeeds')
router.register(r'api/comments', CommentViewSet, basename = 'comments')
router.register(r'api/likes', LikeViewSet, basename = 'likes')
router.register(r'api/notifications', NotificationViewSet, basename = 'notifications')
router.register(r'api/profiles', UserProfileViewSet, basename='profiles')
router.register(r'api/chatgpt', ChatgptViewSet, basename='chatgpt')
router.register(r'api/taskmanager', TaskmanagerViewSet, basename='taskmanager')
router.register(r'api/stocks/strategy', StrategyStockViewSet, basename='strategy')
router.register(r'api/stocks/record', TradeRecordViewSet, basename='record')
router.register(r'api/stocks/ai', AIAnalysisViewSet, basename='AIStock')
router.register(r'api/stocks', StockViewSet, basename='stocks')
router.register(r'api/sessions', SessionViewSet, basename='sessions')
router.register(r'api/orders', OrderViewSet, basename='orders')
router.register(r'api/menus', MenuViewSet, basename='menus')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
