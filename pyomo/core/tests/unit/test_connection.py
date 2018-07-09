#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________
#
# Unit Tests for Elements of a Model
#

import pyutilib.th as unittest
from six import StringIO

from pyomo.environ import *
from pyomo.core.base.connection import ConnectionExpander

class TestConnection(unittest.TestCase):

    def test_default_scalar_constructor(self):
        m = ConcreteModel()
        m.c1 = Connection()
        self.assertEqual(len(m.c1), 0)
        self.assertIsNone(m.c1.directed)
        self.assertIsNone(m.c1.connectors)
        self.assertIsNone(m.c1.source)
        self.assertIsNone(m.c1.destination)

        m = AbstractModel()
        m.c1 = Connection()
        self.assertEqual(len(m.c1), 0)
        self.assertIsNone(m.c1.directed)
        self.assertIsNone(m.c1.connectors)
        self.assertIsNone(m.c1.source)
        self.assertIsNone(m.c1.destination)

        inst = m.create_instance()
        self.assertEqual(len(inst.c1), 0)
        self.assertIsNone(inst.c1.directed)
        self.assertIsNone(inst.c1.connectors)
        self.assertIsNone(inst.c1.source)
        self.assertIsNone(inst.c1.destination)

    def test_default_indexed_constructor(self):
        m = ConcreteModel()
        m.c1 = Connection([1, 2, 3])
        self.assertEqual(len(m.c1), 0)
        self.assertIs(m.c1.type(), Connection)

        m = AbstractModel()
        m.c1 = Connection([1, 2, 3])
        self.assertEqual(len(m.c1), 0)
        self.assertIs(m.c1.type(), Connection)


        inst = m.create_instance()
        self.assertEqual(len(m.c1), 0)
        self.assertIs(m.c1.type(), Connection)

    def test_with_scalar_conns(self):
        m = ConcreteModel()
        m.con1 = Connector()
        m.con2 = Connector()
        m.c1 = Connection(source=m.con1, destination=m.con2)
        self.assertEqual(len(m.c1), 1)
        self.assertTrue(m.c1.directed)
        self.assertIs(m.c1.source, m.con1)
        self.assertIs(m.c1.destination, m.con2)
        self.assertIs(m.c1.connectors[0], m.con1)
        self.assertIs(m.c1.connectors[1], m.con2)
        m.c2 = Connection(connectors=(m.con1, m.con2))
        self.assertEqual(len(m.c2), 1)
        self.assertFalse(m.c2.directed)
        self.assertIsInstance(m.c2.connectors, tuple)
        self.assertEqual(len(m.c2.connectors), 2)
        self.assertIs(m.c2.connectors[0], m.con1)
        self.assertIs(m.c2.connectors[1], m.con2)
        self.assertIsNone(m.c2.source)
        self.assertIsNone(m.c2.destination)

        m = AbstractModel()
        m.con1 = Connector()
        m.con2 = Connector()
        m.c1 = Connection(source=m.con1, destination=m.con2)
        self.assertEqual(len(m.c1), 0)
        self.assertIsNone(m.c1.directed)
        self.assertIsNone(m.c1.connectors)
        self.assertIsNone(m.c1.source)
        self.assertIsNone(m.c1.destination)
        m.c2 = Connection(connectors=(m.con1, m.con2))
        self.assertEqual(len(m.c2), 0)
        self.assertIsNone(m.c2.directed)
        self.assertIsNone(m.c2.connectors)
        self.assertIsNone(m.c2.source)
        self.assertIsNone(m.c2.destination)

        inst = m.create_instance()
        self.assertEqual(len(inst.c1), 1)
        self.assertTrue(inst.c1.directed)
        self.assertIs(inst.c1.source, inst.con1)
        self.assertIs(inst.c1.destination, inst.con2)
        self.assertIs(inst.c1.connectors[0], inst.con1)
        self.assertIs(inst.c1.connectors[1], inst.con2)
        self.assertEqual(len(inst.c2), 1)
        self.assertFalse(inst.c2.directed)
        self.assertIsInstance(inst.c2.connectors, tuple)
        self.assertEqual(len(inst.c2.connectors), 2)
        self.assertIs(inst.c2.connectors[0], inst.con1)
        self.assertIs(inst.c2.connectors[1], inst.con2)
        self.assertIsNone(inst.c2.source)
        self.assertIsNone(inst.c2.destination)

    def test_with_indexed_conns(self):
        def rule1(m, i):
            return dict(source=m.con1[i], destination=m.con2[i])
        def rule2(m, i):
            return dict(connectors=(m.con1[i], m.con2[i]))
        def rule3(m, i):
            # should accept any two-member iterable
            return (c for c in (m.con1[i], m.con2[i]))

        m = ConcreteModel()
        m.s = RangeSet(1, 5)
        m.con1 = Connector(m.s)
        m.con2 = Connector(m.s)
        m.c1 = Connection(m.s, rule=rule1)
        self.assertEqual(len(m.c1), 5)
        self.assertTrue(m.c1[4].directed)
        self.assertIs(m.c1[4].source, m.con1[4])
        self.assertIs(m.c1[4].destination, m.con2[4])
        self.assertIs(m.c1[4].connectors[0], m.con1[4])
        self.assertIs(m.c1[4].connectors[1], m.con2[4])
        m.c2 = Connection(m.s, rule=rule2)
        self.assertEqual(len(m.c2), 5)
        self.assertFalse(m.c2[4].directed)
        self.assertIsInstance(m.c2[4].connectors, tuple)
        self.assertEqual(len(m.c2[4].connectors), 2)
        self.assertIs(m.c2[4].connectors[0], m.con1[4])
        self.assertIs(m.c2[4].connectors[1], m.con2[4])
        self.assertIsNone(m.c2[4].source)
        self.assertIsNone(m.c2[4].destination)
        m.c3 = Connection(m.s, rule=rule3, directed=True)
        self.assertEqual(len(m.c3), 5)
        self.assertTrue(m.c3[4].directed)
        self.assertIs(m.c3[4].source, m.con1[4])
        self.assertIs(m.c3[4].destination, m.con2[4])
        self.assertIs(m.c3[4].connectors[0], m.con1[4])
        self.assertIs(m.c3[4].connectors[1], m.con2[4])
        m.c4 = Connection(m.s, rule=rule3)
        self.assertEqual(len(m.c4), 5)
        self.assertFalse(m.c4[4].directed)
        self.assertIsInstance(m.c4[4].connectors, tuple)
        self.assertEqual(len(m.c4[4].connectors), 2)
        self.assertIs(m.c4[4].connectors[0], m.con1[4])
        self.assertIs(m.c4[4].connectors[1], m.con2[4])
        self.assertIsNone(m.c4[4].source)
        self.assertIsNone(m.c4[4].destination)

        m = AbstractModel()
        m.s = RangeSet(1, 5)
        m.con1 = Connector(m.s)
        m.con2 = Connector(m.s)
        m.c1 = Connection(m.s, rule=rule1)
        self.assertEqual(len(m.c1), 0)
        self.assertIs(m.c1.type(), Connection)
        m.c2 = Connection(m.s, rule=rule2)
        self.assertEqual(len(m.c2), 0)
        self.assertIs(m.c1.type(), Connection)

        inst = m.create_instance()
        self.assertEqual(len(inst.c1), 5)
        self.assertTrue(inst.c1[4].directed)
        self.assertIs(inst.c1[4].source, inst.con1[4])
        self.assertIs(inst.c1[4].destination, inst.con2[4])
        self.assertIs(inst.c2[4].connectors[0], inst.con1[4])
        self.assertIs(inst.c2[4].connectors[1], inst.con2[4])
        self.assertEqual(len(inst.c2), 5)
        self.assertFalse(inst.c2[4].directed)
        self.assertIs(inst.c2[4].connectors[0], inst.con1[4])
        self.assertIs(inst.c2[4].connectors[1], inst.con2[4])
        self.assertIsNone(inst.c2[4].source)
        self.assertIsNone(inst.c2[4].destination)

    def test_pprint(self):
        m = ConcreteModel()
        m.s = RangeSet(1, 5)
        m.con1 = Connector(m.s)
        m.con2 = Connector(m.s)

        @m.Connection(m.s)
        def friend(m, i):
            return dict(source=m.con1[i], destination=m.con2[i])

        os = StringIO()
        m.friend.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""friend : Size=5, Index=s, Active=True
    Key : Connectors         : Directed : Active
      1 : (con1[1], con2[1]) :     True :   True
      2 : (con1[2], con2[2]) :     True :   True
      3 : (con1[3], con2[3]) :     True :   True
      4 : (con1[4], con2[4]) :     True :   True
      5 : (con1[5], con2[5]) :     True :   True
