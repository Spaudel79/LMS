from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from merosiksha.core.models import TimeStampAbstractModel
from merosiksha.study.models import Levels, Subject
from merosiksha.students.models import Student

from .validators import ModifiedFileField


class OnlineClass(TimeStampAbstractModel):

    level = models.ForeignKey(
        Levels, on_delete=models.CASCADE, null=True, related_name="online_class"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        related_name="online_class",
    )

    class_link = models.URLField(max_length=255, blank=True)

    credentials = models.JSONField(null=True, default=dict)

    name = models.CharField(max_length=25, blank=True)

    students_in_class = models.ManyToManyField(Student, related_name="online_class")


    def __str__(self):
        return "Online Class of {} of {} level".format(self.subject, self.subject.level)

    @property
    def class_name(self):
        return "%s%s" % (self.level.name, self.name)

    @property
    def total_students_in_class(self):

        total = self.students_in_class.all().count()
        return total


class Resource(TimeStampAbstractModel):

    level = models.ForeignKey(
        Levels, on_delete=models.CASCADE, null=True, related_name="resources"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        related_name="resources",
    )

    def __str__(self):
        return "Resources of level {} of subject {}".format(self.level, self.subject)

    @property
    def resource_folders(self):
        folder_list = self.folder.all().values_list("name", flat=True)
        return folder_list


class Folder(TimeStampAbstractModel):

    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, null=True, related_name="folder"
    )

    name = models.CharField(max_length=25, blank=True)

    def __str__(self):
        return self.name

    @property
    def folder_notes(self):
        return self.docs.all()

    @property
    def created_date(self):
        return self.created_at.date()

    @property
    def modified_at(self):
        return self.updated_at.date()

    @property
    def folder_size(self):
        total = sum(abc.file_size for abc in self.docs.only("file"))
        return str(total) + "KB"


class Document(TimeStampAbstractModel):

    folder = models.ForeignKey(
        Folder, on_delete=models.SET_NULL, null=True, related_name="docs"
    )

    file = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.file.name

    @property
    def file_name(self):
        return self.file.name

    @property
    def file_size(self):
        if self.file:
            size = self.file.size
            size = int(size / 1024)
            # return str(size)+'KB'
            return size

    @property
    def created_date(self):
        return self.created_at.date()

    @property
    def created_time(self):
        return self.created_at.time()


class Assignment(TimeStampAbstractModel):

    online_class = models.ForeignKey(
        OnlineClass, on_delete=models.SET_NULL, null=True, related_name="class_assignments"
    )

    name = models.CharField(max_length=100, blank=True)

    due_date = models.DateField()
    description = models.TextField(blank=True)

    # file = ModifiedFileField(file_type=['pdf',s'pptx','jpg','png','docs'],
    #                          max_file_size=1048576,
    #                          blank=True, null=True)

    file = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def total_checked_papers(self):
        total = self.student_assignments.all()


@receiver(pre_delete, sender=Assignment)
def remove_file(**kwargs):
    instance = kwargs.get('instance')
    instance.file.delete(save=False)


class StudentAssignment(TimeStampAbstractModel):

    assignment =  models.ForeignKey(
        Assignment,
        on_delete=models.SET_NULL,
        null=True,
        related_name="student_assignments",
    )

    student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True,
        related_name="student_assignments"
    )

    status = models.BooleanField(default=False)
    grade = models.CharField(max_length=2,blank=True)
    feedback = models.TextField(blank=True)


    def __str__(self):
        return "assignment {}, submitted by {}".format(self.assignment,
                                                       self.student)


    def get_status(self):
        return 'checked' if self.status ==True else 'unchecked'

    @property
    def submitted_time(self):
        return self.created_at

    @classmethod
    def checked_papers(cls):
        return cls.objects.filter(status=True)

    @classmethod
    def checked_papers(cls):
        return cls.objects.filter(status=True)


class AssignmentFile(TimeStampAbstractModel):

    student_assignment = models.ForeignKey(
        StudentAssignment, on_delete=models.SET_NULL, null=True, related_name="assignment_files"
    )
    assignment_file = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.file.name

    @property
    def file_name(self):
        return self.file.name

    @property
    def file_size(self):
        if self.file:
            size = self.file.size
            size = int(size / 1024)
            # return str(size)+'KB'
            return size

    @property
    def created_date(self):
        return self.created_at.date()

    @property
    def created_time(self):
        return self.created_at.time()
