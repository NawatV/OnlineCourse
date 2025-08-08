from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL
    path(route='', view=views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    # ex: /onlinecourse/5/
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    # ex: /enroll/5/
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),

    #------------ Task 5 ---------------------------------
    path('<int:course_id>/submit/', views.submit, name="submit"),
    path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name="exam_result"),
    #-----------------------------------------------------

    #------------ Added ----------------------------------
    path('teaminfo/', views.TeamListView.as_view(), name='teaminfo'),
    path('news/', views.NewsListView.as_view(), name='news'),
    path('reaction/<int:pk>/<str:model_type>/', views.add_reaction, name='add_reaction'),
    path('comment/<int:pk>/<str:model_type>/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('rating/<int:pk>/<str:model_type>/', views.add_rating, name='add_rating'),
    #-----------------------------------------------------

 ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
