from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeBrisbane
from qiskit.primitives import BackendSamplerV2
import json

energy_history = []

def callback(eval_count, parameters, mean, metadata):
    energy_history.append(float(mean))

sampler = StatevectorSampler()

optimizer = COBYLA(maxiter=200)

qaoa = QAOA(
    sampler=sampler,
    optimizer=optimizer,
    reps=2,
    callback=callback
)

quantum_energy={
    "energy_history":energy_history
}

with open("qaoa_energy.json","w") as f:
    json.dump(quantum_energy,f,indent=4)