from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
import json

sampler= StatevectorSampler()

qaoa = QAOA(
    sampler=sampler,
    optimizer=COBYLA(maxiter=200),
    reps=2
)

