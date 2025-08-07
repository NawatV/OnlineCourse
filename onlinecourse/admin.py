from django.contrib import admin
#------------ Task 2 -------------------
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission, Team, News, Reaction, Comment # Added

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2
#----------------------------------------

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5

#------------ Task 2 -------------------
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['content']
#----------------------------------------

class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)

#------------ Task 2 -------------------
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
#----------------------------------------

#------------ Added -------------------
admin.site.register(Team)
admin.site.register(News)
admin.site.register(Reaction)
admin.site.register(Comment)
#----------------------------------------