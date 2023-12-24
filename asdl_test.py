import ir
ir.generate_asdl_file()
import _asdl.loma as loma_ir

c = loma_ir.Const(5.0, 'haha')
print(c)
d = loma_ir.Const(6.0, 'hehe')
print(d)
print(c)
print(loma_ir.Const(7.0))