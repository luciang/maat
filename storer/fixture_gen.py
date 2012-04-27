from datetime import datetime
from fixture_generator import fixture_generator

from django.contrib.auth.models import User, Group
from storer.models import Assignment, Misc, UploadActiveInterval, TesterVM

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


@fixture_generator(TesterVM)
def test_testervm():
    TesterVM.objects.create(host='localhost', vm_name="algo-linux")


#@fixture_generator(Assignment)

@fixture_generator(Assignment, requires=["storer.test_testervm"])
def test_assignment():
    tvm = TesterVM.objects.order_by("vm_name")[0]
    ass = Assignment.objects.create(order_number=1,
                                    name='backtracking-ass',
                                    deadline=datetime.now(),
                                    tests='/tmp/',
                                    penalty="[(10,1)]")
    ass.test_vms.add(tvm)


@fixture_generator(requires=["storer.test_users",
                             "storer.test_assignment"])
def test_all():
    # collects all fixture generators
    pass