""")

        m = ConcreteModel()
        m.z = RangeSet(1, 2)
        m.con1 = Connector(m.z)
        m.con2 = Connector(m.z)

        @m.Connection(m.z)
        def pal(m, i):
            return (m.con1[i], m.con2[i])

        m.pal[2].deactivate()

        os = StringIO()
        m.pal.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""pal : Size=2, Index=z, Active=True
    Key : Connectors         : Directed : Active
      1 : (con1[1], con2[1]) :    False :   True
      2 : (con1[2], con2[2]) :    False :  False
""")


    def test_expand_single_scalar(self):
        m = ConcreteModel()
        m.x = Var()
        m.y = Var()
        m.con1 = Connector()
        m.con1.add(m.x, "v")
        m.con2 = Connector()
        m.con2.add(m.y, "v")

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(source=m.con1, destination=m.con2)
        m.nocon = Constraint(expr = m.x == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 2)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 2)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.active)
        self.assertTrue(blk.component('v_equality').active)

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    1 Constraint Declarations
        v_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body  : Upper : Active
            None :   0.0 : x - y :   0.0 :   True

    1 Declarations: v_equality
""")


    def test_expand_scalar(self):
        m = ConcreteModel()
        m.x = Var()
        m.y = Var()
        m.z = Var()
        m.w = Var()
        m.con1 = Connector()
        m.con1.add(m.x, "a")
        m.con1.add(m.y, "b")
        m.con2 = Connector()
        m.con2.add(m.z, "a")
        m.con2.add(m.w, "b")

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.con1, m.con2))
        m.nocon = Constraint(expr = m.x == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 3)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 3)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.active)
        self.assertTrue(blk.component('a_equality').active)
        self.assertTrue(blk.component('b_equality').active)

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        a_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body  : Upper : Active
            None :   0.0 : x - z :   0.0 :   True
        b_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body  : Upper : Active
            None :   0.0 : y - w :   0.0 :   True

    2 Declarations: a_equality b_equality
""")


    def test_expand_expression(self):
        m = ConcreteModel()
        m.x = Var()
        m.y = Var()
        m.z = Var()
        m.w = Var()
        m.con1 = Connector()
        m.con1.add(-m.x, name='expr1')
        m.con1.add(1 + m.y, name='expr2')
        m.con2 = Connector()
        m.con2.add(-m.z, name='expr1')
        m.con2.add(1 + m.w, name='expr2')

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.con1, m.con2))
        m.nocon = Constraint(expr = m.x == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 3)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 3)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.active)
        self.assertTrue(blk.component('expr1_equality').active)
        self.assertTrue(blk.component('expr2_equality').active)

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        expr1_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body    : Upper : Active
            None :   0.0 : - x + z :   0.0 :   True
        expr2_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body            : Upper : Active
            None :   0.0 : 1 + y - (1 + w) :   0.0 :   True

    2 Declarations: expr1_equality expr2_equality
