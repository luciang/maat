from fixture_generator import fixture_generator

from django.contrib.auth.models import User, Group

#@fixture_generator(User, requires=["my_app.test_groups"])
@fixture_generator(User)
def test_users():
    paswd = "pass"
    # create one Super user
    su = User.objects.create(username="super", password=paswd,
                             is_staff=True, is_superuser=True)
    # create one Teacher
    ta = User.objects.create(username="ta", password=paswd, is_staff=True)
    # create one Student
    sa = User.objects.create(username="sa", password=paswd, is_staff=False)
