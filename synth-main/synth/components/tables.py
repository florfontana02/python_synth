import numpy as np

def SineTable(N):
    """Tabla senoidal pura."""
    return np.sin(2 * np.pi * np.arange(N) / N)

def SquareTable(N):
    """Tabla de onda cuadrada (±1)."""
    # Signo de la senoide
    return np.sign(SineTable(N))

def SawtoothTable(N):
    """Tabla de diente de sierra: rampa lineal de -1 a +1."""
    return 2 * (np.arange(N) / N) - 1

def TriangleTable(N):
    """Tabla triangular: rampa ascendente y descendente."""
    ramp = 2 * (np.arange(N) / N)
    tri  = np.where(ramp <= 1, ramp, 2 - ramp)
    return 2 * tri - 1
