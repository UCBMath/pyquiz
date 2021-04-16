from pyquiz.expr import *
from pyquiz.rand import *
from pyquiz import *
import lib.lay_1_1

seed(22)

begin_quiz(
    title="Test Quiz 2",
    description=rf"""
    <p>This is an example quiz.</p>
    """
)

begin_group()
for i in range(10):
    lib.lay_1_1.q1()
end_group()

begin_group()
for i in range(10):
    lib.lay_1_1.q2()
end_group()

begin_group()
for i in range(10):
    lib.lay_1_1.q3()
end_group()

begin_group()
for i in range(10):
    lib.lay_1_1.q4()
end_group()

begin_group(pick_count=3)
lib.lay_1_1.true_false_bank()
end_group()

end_quiz()
