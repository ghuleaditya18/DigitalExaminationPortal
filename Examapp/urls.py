from django.urls import path
from . import views
urlpatterns = [
    path('', views.LoginChoice, name='login_choice'),
    path('create-question/', views.CreateQuestion, name='create_question'),
    path('create-subject/',views.CreateSubject,name='create_subject'),
    path('show-subject/',views.ShowAllSubject,name='show_all_subject'),
    path('update-subject/<int:id>/',views.ShowSubjectForUpdate,name='show_update_subject'),
    path('update-subject-data/<int:id>/',views.UpdateSubject,name='update_subject'),
    path('delete-subject/<int:id>/',views.ShowSubjectForDelete,name='show_delete_subject'),
    path('delete-subject-confirm/<int:id>/',views.DeleteSubject,name='delete_subject'),
    
    path('show-question/', views.ShowAllQuestion, name='show_all_question'),
    path('update-question/<int:id>/', views.ShowQuestionforUpdate, name='show_update_question'),
    path('update-question-data/<int:id>/', views.UpdateQuestion, name='update_question'),
    path('delete-question/<int:id>/', views.ShowQuestionforDelete, name='show_delete_question'),
    path('delete-question-confirm/<int:id>/', views.DeleteQuestion, name='delete_question'),

    path('user-curd/', views.UserCurdPage, name='user_curd'),

    path('create-user/', views.CreateUser, name='create_user'),
    path('register/student/', views.RegisterUser, {'role': 'student'}, name='student_register'),
    path('register/teacher/', views.RegisterUser, {'role': 'teacher'}, name='teacher_register'),
    path('show-user/', views.ShowAllUser, name='show_all_user'),

    path('update-user/<int:id>/', views.ShowUserforUpdate, name='show_update_user'),
    path('update-user-data/<int:id>/', views.UpdateUser, name='update_user'),

    path('delete-user/<int:id>/', views.ShowUserforDelete, name='show_delete_user'),
    path('delete-user-confirm/<int:id>/', views.DeleteUser, name='delete_user'),

    path('login/', views.LoginChoice, name='login'),
    path('login/student/', views.LoginUser, {'role': 'student'}, name='student_login'),
    path('login/teacher/', views.LoginUser, {'role': 'teacher'}, name='teacher_login'),
    path('forgot-password/student/', views.ForgotPassword, {'role': 'student'}, name='student_forgot_password'),
    path('forgot-password/teacher/', views.ForgotPassword, {'role': 'teacher'}, name='teacher_forgot_password'),
    path('verify-otp/', views.VerifyOTP, name='verify_otp'),
    path('resend-otp/', views.ResendOTP, name='resend_otp'),
    path('reset-password/', views.ResetPassword, name='reset_password'),
    path('logout/', views.LogoutUser, name='logout'),

    path('home/', views.HomePage, name='home'),
    path('dashboard/', views.Dashboard, name='dashboard'),
    path('profile/', views.StudentProfile, name='student_profile'),
    path('profile/update/', views.UpdateStudentProfile, name='update_student_profile'),
    path('profile/delete/', views.DeleteStudentProfile, name='delete_student_profile'),

    path('subject/', views.SubjectPage, name='subject'),
    path('start-test/', views.StartTest, name='start_test'),
    path('next-question/',views.NextQuestion,name='next_question'),
    path('previous-question/',views.PreviousQuestion,name='previous_question'),
    path('end-test/',views.EndTest,name='end_test'),
    path('record-window-warning/', views.RecordWindowWarning, name='record_window_warning'),

    path('showresults/', views.show_results, name='showresults'),

    path( 'delete-result/<int:id>/',views.DeleteResult,name='delete_result'),
    path('delete-multiple-results/',views.DeleteMultipleResults,name='delete_multiple_results'),
]
