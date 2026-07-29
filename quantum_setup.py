from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeBrisbane
from qiskit.primitives import BackendSamplerV2


sampler = StatevectorSampler()

optimizer = COBYLA(maxiter=200)

qaoa = QAOA(
    sampler=sampler,
    optimizer=optimizer,
    reps=2
)