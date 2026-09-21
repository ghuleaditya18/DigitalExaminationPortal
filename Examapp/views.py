from functools import wraps
from datetime import datetime, timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    ForgotPasswordForm,
    ResetPasswordForm,
    StudentProfileForm,
    UserForm,
)
from .models import Question, Result, UserInfo, Subject


TEST_CONFIGS = {
    10: 15,
    20: 30,
    50: 60,
}

FORM_ERRORS_KEY = 'form_errors'


def _store_form_errors(request, form):
    request.session[FORM_ERRORS_KEY] = {
        field: [str(error) for error in errors]
        for field, errors in form.errors.items()
    }


def _apply_stored_form_errors(request, form):
    errors = request.session.pop(FORM_ERRORS_KEY, None)
    if not errors:
        return form

    form.cleaned_data = {}
    for field, field_errors in errors.items():
        error_field = field if field in form.fields else None
        for error in field_errors:
            form.add_error(error_field, error)
    return form


def _refresh_session_user(request):
    username = request.session.get('username')
    if not username:
        return None

    user = UserInfo.objects.filter(username=username).first()
    if not user:
        request.session.flush()
        return None

    request.session['user_id'] = user.id
    request.session['role'] = user.role
    return user


def session_login_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not _refresh_session_user(request):
            return redirect('login_choice')
        return view(request, *args, **kwargs)
    return wrapped


def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            user = _refresh_session_user(request)
            if not user:
                return redirect('login_choice')
            if user.role != role:
                return redirect('dashboard')
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def LoginChoice(request):
    if request.session.get('username'):
        request.session.flush()
    return render(request, 'User/login_choice.html')


def LoginUser(request, role=None):
    if role not in {'student', 'teacher'}:
        return redirect('login_choice')

    if request.method == 'POST':
        username = (
            request.POST.get(f'{role}_login_name')
            or request.POST.get('username')
        )
        password = (
            request.POST.get(f'{role}_login_secret')
            or request.POST.get('password')
        )
        user = UserInfo.objects.filter(username=username, role=role).first()

        if user and user.locked_until and user.locked_until > timezone.now():
            request.session['login_error'] = (
                'Account is locked. Try again after 15 minutes.'
            )
            return redirect(f'{role}_login')

        if user and user.locked_until:
            user.failed_login_attempts = 0
            user.locked_until = None
            user.save(update_fields=['failed_login_attempts', 'locked_until'])

        if user and check_password(password, user.password):
            user.failed_login_attempts = 0
            user.locked_until = None
            user.save(update_fields=['failed_login_attempts', 'locked_until'])
            request.session['username'] = user.username
            request.session['user_id'] = user.id
            request.session['role'] = user.role
            return redirect('dashboard')

        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = timezone.now() + timedelta(minutes=15)
            user.save(update_fields=['failed_login_attempts', 'locked_until'])

        request.session['login_error'] = f'Invalid {role} username or password'
        return redirect(f'{role}_login')

    return render(request, 'User/login.html', {
        'role': role,
        'error': request.session.pop('login_error', None),
    })


def LogoutUser(request):
    request.session.flush()
    return redirect('login_choice')


@session_login_required
def Dashboard(request):
    if request.session.get('role') == 'teacher':
        context = {
            'question_count': Question.objects.count(),
            'student_count': UserInfo.objects.filter(role='student').count(),
            'attempt_count': Result.objects.count(),
        }
    else:
        context = {
            'attempt_count': Result.objects.filter(
                username_id=request.session['user_id']
            ).count(),
        }
    return render(request, 'dashboard.html', context)


@role_required('teacher')
def CreateQuestion(request):

    subjects = Subject.objects.all().order_by('subject_name')

    if request.method == 'POST':

        Question.objects.create(
            qtext=request.POST.get('qtext', '').strip(),
            opt1=request.POST.get('opt1', '').strip(),
            opt2=request.POST.get('opt2', '').strip(),
            opt3=request.POST.get('opt3', '').strip(),
            opt4=request.POST.get('opt4', '').strip(),
            corr_ans=request.POST.get('corr_ans', '').strip(),
            subject=request.POST.get('subject', '').strip(),
        )

        return redirect('show_all_question')

    return render(
        request,
        'Questions/createquestion.html',
        {
            'subjects': subjects
        }
    )


