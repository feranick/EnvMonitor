sudo apt install cython
python3 setup.py build_ext --inplace

(only the generated .so file is needed for execution)

To use:

import libEnvMonitorC

libEnvMonitorC.absHumidity...