""")


    def test_expand_indexed(self):
        m = ConcreteModel()
        m.x = Var([1,2])
        m.y = Var([1,2], [1,2])
        m.z = Var()
        m.t = Var([1,2])
        m.u = Var([1,2], [1,2])
        m.v = Var()
        m.con1 = Connector()
        m.con1.add(m.x, "a")
        m.con1.add(m.y, "b")
        m.con1.add(m.z, "c")
        m.con2 = Connector()
        m.con2.add(m.t, "a")
        m.con2.add(m.u, "b")
        m.con2.add(m.v, "c")

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.con1, m.con2))
        m.nocon = Constraint(expr = m.x[1] == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 4)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 8)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.active)
        self.assertTrue(blk.component('a_equality').active)

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    3 Constraint Declarations
        a_equality : Size=2, Index=x_index, Active=True
            Key : Lower : Body        : Upper : Active
              1 :   0.0 : x[1] - t[1] :   0.0 :   True
              2 :   0.0 : x[2] - t[2] :   0.0 :   True
        b_equality : Size=4, Index=y_index, Active=True
            Key    : Lower : Body            : Upper : Active
            (1, 1) :   0.0 : y[1,1] - u[1,1] :   0.0 :   True
            (1, 2) :   0.0 : y[1,2] - u[1,2] :   0.0 :   True
            (2, 1) :   0.0 : y[2,1] - u[2,1] :   0.0 :   True
            (2, 2) :   0.0 : y[2,2] - u[2,2] :   0.0 :   True
        c_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body  : Upper : Active
            None :   0.0 : z - v :   0.0 :   True

    3 Declarations: a_equality b_equality c_equality
""")


    def test_expand_trivial(self):
        m = ConcreteModel()
        m.x = Var()
        m.con = Connector()
        m.con.add(m.x, "a")

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.con, m.con))
        m.nocon = Constraint(expr = m.x == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 2)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 2)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.active)
        self.assertTrue(blk.component('a_equality').active)

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    1 Constraint Declarations
        a_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body  : Upper : Active
            None :   0.0 : x - x :   0.0 :   True

    1 Declarations: a_equality
""")


    def test_expand_empty_scalar(self):
        m = ConcreteModel()
        m.x = Var(bounds=(1,3))
        m.y = Var(domain=Binary)
        m.CON = Connector()
        m.CON.add(m.x)
        m.CON.add(m.y)
        m.ECON = Connector()

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.CON, m.ECON))
        m.nocon = Constraint(expr = m.x == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 3)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 3)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.component('x_equality').active)
        self.assertTrue(blk.component('y_equality').active)

        self.assertIs( m.x.domain, m.component('ECON.auto.x').domain )
        self.assertIs( m.y.domain, m.component('ECON.auto.y').domain )
        self.assertEqual( m.x.bounds, m.component('ECON.auto.x').bounds )
        self.assertEqual( m.y.bounds, m.component('ECON.auto.y').bounds )

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body            : Upper : Active
            None :   0.0 : x - ECON.auto.x :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body            : Upper : Active
            None :   0.0 : y - ECON.auto.y :   0.0 :   True

    2 Declarations: x_equality y_equality
""")


    def test_expand_empty_expression(self):
        m = ConcreteModel()
        m.x = Var()
        m.y = Var()
        m.CON = Connector()
        m.CON.add(-m.x, 'x')
        m.CON.add(1 + m.y, 'y')
        m.ECON = Connector()

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.CON, m.ECON))
        m.nocon = Constraint(expr = m.x == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 3)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 3)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.component('x_equality').active)
        self.assertTrue(blk.component('y_equality').active)

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body              : Upper : Active
            None :   0.0 : - x - ECON.auto.x :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                : Upper : Active
            None :   0.0 : 1 + y - ECON.auto.y :   0.0 :   True

    2 Declarations: x_equality y_equality
