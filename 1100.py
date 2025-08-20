import numpy as np
x = []
x.append(2)
for i in range(0,10):
    x_l = x[-1]
    y = x_l-(x_l*x_l*x_l-3*x_l-1)/(3*x_l*x_l-3)
    x.append(y)
x_true = [1.87938524 for i in range(len(x))]
print(x,'\n',x_true)
print(np.array(x)-np.array(x_true))