@role_required('teacher')
def ShowAllQuestion(request):
    return render(request, 'Questions/Showallquestion.html', {
        'data': Question.objects.all()
    })


@role_required('teacher')
def ShowQuestionforUpdate(request, id):
    return render(request, 'Questions/Updatequestion.html', {
        'data': get_object_or_404(Question, qno=id)
    })


@role_required('teacher')
def UpdateQuestion(request, id):
    data = get_object_or_404(Question, qno=id)
    if request.method == 'POST':
        data.qtext = request.POST.get('qtext', '').strip()
        data.opt1 = request.POST.get('opt1', '').strip()
        data.opt2 = request.POST.get('opt2', '').strip()
        data.opt3 = request.POST.get('opt3', '').strip()
        data.opt4 = request.POST.get('opt4', '').strip()
        data.corr_ans = request.POST.get('corr_ans', '').strip()
        data.subject = request.POST.get('subject', '').strip()
        data.save()
        return redirect('show_all_question')
    return render(request, 'Questions/Updatequestion.html', {'data': data})


@role_required('teacher')
def ShowQuestionforDelete(request, id):
    return render(request, 'Questions/deletequestion.html', {
        'data': get_object_or_404(Question, qno=id)
    })


@role_required('teacher')
def DeleteQuestion(request, id):
    data = get_object_or_404(Question, qno=id)
    if request.method == 'POST':
        data.delete()
        return redirect('show_all_question')
    return render(request, 'Questions/deletequestion.html', {'data': data})


def CreateUser(request):
    if request.session.get('role') != 'teacher':
        return redirect('login_choice')

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('show_all_user')
        _store_form_errors(request, form)
        return redirect('create_user')

    form = _apply_stored_form_errors(request, UserForm())
    return render(request, 'User/createuser.html', {
        'form': form,
        'title': 'Create User',
        'subtitle': 'Add a student or teacher account.',
        'submit_label': 'Create Account',
    })


def RegisterUser(request, role=None):
    if role not in {'student', 'teacher'}:
        return redirect('login_choice')

    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = role
            user.save()
            return redirect(f'{role}_login')
        _store_form_errors(request, form)
        return redirect(f'{role}_register')

    form = _apply_stored_form_errors(request, StudentProfileForm())

    return render(request, 'User/createuser.html', {
        'form': form,
        'role': role,
        'title': f'Create {role.title()} Account',
        'subtitle': f'Register as a {role} to access the portal.',
        'submit_label': 'Register',
    })

def ForgotPassword(request, role=None):
    if role not in {'student', 'teacher'}:
        return redirect('login_choice')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            user = UserInfo.objects.filter(
                username=form.cleaned_data['username'],
                mobile_no=form.cleaned_data['mobile_no'],
                role=role,
            ).first()
            if user:
                request.session['reset_user_id'] = user.id
                return redirect('reset_password')
            form.add_error(None, 'No matching account was found.')
        _store_form_errors(request, form)
        return redirect(f'{role}_forgot_password')

    form = _apply_stored_form_errors(request, ForgotPasswordForm())
    return render(request, 'User/forgot_password.html', {'form': form, 'role': role})


def ResetPassword(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('login_choice')
    user = get_object_or_404(UserInfo, id=user_id)
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST, username=user.username)
        if form.is_valid():
            user.password = make_password(form.cleaned_data['password'])
            user.failed_login_attempts = 0
            user.locked_until = None
            user.save(update_fields=[
                'password', 'failed_login_attempts', 'locked_until',
            ])
            request.session.pop('reset_user_id', None)
            return redirect(f'{user.role}_login')
        _store_form_errors(request, form)
        return redirect('reset_password')

    form = _apply_stored_form_errors(
        request,
        ResetPasswordForm(username=user.username)
    )
    return render(request, 'User/reset_password.html', {'form': form})


