from rest_framework import serializers

from merosiksha.lms.resources.models import Document, Folder, OnlineClass, Resource,Assignment,StudentAssignment


class OnlineClassSerializer(serializers.ModelSerializer):

    class_name = serializers.ReadOnlyField()

    class Meta:
        model = OnlineClass
        fields = [
            "id",
            "class_name",
            "level",
            "subject",
            "class_link",
            "credentials",
            "name",
        ]


class OnlineClassDetailSerializer(serializers.ModelSerializer):

    subject = serializers.StringRelatedField()

    class Meta:
        model = OnlineClass
        fields = ["id", "class_name", "subject", "class_link", "credentials",'students_in_class']


class DocumentSerializer(serializers.ModelSerializer):

    file_name = serializers.ReadOnlyField()
    file_size = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = [
            "id",
            "folder",
            "file",
            "file_name",
            "file_size",
            "created_date",
            "created_time",
        ]

    def create(self, validated_data):

        filename = str(validated_data.get("file"))
        self.validate_filename(filename)
        size = validated_data["file"].size
        if int(size / 1048576) > 100:
            raise serializers.ValidationError("Max file size is 100 MB.")
        doc = super(DocumentSerializer, self).create(validated_data)
        return doc

    def validate_filename(self, filename):

        ext = filename.split(".")[1]
        if ext.lower() not in ["pdf", "pptx", "jpg", "png", "docs"]:
            raise serializers.ValidationError(
                "{} is an invalid file type. "
                "Available file types are 'pdf','pptx','jpg','png','docs'.".format(ext)
            )
        pass

    # def validate(self, attrs):
    #     ext = TemporaryUploadedFile.temporary_file_path(self)
    #     print(ext)
    #     breakpoint()


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["id", "resource", "name", "folder_size", "modified_at"]


class ResourceFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["name"]


class ResourceSerializer(serializers.ModelSerializer):

    # resources_folders = serializers.SerializerMethodField('get_all_folders')

    class Meta:
        model = Resource
        fields = ["id", "level", "subject", "resource_folders"]

    def get_all_folders(self, obj):

        qs = obj.folder.all()
        details = ResourceFolderSerializer(qs, many=True, read_only=True)
        return details.data

class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = ['id','online_class','name','due_date','description','file']


    def create(self, validated_data):

        filename = str(validated_data.get("file"))
        self.validate_filename(filename)
        size = validated_data["file"].size
        if int(size / 1048576) > 100:
            raise serializers.ValidationError("Max file size is 20 MB.")
        assignment = super(AssignmentSerializer, self).create(validated_data)
        return assignment

    def validate_filename(self, filename):

        ext = filename.split(".")[1]
        if ext.lower() not in ["pdf", "pptx", "jpg", "png", "docs"]:
            raise serializers.ValidationError(
                "{} is an invalid file type. "
                "Available file types are 'pdf','pptx','jpg','png','docs'.".format(ext)
            )
        pass


class AssignmentDetailSerializer(serializers.ModelSerializer):

    total_students = serializers.ReadOnlyField()
    total_submitted = serializers.ReadOnlyField()

    class Meta:
        model = Assignment
        fields = ['id','online_class','name','created_at','due_date',
                  'total_students','total_submitted','file']


class StudentAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentAssignment
        fields = ['id', 'assignment', 'student','grade','get_status','feedback','submitted_time' ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['student_name'] = instance.student.user.name

        return representation