""")


    def test_expand_empty_indexed(self):
        m = ConcreteModel()
        m.x = Var([1,2], domain=Binary)
        m.y = Var(bounds=(1,3))
        m.CON = Connector()
        m.CON.add(m.x)
        m.CON.add(m.y)
        m.ECON = Connector()

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.CON, m.ECON))
        m.nocon = Constraint(expr = m.x[1] == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 3)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 4)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.component('x_equality').active)
        self.assertTrue(blk.component('y_equality').active)

        self.assertIs( m.x[1].domain, m.component('ECON.auto.x')[1].domain )
        self.assertIs( m.x[2].domain, m.component('ECON.auto.x')[2].domain )
        self.assertIs( m.y.domain, m.component('ECON.auto.y').domain )
        self.assertEqual( m.x[1].bounds, m.component('ECON.auto.x')[1].bounds )
        self.assertEqual( m.x[2].bounds, m.component('ECON.auto.x')[2].bounds )
        self.assertEqual( m.y.bounds, m.component('ECON.auto.y').bounds )

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=2, Index=x_index, Active=True
            Key : Lower : Body                  : Upper : Active
              1 :   0.0 : x[1] - ECON.auto.x[1] :   0.0 :   True
              2 :   0.0 : x[2] - ECON.auto.x[2] :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body            : Upper : Active
            None :   0.0 : y - ECON.auto.y :   0.0 :   True

    2 Declarations: x_equality y_equality
""")


    def test_expand_multiple_empty_indexed(self):
        m = ConcreteModel()
        m.x = Var([1,2], domain=Binary)
        m.y = Var(bounds=(1,3))
        m.CON = Connector()
        m.CON.add(m.x)
        m.CON.add(m.y)
        m.ECON2 = Connector()
        m.ECON1 = Connector()

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        # Define d first to test that it knows how to expand the ECONs
        m.d = Connection(connectors=(m.ECON2, m.ECON1))
        m.c = Connection(connectors=(m.CON, m.ECON1))
        m.nocon = Constraint(expr = m.x[1] == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 5)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 7)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk_c = m.component('c_expanded')
        self.assertTrue(blk_c.component('x_equality').active)
        self.assertTrue(blk_c.component('y_equality').active)
        self.assertFalse(m.d.active)
        blk_d = m.component('d_expanded')
        self.assertTrue(blk_d.component('x_equality').active)
        self.assertTrue(blk_d.component('y_equality').active)

        self.assertIs( m.x[1].domain, m.component('ECON1.auto.x')[1].domain )
        self.assertIs( m.x[2].domain, m.component('ECON1.auto.x')[2].domain )
        self.assertIs( m.y.domain, m.component('ECON1.auto.y').domain )
        self.assertEqual( m.x[1].bounds, m.component('ECON1.auto.x')[1].bounds )
        self.assertEqual( m.x[2].bounds, m.component('ECON1.auto.x')[2].bounds )
        self.assertEqual( m.y.bounds, m.component('ECON1.auto.y').bounds )

        self.assertIs( m.x[1].domain, m.component('ECON2.auto.x')[1].domain )
        self.assertIs( m.x[2].domain, m.component('ECON2.auto.x')[2].domain )
        self.assertIs( m.y.domain, m.component('ECON2.auto.y').domain )
        self.assertEqual( m.x[1].bounds, m.component('ECON2.auto.x')[1].bounds )
        self.assertEqual( m.x[2].bounds, m.component('ECON2.auto.x')[2].bounds )
        self.assertEqual( m.y.bounds, m.component('ECON2.auto.y').bounds )

        os = StringIO()
        blk_c.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=2, Index=x_index, Active=True
            Key : Lower : Body                   : Upper : Active
              1 :   0.0 : x[1] - ECON1.auto.x[1] :   0.0 :   True
              2 :   0.0 : x[2] - ECON1.auto.x[2] :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body             : Upper : Active
            None :   0.0 : y - ECON1.auto.y :   0.0 :   True

    2 Declarations: x_equality y_equality
""")

        os = StringIO()
        blk_d.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""d_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=2, Index=x_index, Active=True
            Key : Lower : Body                              : Upper : Active
              1 :   0.0 : ECON2.auto.x[1] - ECON1.auto.x[1] :   0.0 :   True
              2 :   0.0 : ECON2.auto.x[2] - ECON1.auto.x[2] :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                        : Upper : Active
            None :   0.0 : ECON2.auto.y - ECON1.auto.y :   0.0 :   True

    2 Declarations: x_equality y_equality
""")


    def test_expand_multiple_indexed(self):
        m = ConcreteModel()
        m.x = Var([1,2], domain=Binary)
        m.y = Var(bounds=(1,3))
        m.CON = Connector()
        m.CON.add(m.x)
        m.CON.add(m.y)
        m.a1 = Var([1,2])
        m.a2 = Var([1,2])
        m.b1 = Var()
        m.b2 = Var()
        m.ECON2 = Connector()
        m.ECON2.add(m.a1,'x')
        m.ECON2.add(m.b1,'y')
        m.ECON1 = Connector()
        m.ECON1.add(m.a2,'x')
        m.ECON1.add(m.b2,'y')

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.CON, m.ECON1))
        m.d = Connection(connectors=(m.ECON2, m.ECON1))
        m.nocon = Constraint(expr = m.x[1] == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 5)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 7)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk_c = m.component('c_expanded')
        self.assertTrue(blk_c.component('x_equality').active)
        self.assertTrue(blk_c.component('y_equality').active)
        self.assertFalse(m.d.active)
        blk_d = m.component('d_expanded')
        self.assertTrue(blk_d.component('x_equality').active)
        self.assertTrue(blk_d.component('y_equality').active)

        os = StringIO()
        blk_c.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=2, Index=x_index, Active=True
            Key : Lower : Body         : Upper : Active
              1 :   0.0 : x[1] - a2[1] :   0.0 :   True
              2 :   0.0 : x[2] - a2[2] :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body   : Upper : Active
            None :   0.0 : y - b2 :   0.0 :   True

    2 Declarations: x_equality y_equality