@role_required('teacher')
def ShowAllUser(request):
    return render(request, 'User/Showalluser.html', {
        'data': UserInfo.objects.all()
    })


@role_required('teacher')
def ShowUserforUpdate(request, id):
    user = get_object_or_404(UserInfo, id=id)
    return render(request, 'User/Updateuser.html', {
        'form': _apply_stored_form_errors(request, UserForm(instance=user)),
        'user': user,
    })


@role_required('teacher')
def UpdateUser(request, id):
    user = get_object_or_404(UserInfo, id=id)
    form = UserForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('show_all_user')
    if request.method == 'POST':
        _store_form_errors(request, form)
        return redirect('show_update_user', id=id)
    form = _apply_stored_form_errors(request, form)
    return render(request, 'User/Updateuser.html', {'form': form, 'user': user})


@role_required('teacher')
def ShowUserforDelete(request, id):
    return render(request, 'User/deleteuser.html', {
        'user': get_object_or_404(UserInfo, id=id)
    })


@role_required('teacher')
def DeleteUser(request, id):
    user = get_object_or_404(UserInfo, id=id)
    if request.method == 'POST':
        user.delete()
    return redirect('show_all_user')


@role_required('student')
def StudentProfile(request):
    user = get_object_or_404(UserInfo, id=request.session['user_id'])
    return render(request, 'User/student_profile.html', {'student': user})


@role_required('student')
def UpdateStudentProfile(request):
    user = get_object_or_404(UserInfo, id=request.session['user_id'])
    form = StudentProfileForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        student = form.save()
        request.session['username'] = student.username
        return redirect('student_profile')
    if request.method == 'POST':
        _store_form_errors(request, form)
        return redirect('update_student_profile')
    form = _apply_stored_form_errors(request, form)
    return render(request, 'User/student_profile_form.html', {'form': form})


@role_required('student')
def DeleteStudentProfile(request):
    user = get_object_or_404(UserInfo, id=request.session['user_id'])
    if request.method == 'POST':
        user.delete()
        request.session.flush()
        return redirect('login_choice')
    return render(request, 'User/student_profile_delete.html', {'student': user})


@role_required('student')
def SubjectPage(request):
    subjects = Subject.objects.all().order_by('subject_name')
    return render(request, 'Result/subject.html', {'subjects': subjects})


@role_required('student')
def StartTest(request):
    subject = request.GET.get('subject')
    try:
        question_limit = int(request.GET.get('question_limit', 0))
    except ValueError:
        question_limit = 0
    if question_limit not in TEST_CONFIGS:
        return redirect('subject')

    questions = Question.objects.filter(
    subject=subject
    ).order_by('?')
    if questions.count() < question_limit:
        return render(request, 'Result/subject.html', {
            'subjects': Subject.objects.all().order_by('subject_name'),
            'error': (
                f'{subject} currently has only {questions.count()} questions. '
                #f'Add at least {question_limit} questions to start this test.'
            ),
        })

    selected_questions = questions[:question_limit]

    allquestions = [{
        'id': q.qno,
        'qno': index,
        'qtext': q.qtext,
        'opt1': q.opt1,
        'opt2': q.opt2,
        'opt3': q.opt3,
        'opt4': q.opt4,
        'corr_ans': q.corr_ans,
        'subject': q.subject,
    }
    for index, q in enumerate(
        selected_questions,
        start=1
    )]
    if not allquestions:
        return render(request, 'Result/subject.html', {
            'subjects': Subject.objects.all().order_by('subject_name'),
            'error': 'No questions are available for that subject.',
        })
    request.session['subject'] = subject
    request.session['allquestions'] = allquestions
    request.session['qno'] = 0
    request.session['answer'] = {}
    request.session['warning_count'] = 0
    request.session['exam_deadline'] = (
        timezone.now() + timedelta(minutes=TEST_CONFIGS[question_limit])
    ).isoformat()
    return render(request, 'Result/starttest.html', _exam_context(request, allquestions[0]))


