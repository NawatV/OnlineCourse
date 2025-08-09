from django.shortcuts import render
from django.http import HttpResponseRedirect

# Import any new Models here
from .models import Course, Enrollment, Team, News, Reaction, Comment, Rating  # Added
from django.contrib.auth.decorators import login_required # Added

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


#------------ Task 5 -------------------
from .models import Course, Enrollment, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission_id = submission.id
    return HttpResponseRedirect(reverse(viewname='onlinecourse:exam_result', args=(course_id, submission_id,)))

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = Submission.objects.get(id=submission_id)
    choices = submission.choices.all()

    total_score = 0
    questions = course.question_set.all()  # Assuming course has related questions

    for question in questions:
        correct_choices = question.choice_set.filter(is_correct=True)  # Get all correct choices for the question
        selected_choices = choices.filter(question=question)  # Get the user's selected choices for the question

        # Check if the selected choices are the same as the correct choices
        if set(correct_choices) == set(selected_choices):
            total_score += question.grade  # Add the question's grade only if all correct answers are selected

    context['course'] = course
    context['grade'] = total_score
    context['choices'] = choices

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
#-----------------------------------------------------

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses

    #--- ****** Count each rating_amount before displaying them on course_list_bootstrap.html ---
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_list = context['course_list']

        for course in course_list:
            course.rating_1_count = course.rating_set.filter(rating_amount='rating_1').count()
            course.rating_2_count = course.rating_set.filter(rating_amount='rating_2').count()
            course.rating_3_count = course.rating_set.filter(rating_amount='rating_3').count()
            course.rating_4_count = course.rating_set.filter(rating_amount='rating_4').count()
            course.rating_5_count = course.rating_set.filter(rating_amount='rating_5').count()

            #--- Find the avg with 2-digit decimal ---
            total_ratings = course.rating_1_count*1 +course.rating_2_count*2 +course.rating_3_count*3 +course.rating_4_count*4 +course.rating_5_count*5
            total_count = course.rating_1_count +course.rating_2_count +course.rating_3_count +course.rating_4_count +course.rating_5_count
            course.total_count = total_count
            if total_count == 0:
                course.rating_avg_count = 0
            else:
                course.rating_avg_count = round(total_ratings / total_count, 2) 

            # Get this user's rating (if any)
            if self.request.user.is_authenticated:
                user_rating = course.rating_set.filter(user=self.request.user).first()
                course.user_rating_amount = user_rating.rating_amount if user_rating else None

        return context

#==================== Added ====================
#------- Team ---------------------------
def teaminfo(request):
    return render(request, 'onlinecourse/team_info_bootstrap.html')

class TeamListView(generic.ListView):
    model = Team
    template_name = 'onlinecourse/team_info_bootstrap.html'
    context_object_name = 'team_list'

    def get_queryset(self):
        return Team.objects.all().order_by('start_date')  #Ascending

    #--- ****** Count each rating_amount before displaying them on team_info_bootstrap.html ---
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_list = context['team_list']

        for team in team_list:
            team.rating_1_count = team.rating_set.filter(rating_amount='rating_1').count()
            team.rating_2_count = team.rating_set.filter(rating_amount='rating_2').count()
            team.rating_3_count = team.rating_set.filter(rating_amount='rating_3').count()
            team.rating_4_count = team.rating_set.filter(rating_amount='rating_4').count()
            team.rating_5_count = team.rating_set.filter(rating_amount='rating_5').count()

            #--- Find the avg with 2-digit decimal ---
            total_ratings = team.rating_1_count*1 +team.rating_2_count*2 +team.rating_3_count*3 +team.rating_4_count*4 +team.rating_5_count*5
            total_count = team.rating_1_count +team.rating_2_count +team.rating_3_count +team.rating_4_count +team.rating_5_count
            team.total_count = total_count
            if total_count == 0:
                team.rating_avg_count = 0
            else:
                team.rating_avg_count = round(total_ratings / total_count, 2) 

            # Get this user's rating (if any)
            if self.request.user.is_authenticated:
                user_rating = team.rating_set.filter(user=self.request.user).first()
                team.user_rating_amount = user_rating.rating_amount if user_rating else None

        return context

#------- News ---------------------------
def news(request):
    return render(request, 'onlinecourse/news_bootstrap.html')

class NewsListView(generic.ListView):
    model = News
    template_name = 'onlinecourse/news_bootstrap.html'
    context_object_name = 'news_list'

    def get_queryset(self):
        return News.objects.all().order_by('-pub_date')  #Descending

    #--- ****** Count each reaction_type before displaying them on news_bootstrap.html ---
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news_list = context['news_list']

        for news in news_list:
            news.like_count = news.reaction_set.filter(reaction_type='like').count()
            news.love_count = news.reaction_set.filter(reaction_type='love').count()
            news.dislike_count = news.reaction_set.filter(reaction_type='dislike').count()
            news.angry_count = news.reaction_set.filter(reaction_type='angry').count()

            # Get this user's reaction (if any)
            if self.request.user.is_authenticated:
                user_reaction = news.reaction_set.filter(user=self.request.user).first()
                news.user_reaction_type = user_reaction.reaction_type if user_reaction else None

        return context

#------- Reaction ---------------------------
def add_reaction(request, pk, model_type):
    if request.method == "POST":
        reaction_type = request.POST.get("reaction_type")
        
        if model_type == "news":
            target = News.objects.get(pk=pk)
            reaction_filter = {"user": request.user, "news": target}
            # Delete the existing reaction
            Reaction.objects.filter(**reaction_filter).delete()
            # Add a new reaction 
            Reaction.objects.create(user=request.user, news=target, reaction_type=reaction_type)

    return redirect(request.META.get('HTTP_REFERER', '/'))

#------- Comment ---------------------------
def add_comment(request, pk, model_type):
    if request.method == "POST":
        text = request.POST.get("text")

        if model_type == "news":
            target = News.objects.get(pk=pk)
            Comment.objects.create(user=request.user, news=target, text=text)
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Allow delete only if the user owns the comment
    if request.user == comment.user:
        # Determine redirect target: news or team
        if comment.news:
            post_id = comment.news.id
            model_type = "news"
        else:
            post_id = None
            model_type = None

        comment.delete()

    #return redirect("onlinecourse:news") + f"#news-{post_id}"
    return redirect(request.META.get('HTTP_REFERER', '/'))

#------- Rating ---------------------------
def add_rating(request, pk, model_type):
    if request.method == "POST":
        rating_amount = request.POST.get("rating_amount")
        
        if model_type == "course":
            target = Course.objects.get(pk=pk)
            rating_filter = {"user": request.user, "course": target}
            # Delete the existing rating
            Rating.objects.filter(**rating_filter).delete()
            # Add a new rating 
            Rating.objects.create(user=request.user, course=target, rating_amount=rating_amount)

        elif model_type == "team":
            target = Team.objects.get(pk=pk)
            rating_filter = {"user": request.user, "team": target}
                #X: Rating.objects.create(user=request.user, team=target, rating_amount=rating_amount)
            # Delete the existing rating
            Rating.objects.filter(**rating_filter).delete()
            # Add a new rating 
            Rating.objects.create(user=request.user, team=target, rating_amount=rating_amount)

    return redirect(request.META.get('HTTP_REFERER', '/'))
#================================================

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))

# An example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
   submitted_anwsers = []
   for key in request.POST:
       if key.startswith('choice'):
           value = request.POST[key]
           choice_id = int(value)
           submitted_anwsers.append(choice_id)
   return submitted_anwsers