""")

        os = StringIO()
        blk_d.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""d_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=2, Index=x_index, Active=True
            Key : Lower : Body          : Upper : Active
              1 :   0.0 : a1[1] - a2[1] :   0.0 :   True
              2 :   0.0 : a1[2] - a2[2] :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body    : Upper : Active
            None :   0.0 : b1 - b2 :   0.0 :   True

    2 Declarations: x_equality y_equality
""")


    def test_expand_implicit_indexed(self):
        m = ConcreteModel()
        m.x = Var([1,2], domain=Binary)
        m.y = Var(bounds=(1,3))
        m.CON = Connector()
        m.CON.add(m.x)
        m.CON.add(m.y)
        m.a2 = Var([1,2])
        m.b1 = Var()
        m.ECON2 = Connector(implicit=['x'])
        m.ECON2.add(m.b1,'y')
        m.ECON1 = Connector(implicit=['y'])
        m.ECON1.add(m.a2,'x')

        # The connection should be deactivated and expanded,
        # the constraint should be left untouched.
        m.c = Connection(connectors=(m.CON, m.ECON1))
        m.d = Connection(connectors=(m.ECON2, m.CON))
        m.nocon = Constraint(expr = m.x[1] == 2)

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        os = StringIO()
        m.ECON1.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""ECON1 : Size=1, Index=None
    Key  : Name : Size : Variable
    None :    x :    2 :       a2
         :    y :    - :     None
""")

        TransformationFactory('core.expand_connections').apply_to(m)

        os = StringIO()
        m.ECON1.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""ECON1 : Size=1, Index=None
    Key  : Name : Size : Variable
    None :    x :    2 :           a2
         :    y :    1 : ECON1.auto.y
""")

        self.assertEqual(len(list(m.component_objects(Constraint))), 5)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 7)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.c.active)
        blk_c = m.component('c_expanded')
        self.assertTrue(blk_c.component('x_equality').active)
        self.assertTrue(blk_c.component('y_equality').active)
        self.assertFalse(m.d.active)
        blk_d = m.component('d_expanded')
        self.assertTrue(blk_d.component('x_equality').active)
        self.assertTrue(blk_d.component('y_equality').active)

        os = StringIO()
        blk_c.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=2, Index=x_index, Active=True
            Key : Lower : Body         : Upper : Active
              1 :   0.0 : x[1] - a2[1] :   0.0 :   True
              2 :   0.0 : x[2] - a2[2] :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body             : Upper : Active
            None :   0.0 : y - ECON1.auto.y :   0.0 :   True

    2 Declarations: x_equality y_equality
""")

        os = StringIO()
        blk_d.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""d_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        x_equality : Size=2, Index=x_index, Active=True
            Key : Lower : Body                   : Upper : Active
              1 :   0.0 : ECON2.auto.x[1] - x[1] :   0.0 :   True
              2 :   0.0 : ECON2.auto.x[2] - x[2] :   0.0 :   True
        y_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body   : Upper : Active
            None :   0.0 : b1 - y :   0.0 :   True

    2 Declarations: x_equality y_equality
""")


    def test_varlist_aggregator(self):
        m = ConcreteModel()
        m.flow = VarList()
        m.phase = Var(bounds=(1,3))
        m.CON = Connector()
        m.CON.add( m.flow,
                   aggregate=lambda m,v: sum(v[i] for i in v) == 0 )
        m.CON.add(m.phase)
        m.ECON2 = Connector()
        m.ECON1 = Connector()

        m.c = Connection(connectors=(m.CON, m.ECON1))
        m.d = Connection(connectors=(m.ECON2, m.CON))

        self.assertEqual(len(list(m.component_objects(Constraint))), 0)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 0)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 5)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 5)
        self.assertFalse(m.c.active)
        blk_c = m.component('c_expanded')
        self.assertTrue(blk_c.component('flow_equality').active)
        self.assertTrue(blk_c.component('phase_equality').active)
        self.assertFalse(m.d.active)
        blk_d = m.component('d_expanded')
        self.assertTrue(blk_d.component('flow_equality').active)
        self.assertTrue(blk_d.component('phase_equality').active)

        self.assertEqual( len(m.flow), 2 )

        os = StringIO()
        blk_c.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        flow_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                      : Upper : Active
            None :   0.0 : ECON1.auto.flow - flow[1] :   0.0 :   True
        phase_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                     : Upper : Active
            None :   0.0 : phase - ECON1.auto.phase :   0.0 :   True

    2 Declarations: flow_equality phase_equality