def _exam_context(request, question, msg=None):
    deadline = datetime.fromisoformat(request.session['exam_deadline'])
    remaining_seconds = max(0, int((deadline - timezone.now()).total_seconds()))
    context = {
        'question': question,
        'total_questions': len(request.session['allquestions']),
        'remaining_seconds': remaining_seconds,
        'warning_count': min(request.session.get('warning_count', 0), 3),
    }
    if msg:
        context['msg'] = msg
    return context


def _test_expired(request):
    deadline = request.session.get('exam_deadline')
    return deadline and timezone.now() >= datetime.fromisoformat(deadline)


def _save_answer(request):
    if 'op' in request.GET:
        allanswer = request.session['answer']
        allanswer[request.GET['qno']] = [
            request.GET['qno'], request.GET['qtext'],
            request.GET['op'].strip(), request.GET['answer'].strip(),
        ]
        request.session['answer'] = allanswer


@role_required('student')
def NextQuestion(request):
    if 'allquestions' not in request.session:
        return redirect('subject')
    _save_answer(request)
    if _test_expired(request):
        return _finalize_test(request, 'Time is up. Your test was submitted automatically.')
    allquestions = request.session['allquestions']
    questionindex = request.session['qno']
    if questionindex < len(allquestions) - 1:
        request.session['qno'] += 1
        return render(request, 'Result/starttest.html', _exam_context(
            request, allquestions[request.session['qno']]
        ))
    return render(request, 'Result/starttest.html', _exam_context(
        request, allquestions[-1], 'This is the Last Question'
    ))


@role_required('student')
def PreviousQuestion(request):
    if 'allquestions' not in request.session:
        return redirect('subject')
    _save_answer(request)
    if _test_expired(request):
        return _finalize_test(request, 'Time is up. Your test was submitted automatically.')
    allquestions = request.session['allquestions']
    questionindex = request.session['qno']
    if questionindex > 0:
        request.session['qno'] -= 1
        return render(request, 'Result/starttest.html', _exam_context(
            request, allquestions[request.session['qno']]
        ))
    return render(request, 'Result/starttest.html', _exam_context(
        request, allquestions[0], 'This is the First Question'
    ))


@role_required('student')
def EndTest(request):
    if 'allquestions' not in request.session:
        return redirect('showresults')
    _save_answer(request)
    submission_message = None
    if _test_expired(request):
        submission_message = 'Time is up. Your test was submitted automatically.'
    elif request.GET.get('submission_reason') == 'window-switch':
        submission_message = (
            'The test was submitted automatically because the window-switch '
            'warning limit was exceeded.'
        )
    return _finalize_test(request, submission_message)


def _finalize_test(request, submission_message=None):
    score = 0
    review_data = []
    for res in request.session['answer'].values():
        is_correct = res[2].strip().casefold() == res[3].strip().casefold()
        score += int(is_correct)
        review_data.append({
            'question': res[1], 'user_answer': res[2],
            'correct_answer': res[3], 'status': is_correct,
        })
    total_questions = len(request.session['allquestions'])
    wrong_answers = total_questions - score
    percentage = round((score / total_questions) * 100, 2) if total_questions else 0
    Result.objects.create(
        username_id=request.session['user_id'],
        subject=request.session['subject'],
        score=score,
        total_questions=total_questions,
        correct_answers=score,
        wrong_answers=wrong_answers,
        percentage=percentage,
    )
    for key in (
        'allquestions', 'qno', 'answer', 'exam_deadline',
        'warning_count', 'subject',
    ):
        request.session.pop(key, None)
    return render(request, 'Result/score.html', {
        'finalscore': score, 'total_questions': total_questions,
        'correct_answers': score, 'wrong_answers': wrong_answers,
        'percentage': percentage, 'review_data': review_data,
        'submission_message': submission_message,
    })


