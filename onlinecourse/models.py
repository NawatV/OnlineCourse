import sys, os # Added
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid
from uuid import uuid4 # Added
from django.contrib.auth.models import User # Added


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation

#------------------ Added ------------------
# Fixed using the wrong image (caching) & flexible for any folder
def upload_to_unique_image_dir(base_dir):
    def unique_image_dir(instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{uuid4().hex}.{ext}"
        return os.path.join(base_dir, filename)
    return unique_image_dir

# Fixed 'ValueError: Could not find function unique_image_dir in onlinecourse.models.'
def upload_to_course_images(instance, filename):
    return upload_to_unique_image_dir('course_images')(instance, filename)
def upload_to_team_images(instance, filename):
    return upload_to_unique_image_dir('team_images')(instance, filename)
def upload_to_news_images(instance, filename):
    return upload_to_unique_image_dir('news_images')(instance, filename)
#------------------------------------------

# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to=upload_to_course_images, null=True, blank=True)
        #X: image = models.ImageField(upload_to='course_images/')
        #X-Error: upload_to_dir('course_images')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description

#------------------ Added ------------------
# Team model
class Team(models.Model):
    fullname = models.CharField(null=False, max_length=100, default='Anonymous')
    image = models.ImageField(upload_to=upload_to_team_images, null=True, blank=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    contact = models.CharField(null=False, max_length=100, default='Contact')
    role = models.CharField(max_length=500)
    description = models.TextField(max_length=5000, blank=True)

    def __str__(self):
        return "Full Name: " + self.fullname + "," + \
               "Role: " + self.role

# News model
class News(models.Model):
    title = models.CharField(null=False, max_length=100, default='Title')
    image = models.ImageField(upload_to=upload_to_news_images, null=True, blank=True)
    pub_date = models.DateField(null=True)
    mod_date = models.DateField(null=True)
    url = models.CharField(null=True, max_length=500, default='URL')
    keyword = models.TextField(max_length=1000, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return "Title: " + self.title + "," + \
               "Published: " + str(self.pub_date) + "," + \
               "Modified: " + str(self.mod_date)

# Reaction model
class Reaction(models.Model):
    REACTION_TYPES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('dislike', 'Dislike'),
        ('angry', 'Angry'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey('News', null=True, blank=True, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    reacted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  "User:" + str(self.user) + ", " + \
                "News:" + str(self.news) + ", " + \
                "Reacted at: " + str(self.reacted_at)

# Comment model
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey('News', null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField(null=False, max_length=5000, blank=True)
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  "User:" + str(self.user) + ", " + \
                "News:" + str(self.news) + ", " + \
                "Commented at: " + str(self.commented_at)

# Rating model
class Rating(models.Model):
    RATING_AMOUNTS = [
        ('rating_1', 'rating_1'),
        ('rating_2', 'rating_2'),
        ('rating_3', 'rating_3'),
        ('rating_4', 'rating_4'),
        ('rating_5', 'rating_5'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', null=True, blank=True, on_delete=models.CASCADE)
    team = models.ForeignKey('Team', null=True, blank=True, on_delete=models.CASCADE)
    rating_amount = models.CharField(max_length=10, choices=RATING_AMOUNTS)
    rated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  "User:" + str(self.user) + ", " + \
                "Course:" + str(self.course) + ", " + \
                "Team:" + str(self.team) + ", " + \
                "Rated at: " + str(self.rated_at)
#-------------------------------------------

# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()


# Enrollment model
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

#------------ Task 1 -------------------
class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    grade = models.IntegerField(default=50)

    def __str__(self):
        return "Question: " + self.content

    # Cal if the learner gets the score of the question
    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(is_correct=True).count()
                               #choice_set: allows access to all the Choice objs.
                               #id__in: a field lookup: only the ones whose id='selected_id' will be included   
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        if all_answers == selected_correct:
            return True
        else:
            return False

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

# One enrollment could have multiple submission
# One submission could have multiple choices
# One choice could belong to multiple submissions
