from apps.SIMS.models import Student, Class, Teacher
from entrance import routes

app_name = "sims"

studentModelDict = {'model': Student}
clsModelDict = {'model': Class}
teacherModelDict = {'model': Teacher}

urlpatterns = [
    # 学生
    routes.indexPageRoute('student', kwargs=studentModelDict, display='学生'),
    routes.editButtonRoute('student', kwargs=studentModelDict),
    routes.detailButtonRoute('student', kwargs=studentModelDict),
    routes.deleteButtonRoute('student', kwargs=studentModelDict),
    routes.addButtonRoute('student', kwargs=studentModelDict),

    # 教师
    routes.indexPageRoute('teacher', kwargs=teacherModelDict, display='教师'),
    routes.editButtonRoute('teacher', kwargs=teacherModelDict),
    routes.detailButtonRoute('teacher', kwargs=teacherModelDict),
    routes.deleteButtonRoute('teacher', kwargs=teacherModelDict),
    routes.addButtonRoute('teacher', kwargs=teacherModelDict),

    # 班级
    routes.indexPageRoute('cls', kwargs=clsModelDict, display='班级'),
    routes.editButtonRoute('cls', kwargs=clsModelDict),
    routes.detailButtonRoute('cls', kwargs=clsModelDict),
    routes.deleteButtonRoute('cls', kwargs=clsModelDict),
    routes.addButtonRoute('cls', kwargs=clsModelDict),
]