@role_required('student')
def RecordWindowWarning(request):
    if request.method != 'POST' or 'allquestions' not in request.session:
        return JsonResponse({'submit': False, 'warning_count': 0})
    request.session['warning_count'] = min(
        request.session.get('warning_count', 0) + 1,
        4,
    )
    request.session.modified = True
    warning_count = request.session['warning_count']
    return JsonResponse({
        'submit': warning_count >= 3,
        'warning_count': warning_count,
        'message': (
            'Window switching is not allowed. '
            f'Warning {min(warning_count, 3)} of 3.'
        ),
    })


@session_login_required
def show_results(request):
    results = Result.objects.select_related('username')
    sort = request.GET.get('sort', 'percentage_desc')
    min_percentage = request.GET.get('min_percentage', '').strip()
    max_percentage = request.GET.get('max_percentage', '').strip()

    if request.session.get('role') == 'student':
        results = results.filter(
            username_id=request.session['user_id']
        ).order_by('-created_at')
    else:
        if min_percentage:
            try:
                results = results.filter(percentage__gte=float(min_percentage))
            except ValueError:
                min_percentage = ''

        if max_percentage:
            try:
                results = results.filter(percentage__lte=float(max_percentage))
            except ValueError:
                max_percentage = ''

        sort_options = {
            'percentage_desc': '-percentage',
            'percentage_asc': 'percentage',
            'latest': '-created_at',
            'student': 'username__username',
        }
        results = results.order_by(sort_options.get(sort, '-percentage'))

    return render(request, 'Result/show_results.html', {
        'results': results,
        'sort': sort,
        'min_percentage': min_percentage,
        'max_percentage': max_percentage,
    })


def HomePage(request):
    return redirect('login_choice')


@role_required('teacher')
def UserCurdPage(request):
    return redirect('show_all_user')

@role_required('teacher')
def CreateSubject(request):

    if request.method == 'POST':

        subject_name = request.POST.get(
            'subject_name',
            ''
        ).strip()

        if subject_name:

            Subject.objects.create(
                subject_name=subject_name
            )

            return redirect('show_all_subject')

    return render(
        request,
        'Subject/createsubject.html'
    )


@role_required('teacher')
def ShowAllSubject(request):

    return render(
        request,
        'Subject/showallsubject.html',
        {
            'subjects': Subject.objects.all().order_by('subject_id')
        }
    )

@role_required('teacher')
def ShowSubjectForUpdate(request, id):

    subject = get_object_or_404(
        Subject,
        subject_id=id
    )

    return render(
        request,
        'Subject/updatesubject.html',
        {
            'subject': subject
        }
    )


@role_required('teacher')
def UpdateSubject(request, id):

    subject = get_object_or_404(
        Subject,
        subject_id=id
    )

    if request.method == 'POST':

        subject.subject_name = request.POST.get(
            'subject_name',
            ''
        ).strip()

        subject.save()

        return redirect(
            'show_all_subject'
        )

    return render(
        request,
        'Subject/updatesubject.html',
        {
            'subject': subject
        }
    )


@role_required('teacher')
def ShowSubjectForDelete(request, id):

    subject = get_object_or_404(
        Subject,
        subject_id=id
    )

    return render(
        request,
        'Subject/deletesubject.html',
        {
            'subject': subject
        }
    )


@role_required('teacher')
def DeleteSubject(request, id):

    subject = get_object_or_404(
        Subject,
        subject_id=id
    )

    if request.method == 'POST':

        subject.delete()

        return redirect(
            'show_all_subject'
        )

    return render(
        request,
        'Subject/deletesubject.html',
        {
            'subject': subject
        }
    )

@role_required('teacher')
def DeleteResult(request, id):

    result = get_object_or_404(
        Result,
        pk=id
    )

    result.delete()

    return redirect(
        'showresults'
    )

@role_required('teacher')
def DeleteMultipleResults(request):

    if request.method == 'POST':

        ids = request.POST.getlist(
            'selected_results'
        )

        Result.objects.filter(
            id__in=ids
        ).delete()

    return redirect('showresults')
