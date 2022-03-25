from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from . import views
from merosiksha.lms.resources.api.v1.views import admin

app_name = "lms.resources"

router = DefaultRouter()
router.register(r"class", admin.OnlineClassView)
router.register(r"folder", admin.FolderView)
router.register(r"assignment", admin.AssignmentView)
router.register(r"studentassignment", admin.StudentAssignmentView)


urlpatterns = [
    path(
        "class/<int:pk>/",
        admin.OnlineClassView.as_view({"delete": "destroy", "patch": "partial_update"}),
    ),

    path(
        "class/<int:pk>/join/",
        admin.OnlineClassView.as_view({"put": "join_online_class"}),
    ),

    path(
        "folder/<int:pk>/<slug:slug>/",
        admin.FolderView.as_view({"put": "add_remove_files"}),
    ),
    path("docs/", admin.DocumentView.as_view()),
    path("resource/", admin.ResourceView.as_view()),

    path(
        "assignment/<int:pk>/",
        admin.AssignmentView.as_view({"delete": "destroy","put": "update", "patch":"update"}),
    ),
    path(
        "studentassignment/<int:pk>/",
        admin.StudentAssignmentView.as_view({"patch": "check_assignment"}),
    ),
    path(
        "studentassignment/<slug:slug>/",
        admin.StudentAssignmentView.as_view({"get": "all_assignments"}),
    ),

]

urlpatterns += [path("", include(router.urls))]
