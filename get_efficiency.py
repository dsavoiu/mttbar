import sys
import pickle
import hist

with open(sys.argv[1], "rb") as f:
    h = pickle.load(f)

h1d = h[{"category":hist.loc(0), "process":0, "shift":0}]
h1d_lt30 = h1d[:hist.loc(30)]
numerator = h1d_lt30.sum().value
denominator = h1d_lt30.sum(flow=True).value
efficiency = numerator/denominator
print(efficiency)
