from django.utils import timezone
import datetime
from django.db.models import Case, Count
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.generics import (
    DestroyAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.response import Response


from merosiksha.core.mixins import CustomPageNumberPagination
from merosiksha.lms.resources.api.v1.serializers.admin import (
    DocumentSerializer,
    FolderSerializer,
    OnlineClassDetailSerializer,
    OnlineClassSerializer,
    ResourceSerializer,
    AssignmentSerializer,
    AssignmentDetailSerializer,
    StudentAssignmentSerializer
)
from merosiksha.lms.resources.models import Document, Folder, OnlineClass, Resource, Assignment,StudentAssignment,AssignmentFile


class OnlineClassView(viewsets.ModelViewSet):
    queryset = OnlineClass.objects.all().order_by("-created_at")
    serializer_class = OnlineClassSerializer
    serializer_action_classes = {
        "list": OnlineClassDetailSerializer,
    }
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):

        """
        returns a serializer class based on the action
        that has been defined.
        """
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(OnlineClassView, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        subject_id = self.request.query_params.get("subject", None)

        if subject_id is not None:
            self.queryset = OnlineClass.objects.filter(subject=subject_id)
        return super().list(self, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):

        id = kwargs.get("pk")
        data = request.data
        online_class = get_object_or_404(OnlineClass, id=id)
        serializer = self.get_serializer(online_class, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)

    def join_online_class(self,request,*args,**kwargs):

        """
                students join the online class.
                student endpoint later.
         """

        instance = self.get_object()
        student_id = self.request.query_params.get("student")
        instance.students_in_class.add(student_id)
        return Response({
            "message":"You have joined the online class."
        },status=200)



    def destroy(self, request, *args, **kwargs):

        id = self.kwargs.get("pk")
        online_class = get_object_or_404(OnlineClass, id=id)
        online_class.delete()
        return Response(
            {"message": "Online class has been deleted"}, status=status.HTTP_200_OK
        )


class DocumentView(ListCreateAPIView, DestroyAPIView, RetrieveUpdateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    pagination_class = CustomPageNumberPagination


class FolderView(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    pagination_class = CustomPageNumberPagination

    def list(self, request, *args, **kwargs):
        subject_id = self.request.query_params.get("subject", None)
        level_id = self.request.query_params.get("level", None)
        id = kwargs.get("pk")

        if id:
            instance = get_object_or_404(Folder, id=id)
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=200)

        elif level_id is not None:
            if subject_id is not None:
                self.queryset = Folder.objects.filter(
                    level=level_id, subject=subject_id
                )
            else:
                self.queryset = Folder.objects.filter(level=level_id)
        return super().list(self, request, *args, **kwargs)

    def add_remove_files(self, request, *args, **kwargs):
        instance = self.get_object()

        slug = kwargs.get("slug")
        file_list = self.request.data["files"]

        if slug == "add":

            for file in file_list:

                document = get_object_or_404(Document, id=file)
                document.folder = instance
                document.save()

            return Response(
                {
                    "message": "Files have been added to the folder.",
                },
                status=status.HTTP_200_OK,
            )

        else:
            for file in file_list:
                document = get_object_or_404(Document, id=file)
                document.folder = None
                document.save()

            return Response(
                {
                    "message": "Files have been removed from the folder.",
                },
                status=status.HTTP_200_OK,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Folder has been deleted."}, status=200)


class ResourceView(ListCreateAPIView, DestroyAPIView, RetrieveUpdateAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    pagination_class = CustomPageNumberPagination

    def get(self, request, *args, **kwargs):
        subject_id = self.request.query_params.get("subject", None)
        level_id = self.request.query_params.get("level", None)

        if level_id is not None:
            if subject_id is not None:
                self.queryset = Resource.objects.filter(
                    level=level_id, subject=subject_id
                )
            else:
                self.queryset = Resource.objects.filter(level=level_id)
        return super().list(self, request, *args, **kwargs)


class AssignmentView(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    pagination_class = CustomPageNumberPagination

    serializer_action_classes = {
        "list": AssignmentDetailSerializer,
    }


    def get_serializer_class(self):

        """
        returns a serializer class based on the action
        that has been defined.
        """
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(AssignmentView, self).get_serializer_class()


    def list(self, request, *args, **kwargs):

        onlineclass_id = self.request.query_params.get("onlineclass_id", None)

        qs = self.get_queryset().select_related(
            "online_class").prefetch_related(
            "student_assignments").annotate(
            total_students=Count(
                'online_class__students_in_class'),total_submitted=Count(
                'student_assignments'))

        if onlineclass_id is not None:
            qs = qs.filter(online_class=onlineclass_id)

        serializer = self.get_serializer(qs,many=True)
        return Response(serializer.data,status=200)

    def download_file(self):
        pass

    def destroy(self, request, *args, **kwargs):

        """
            triggers django signal to delete the file after instance deletion.
        """
        instance= self.get_object()
        instance.delete()
        return Response({
            "messgae":"Assignment has been deleted."
        })

    def update(self, request, *args, **kwargs):

        instance = self.get_object()
        file = request.FILES.get("file")
        if file:
            instance.file.delete()

        partial = False
        if 'PATCH' in request.method:
            partial = True

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response({
            "message":"assignment has been updated.",
            "updated_data":serializer.data,
        },status=status.HTTP_200_OK)


class StudentAssignmentView(viewsets.ModelViewSet):
    queryset = StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer
    pagination_class = CustomPageNumberPagination

    def create(self, request, *args, **kwargs):
        """
            student assignmnet upload endpoint.
        """

        deadline = Assignment.objects.get(id=request.data["assignment"]).due_date
        dt = datetime.datetime.combine(deadline, datetime.time.max)

        if dt < datetime.datetime.today():
            return Response({"message":"Deadline already crossed."},
                             status=status.HTTP_403_FORBIDDEN)

        assignment_files = request.FILES.getlist("files")

        if assignment_files:
            request.data.pop("files")
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                id = serializer.data["id"]
                assignment_obj = get_object_or_404(StudentAssignment, id=id)

                for file in assignment_files:
                    file_obj = AssignmentFile.objects.create(assignment_file=file)
                    file_obj.student_assignment = assignment_obj

                return Response({"message":"Assignments have been uploaded"},status=200)

        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def check_assignment(self,request,*args,**kwargs):
        #teacher endpoint
        # print(request.data._mutable)


        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if serializer.data['grade'] and instance.status == False:

            instance.status = True
            instance.save(update_fields=("status",))
        return Response(status=200)

    def list(self, request, *args, **kwargs):
        #teacher endpoint

        assignment_id = self.request.query_params.get("assignment_id")
        submit = self.request.query_params.get("submitted",None)

        qs = StudentAssignment.objects.filter(
            assignment=assignment_id).select_related(
            "student")

        self.queryset = qs

        if submit is not None and submit == 'True':
            return super().list(self, request, *args, **kwargs)

        rem_students = []
        for qs in qs.values('student__user__name'):
            rem_students.append(qs)

        return Response(rem_students)

    def all_assignments(self,request,*args,**Kwargs):

        slug = self.kwargs["slug"]
        onlineclass_id = self.request.query_params.get("onlineclass_id", None)

        if slug and slug == 'submitted':

            qs = self.queryset.select_related(
                "assignment","student"
            ).filter(
                student=self.request.user.student).values(
                "assignment__name"
            )
            if onlineclass_id is not None:
                qs = qs
            serializer = self.serializer_class(qs,many=True)
