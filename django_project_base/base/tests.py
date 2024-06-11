import swapper

from django.db import connections
from django.test import TestCase
from dynamicforms import serializers
from rest_framework.test import APIRequestFactory

from django_project_base.base.fields import UserRelatedField
from django_project_base.base.filter_to_model import filter_queryset_or_model_to_project

# Note that the tests get created with demo app's models, not the base module's.
Project = swapper.load_model("django_project_base", "Project")
UserProfile = swapper.load_model("django_project_base", "Profile")
ProjectMember = swapper.load_model("django_project_base", "ProjectMember")


class FilterToModelTest(TestCase):
    def setUp(self):
        super().setUp()

        user = UserProfile.objects.create_user("test.user")
        project1 = Project.objects.create(name="project1", slug="project", owner=user)
        for i in range(10):
            u = UserProfile.objects.create_user(f"test.user.{i}")
            ProjectMember.objects.create(project=project1, member=u)

        user = UserProfile.objects.create_user("test1.user")
        project2 = Project.objects.create(name="project2", slug="project2", owner=user)
        for i in range(15):
            u = UserProfile.objects.create_user(f"test1.user.{i}")
            ProjectMember.objects.create(project=project2, member=u)

    def tearDown(self):
        Project.objects.all().delete()
        UserProfile.objects.all().delete()
        super().tearDown()

    def get_query_count(self):
        res = 0
        for c in connections:
            con = connections[c]
            con.force_debug_cursor = True
            res += len(con.queries)
        return res

    def test_project_selection(self):
        # this is basically a test of django-model-utils.InheritanceManager
        count = self.get_query_count()

        q = filter_queryset_or_model_to_project(queryset=None, model=ProjectMember,
                                                project=Project.objects.get(name="project1"))
        self.assertEqual(q.count(), 10)
        q = filter_queryset_or_model_to_project(queryset=ProjectMember.objects, model=None,
                                                project=Project.objects.get(name="project2"))
        self.assertEqual(q.count(), 15)

        # finally test if number of queries performed was as it needs to be
        self.assertEqual(self.get_query_count() - count, 4)

        q = filter_queryset_or_model_to_project(queryset=ProjectMember.objects, model=None, project=None)
        # Should return qs.none() because the selected project can't be determined from non-existing request here
        self.assertEqual(q.count(), 0)

        # finally test if number of queries performed was as it needs to be
        self.assertEqual(self.get_query_count() - count, 4)

    def context(self, project: "Project"):
        request = APIRequestFactory().get("/")
        if project:
            request.selected_project = project
        return {"request": request}

    def serializer(self, context):
        class TestSerializer(serializers.Serializer):
            user = UserRelatedField()

        return TestSerializer(context=context)

    def test_user_related_field_selection(self):
        ser = self.serializer(context=self.context(Project.objects.get(name="project1")))
        field = ser.fields["user"]
        self.assertIsNotNone(field)
        self.assertEqual(field.get_queryset().count(), 10)

        ser = self.serializer(context=self.context(None))
        field = ser.fields["user"]
        self.assertIsNotNone(field)
        self.assertGreaterEqual(field.get_queryset().count(), 25)
