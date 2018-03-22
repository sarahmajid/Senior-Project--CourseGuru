import nltk
from nltk.corpus import stopwords
from nltk.tokenize.moses import MosesDetokenizer

from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import userratings
from CourseGuru_App.models import courseusers
from CourseGuru_App.models import course
from CourseGuru_App.models import botanswers
from CourseGuru_App.models import User

from CourseGuru_App.luisRun import teachLuis

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
        
def resolveQues(cid, aid, qData):
    ans = answers.objects.get(id = aid)
    ans.resolved = True
    ans.save()
    profRate = False
    if ans.user_id != 38:
        ansRatings = userratings.objects.filter(answer_id = ans.id)
        for row in ansRatings:
            rowUser = row.user_id
            rateUser = User.objects.get(id = rowUser)
            if rateUser.status == "Teacher":
                profRate = True  
        rostSize = courseusers.objects.filter(course_id = cid).count()
        weight = (ans.rating / rostSize) * 100
        if weight >= 5 or profRate:
            detokenizer = MosesDetokenizer()
            data_list = nltk.word_tokenize(qData.question)
            data = [word for word in data_list if word not in stopwords.words('english')]
            detokenizer.detokenize(data, return_str=True)
            dbInfo = " ".join(data).lower()
            botanswers.objects.create(answer = ans.answer, rating = 0, category_id = 9, entities = dbInfo, course_id = cid)
            teachLuis(qData.question, 'Other')
            
def newRating(rate, answerID, userID):
    if userratings.objects.filter(user_id = userID, answer_id = answerID).exists():
        newRate = userratings.objects.get(user_id = userID, answer_id = answerID)
        newRate.rating = rate
        newRate.save()
    else:
        userratings.objects.create(user_id = userID, answer_id = answerID, rating = rate)    
    uprateCt = userratings.objects.filter(answer_id = answerID, rating = 1).count()
    downrateCt = userratings.objects.filter(answer_id = answerID, rating = 0).count()
    record = answers.objects.get(id = answerID)
    record.rating = (uprateCt - downrateCt)
    record.save()