""")

        os = StringIO()
        blk_d.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""d_expanded : Size=1, Index=None, Active=True
    2 Constraint Declarations
        flow_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                      : Upper : Active
            None :   0.0 : ECON2.auto.flow - flow[2] :   0.0 :   True
        phase_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                     : Upper : Active
            None :   0.0 : ECON2.auto.phase - phase :   0.0 :   True

    2 Declarations: flow_equality phase_equality
""")

        os = StringIO()
        m.component('CON.flow.aggregate').pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""CON.flow.aggregate : Size=1, Index=None, Active=True
    Key  : Lower : Body              : Upper : Active
    None :   0.0 : flow[1] + flow[2] :   0.0 :   True
""")

        os = StringIO()
        m.CON.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""CON : Size=1, Index=None
    Key  : Name  : Size : Variable
    None :  flow :    * :     flow
         : phase :    1 :    phase
""")


    def test_extensive_aggregator_scalar(self):
        m = ConcreteModel()
        m.comp = Set(initialize=["a", "b", "c"])
        Feed = Tru = Prod = Block

        # Feed
        m.feed = Feed()
        m.feed.mass = Var()
        m.feed.temp = Var()

        m.feed.outlet = Connector()
        m.feed.outlet.add(m.feed.mass, "mass", extensive="split")
        m.feed.outlet.add(m.feed.temp, "temp")

        # Treatment Unit
        m.tru = Tru()
        m.tru.mass = Var()
        m.tru.temp = Var()

        m.tru.inlet = Connector()
        m.tru.inlet.add(m.tru.mass, "mass", extensive="mix")
        m.tru.inlet.add(m.tru.temp, "temp")

        m.tru.outlet = Connector()
        m.tru.outlet.add(m.tru.mass, "mass", extensive="split")
        m.tru.outlet.add(m.tru.temp, "temp")

        # Product
        m.prod = Prod()
        m.prod.mass = Var()
        m.prod.temp = Var()

        m.prod.inlet = Connector()
        m.prod.inlet.add(m.prod.mass, "mass", extensive="mix")
        m.prod.inlet.add(m.prod.temp, "temp")

        # SplitFrac specifications (optional)
        m.feed.splitfrac = dict()
        m.feed.splitfrac["stream1"] = .6 # fix by default
        m.tru.splitfrac = dict()
        m.tru.splitfrac["stream3"] = dict(val=1, fix=False) # just initialize

        # Connections
        m.stream1 = Connection(source=m.feed.outlet, destination=m.tru.inlet)
        m.stream2 = Connection(source=m.feed.outlet, destination=m.prod.inlet)
        m.stream3 = Connection(source=m.tru.outlet, destination=m.prod.inlet)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertFalse(m.stream1.active)
        self.assertFalse(m.stream2.active)
        self.assertFalse(m.stream3.active)

        self.assertEqual(m.feed.outlet_frac_sum.expr.to_string(),
            "stream1_expanded.splitfrac + stream2_expanded.splitfrac  ==  1.0")

        self.assertEqual(m.tru.outlet_frac_sum.expr.to_string(),
            "stream3_expanded.splitfrac  ==  1.0")

        self.assertEqual(m.prod.inlet_mass_bal.expr.to_string(),
            "stream2_expanded.mass + stream3_expanded.mass - prod.mass  ==  0.0")

        self.assertEqual(m.tru.inlet_mass_bal.expr.to_string(),
            "stream1_expanded.mass - tru.mass  ==  0.0")

        os = StringIO()
        m.stream1_expanded.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""stream1_expanded : Size=1, Index=None, Active=True
    2 Var Declarations
        mass : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :  None :  None : False :  True :  Reals
        splitfrac : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :   0.6 :  None :  True : False :  Reals

    2 Constraint Declarations
        mass_split : Size=1, Index=None, Active=True
            Key  : Lower : Body                                                         : Upper : Active
            None :   0.0 : stream1_expanded.mass - stream1_expanded.splitfrac*feed.mass :   0.0 :   True
        temp_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                 : Upper : Active
            None :   0.0 : feed.temp - tru.temp :   0.0 :   True

    4 Declarations: mass temp_equality splitfrac mass_split
""")

        os = StringIO()
        m.stream2_expanded.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""stream2_expanded : Size=1, Index=None, Active=True
    2 Var Declarations
        mass : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :  None :  None : False :  True :  Reals
        splitfrac : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :  None :  None : False :  True :  Reals

    2 Constraint Declarations
        mass_split : Size=1, Index=None, Active=True
            Key  : Lower : Body                                                         : Upper : Active
            None :   0.0 : stream2_expanded.mass - stream2_expanded.splitfrac*feed.mass :   0.0 :   True
        temp_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                  : Upper : Active
            None :   0.0 : feed.temp - prod.temp :   0.0 :   True

    4 Declarations: mass temp_equality splitfrac mass_split
""")

        os = StringIO()
        m.stream3_expanded.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""stream3_expanded : Size=1, Index=None, Active=True
    2 Var Declarations
        mass : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :  None :  None : False :  True :  Reals
        splitfrac : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :     1 :  None : False : False :  Reals

    2 Constraint Declarations
        mass_split : Size=1, Index=None, Active=True
            Key  : Lower : Body                                                        : Upper : Active
            None :   0.0 : stream3_expanded.mass - stream3_expanded.splitfrac*tru.mass :   0.0 :   True
        temp_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                 : Upper : Active
            None :   0.0 : tru.temp - prod.temp :   0.0 :   True

    4 Declarations: mass temp_equality splitfrac mass_split
