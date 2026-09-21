from django.db import models

class Question(models.Model):
    qno = models.AutoField(primary_key=True)
    qtext = models.TextField()

    opt1 = models.CharField(max_length=100)
    opt2 = models.CharField(max_length=100)
    opt3 = models.CharField(max_length=100)
    opt4 = models.CharField(max_length=100)

    corr_ans = models.CharField(max_length=120)
    subject = models.CharField(max_length=120)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.qtext
    
class UserInfo(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    mobile_no = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Result(models.Model):

    username = models.ForeignKey(
        UserInfo,
        on_delete=models.CASCADE
    )

    subject = models.CharField(max_length=100)

    score = models.IntegerField()

    total_questions = models.IntegerField(default=0)

    correct_answers = models.IntegerField(default=0)

    wrong_answers = models.IntegerField(default=0)

    percentage = models.FloatField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
class Feedback(models.Model):

    username = models.ForeignKey(
        UserInfo,
        on_delete=models.CASCADE
    )

    subject = models.CharField(max_length=100)

    rating = models.CharField(max_length=20)

    comments = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.rating
    
class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name
