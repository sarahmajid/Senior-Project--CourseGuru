from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import userratings
from CourseGuru_App.models import courseusers
from CourseGuru_App.models import course
from CourseGuru_App.models import botanswers

def delCourse(cid):
    tempQues = questions.objects.filter(course_id = cid)
    for x in tempQues:
        tempAns = answers.objects.filter(question_id = x.id)
        #Delete user ratings in course
        for y in tempAns:
            if userratings.objects.filter(answer_id = y.id).exists():
                userratings.objects.filter(answer_id = y.id).delete()
        #Delete answers in course
        if answers.objects.filter(question_id = x.id).exists():
            answers.objects.filter(question_id = x.id).delete()
    #Delete questions in course
    if questions.objects.filter(course_id = cid).exists():
        questions.objects.filter(course_id = cid).delete()
    #Delete course users
    if courseusers.objects.filter(course_id = cid).exists():
        courseusers.objects.filter(course_id = cid).delete()
    #Delete course
    if course.objects.filter(id = cid).exists():
        course.objects.filter(id = cid).delete()
    #Delete botanswers related to this course
    if botanswers.objects.filter(course_id = cid).exists():
        botanswers.objects.filter(course_id = cid).delete()
        
def delQuestion(qid):
    tempAns = answers.objects.filter(question_id = qid)
    for x in tempAns:
        if userratings.objects.filter(answer_id = x.id).exists():
            userratings.objects.filter(answer_id = x.id).delete()
    if answers.objects.filter(question_id = qid).exists():
        answers.objects.filter(question_id = qid).delete()
    if questions.objects.filter(id = qid).exists():
        questions.objects.filter(id = qid).delete()
        
def delAnswers(aid):
    if userratings.objects.filter(answer_id = aid).exists():
        userratings.objects.filter(answer_id = aid).delete()
    if answers.objects.filter(id = aid).exists():
        answers.objects.filter(id = aid).delete()