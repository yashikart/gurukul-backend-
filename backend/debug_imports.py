
try:
    import numpy
    print(f"Numpy version: {numpy.__version__}")
except ImportError as e:
    print(f"Numpy import failed: {e}")
except Exception as e:
    print(f"Numpy error: {e}")

try:
    import torch
    print(f"Torch version: {torch.__version__}")
except ImportError as e:
    print(f"Torch import failed: {e}")
except Exception as e:
    print(f"Torch error: {e}")
