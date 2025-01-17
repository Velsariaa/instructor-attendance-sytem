from django.contrib import admin # type: ignore
from .models import Attendance, Employee,OrgChartList,TimeRecord,Post,DailyTimeRecords,Schedule,SuperUser,History,Comlab,Availability,UserData,UserProfile,Equipment,PositionDCS
from .models import Instructor, Ins_Schedule


admin.site.register(Attendance)
admin.site.register(Employee)
admin.site.register(OrgChartList)
admin.site.register(TimeRecord)
admin.site.register(Post)
admin.site.register(DailyTimeRecords)
admin.site.register(Schedule)
admin.site.register(SuperUser)
admin.site.register(History)
admin.site.register(Comlab)
admin.site.register(Availability)
admin.site.register(UserData)
admin.site.register(UserProfile)
admin.site.register(Equipment)
admin.site.register(PositionDCS)
admin.site.register(Instructor)
admin.site.register(Ins_Schedule)