""")


    def test_extensive_aggregator_indexed(self):
        m = ConcreteModel()
        m.comp = Set(initialize=["a", "b", "c"])
        Feed = Tru = Prod = Block

        # Feed
        m.feed = Feed()
        m.feed.flow = Var(m.comp)
        m.feed.temp = Var()

        m.feed.outlet = Connector()
        m.feed.outlet.add(m.feed.flow, "flow", extensive="split")
        m.feed.outlet.add(m.feed.temp, "temp")

        # Treatment Unit
        m.tru = Tru()
        m.tru.flow_in = Var(m.comp)
        m.tru.flow_out = Var(m.comp)
        m.tru.temp = Var()

        m.tru.inlet = Connector()
        m.tru.inlet.add(m.tru.flow_in, "flow", extensive="mix")
        m.tru.inlet.add(m.tru.temp, "temp")

        m.tru.outlet = Connector()
        m.tru.outlet.add(m.tru.flow_out, "flow", extensive="split")
        m.tru.outlet.add(m.tru.temp, "temp")

        # Product
        m.prod = Prod()
        m.prod.flow = Var(m.comp)
        m.prod.temp = Var()

        m.prod.inlet = Connector()
        m.prod.inlet.add(m.prod.flow, "flow", extensive="mix")
        m.prod.inlet.add(m.prod.temp, "temp")

        # SplitFrac specifications (optional)
        m.feed.splitfrac = dict()
        m.feed.splitfrac["stream1"] = .6 # fix by default
        m.tru.splitfrac = dict()
        m.tru.splitfrac["stream3"] = dict(val=1, fix=False) # just initialize

        # Connections
        m.stream1 = Connection(source=m.feed.outlet, destination=m.tru.inlet)
        m.stream2 = Connection(source=m.feed.outlet, destination=m.prod.inlet)
        m.stream3 = Connection(source=m.tru.outlet, destination=m.prod.inlet)

        TransformationFactory('core.expand_connections').apply_to(m)

        self.assertFalse(m.stream1.active)
        self.assertFalse(m.stream2.active)
        self.assertFalse(m.stream3.active)

        self.assertEqual(m.feed.outlet_frac_sum.expr.to_string(),
            "stream1_expanded.splitfrac + stream2_expanded.splitfrac  ==  1.0")

        self.assertEqual(m.tru.outlet_frac_sum.expr.to_string(),
            "stream3_expanded.splitfrac  ==  1.0")

        os = StringIO()
        m.prod.inlet_flow_bal.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""inlet_flow_bal : Size=3, Index=comp, Active=True
    Key : Lower : Body                                                               : Upper : Active
      a :   0.0 : stream2_expanded.flow[a] + stream3_expanded.flow[a] - prod.flow[a] :   0.0 :   True
      b :   0.0 : stream2_expanded.flow[b] + stream3_expanded.flow[b] - prod.flow[b] :   0.0 :   True
      c :   0.0 : stream2_expanded.flow[c] + stream3_expanded.flow[c] - prod.flow[c] :   0.0 :   True
""")

        os = StringIO()
        m.tru.inlet_flow_bal.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""inlet_flow_bal : Size=3, Index=comp, Active=True
    Key : Lower : Body                                      : Upper : Active
      a :   0.0 : stream1_expanded.flow[a] - tru.flow_in[a] :   0.0 :   True
      b :   0.0 : stream1_expanded.flow[b] - tru.flow_in[b] :   0.0 :   True
      c :   0.0 : stream1_expanded.flow[c] - tru.flow_in[c] :   0.0 :   True
""")

        os = StringIO()
        m.stream1_expanded.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""stream1_expanded : Size=1, Index=None, Active=True
    2 Var Declarations
        flow : Size=3, Index=comp
            Key : Lower : Value : Upper : Fixed : Stale : Domain
              a :  None :  None :  None : False :  True :  Reals
              b :  None :  None :  None : False :  True :  Reals
              c :  None :  None :  None : False :  True :  Reals
        splitfrac : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :   0.6 :  None :  True : False :  Reals

    2 Constraint Declarations
        flow_split : Size=3, Index=comp, Active=True
            Key : Lower : Body                                                               : Upper : Active
              a :   0.0 : stream1_expanded.flow[a] - stream1_expanded.splitfrac*feed.flow[a] :   0.0 :   True
              b :   0.0 : stream1_expanded.flow[b] - stream1_expanded.splitfrac*feed.flow[b] :   0.0 :   True
              c :   0.0 : stream1_expanded.flow[c] - stream1_expanded.splitfrac*feed.flow[c] :   0.0 :   True
        temp_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                 : Upper : Active
            None :   0.0 : feed.temp - tru.temp :   0.0 :   True

    4 Declarations: flow temp_equality splitfrac flow_split
""")

        os = StringIO()
        m.stream2_expanded.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""stream2_expanded : Size=1, Index=None, Active=True
    2 Var Declarations
        flow : Size=3, Index=comp
            Key : Lower : Value : Upper : Fixed : Stale : Domain
              a :  None :  None :  None : False :  True :  Reals
              b :  None :  None :  None : False :  True :  Reals
              c :  None :  None :  None : False :  True :  Reals
        splitfrac : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :  None :  None : False :  True :  Reals

    2 Constraint Declarations
        flow_split : Size=3, Index=comp, Active=True
            Key : Lower : Body                                                               : Upper : Active
              a :   0.0 : stream2_expanded.flow[a] - stream2_expanded.splitfrac*feed.flow[a] :   0.0 :   True
              b :   0.0 : stream2_expanded.flow[b] - stream2_expanded.splitfrac*feed.flow[b] :   0.0 :   True
              c :   0.0 : stream2_expanded.flow[c] - stream2_expanded.splitfrac*feed.flow[c] :   0.0 :   True
        temp_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                  : Upper : Active
            None :   0.0 : feed.temp - prod.temp :   0.0 :   True

    4 Declarations: flow temp_equality splitfrac flow_split
""")

        os = StringIO()
        m.stream3_expanded.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""stream3_expanded : Size=1, Index=None, Active=True
    2 Var Declarations
        flow : Size=3, Index=comp
            Key : Lower : Value : Upper : Fixed : Stale : Domain
              a :  None :  None :  None : False :  True :  Reals
              b :  None :  None :  None : False :  True :  Reals
              c :  None :  None :  None : False :  True :  Reals
        splitfrac : Size=1, Index=None
            Key  : Lower : Value : Upper : Fixed : Stale : Domain
            None :  None :     1 :  None : False : False :  Reals

    2 Constraint Declarations
        flow_split : Size=3, Index=comp, Active=True
            Key : Lower : Body                                                                  : Upper : Active
              a :   0.0 : stream3_expanded.flow[a] - stream3_expanded.splitfrac*tru.flow_out[a] :   0.0 :   True
              b :   0.0 : stream3_expanded.flow[b] - stream3_expanded.splitfrac*tru.flow_out[b] :   0.0 :   True
              c :   0.0 : stream3_expanded.flow[c] - stream3_expanded.splitfrac*tru.flow_out[c] :   0.0 :   True
        temp_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body                 : Upper : Active
            None :   0.0 : tru.temp - prod.temp :   0.0 :   True

    4 Declarations: flow temp_equality splitfrac flow_split
""")


    def test_expand_indexed_connection(self):
        def rule(m, i):
            return (m.c1[i], m.c2[i])

        m = ConcreteModel()
        m.x = Var(initialize=1, domain=Reals)
        m.y = Var(initialize=2, domain=Reals)
        m.c1 = Connector([1, 2])
        m.c1[1].add(m.x, name='v')
        m.c1[2].add(m.y, name='t')
        m.z = Var(initialize=1, domain=Reals)
        m.w = Var(initialize=2, domain=Reals)
        m.c2 = Connector([1, 2])
        m.c2[1].add(m.z, name='v')
        m.c2[2].add(m.w, name='t')

        m.eq = Connection([1, 2], rule=rule)

        TransformationFactory('core.expand_connections').apply_to(m)

        os = StringIO()
        m.component('eq_expanded').pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""eq_expanded : Size=2, Index=eq_index, Active=True
    eq_expanded[1] : Active=True
        1 Constraint Declarations
            v_equality : Size=1, Index=None, Active=True
                Key  : Lower : Body  : Upper : Active
                None :   0.0 : x - z :   0.0 :   True

        1 Declarations: v_equality
    eq_expanded[2] : Active=True
        1 Constraint Declarations
            t_equality : Size=1, Index=None, Active=True
                Key  : Lower : Body  : Upper : Active
                None :   0.0 : y - w :   0.0 :   True

        1 Declarations: t_equality
""")


    def test_connectionexpander(self):
        m = ConcreteModel()
        m.x = Var()
        m.y = Var()
        m.z = Var()
        m.con1 = Connector()
        m.con1.add(m.x, "v")
        m.con2 = Connector()
        m.con2.add(m.y, "v")
        m.con3 = Connector()
        m.con3.add(m.z, "v")

        # The active connection should be deactivated and expanded, but this
        # transform should not expand constraints with connectors, only
        # connections, and it should not expand inactive Connections.
        m.c = Connection(source=m.con1, destination=m.con2)
        m.inactive = Connection(connectors=(m.con3, m.con2))
        m.nocon = Constraint(expr = m.con1 >= 2)
        m.inactive.deactivate()

        self.assertEqual(len(list(m.component_objects(Constraint))), 1)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 1)

        ConnectionExpander().apply(instance=m)

        self.assertEqual(len(list(m.component_objects(Constraint))), 2)
        self.assertEqual(len(list(m.component_data_objects(Constraint))), 2)
        self.assertTrue(m.nocon.active)
        self.assertFalse(m.inactive.active)
        self.assertIsNone(m.component('inactive_expanded'))
        self.assertFalse(m.c.active)
        blk = m.component('c_expanded')
        self.assertTrue(blk.active)
        self.assertTrue(blk.component('v_equality').active)

        os = StringIO()
        blk.pprint(ostream=os)
        self.assertEqual(os.getvalue(),
"""c_expanded : Size=1, Index=None, Active=True
    1 Constraint Declarations
        v_equality : Size=1, Index=None, Active=True
            Key  : Lower : Body  : Upper : Active
            None :   0.0 : x - y :   0.0 :   True

    1 Declarations: v_equality
""")


if __name__ == "__main__":
    unittest.main()
