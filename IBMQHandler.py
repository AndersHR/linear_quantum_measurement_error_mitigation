from qiskit import (
    IBMQ, QuantumCircuit, Aer, execute
)
from qiskit.providers.ibmq import least_busy
from qiskit.providers.aer.noise import NoiseModel

#
# Class for handling execution of quantum circuits,
# both for simulation and on IBMs physical quantum computers
#


class IBMQHandler:

    def __init__(self, n_qubits: int, shots: int = 8192, credentials: str = ""):
        self.n_qubits = n_qubits
        self.shots = shots

        self.aer_backend = Aer.get_backend("qasm_simulator")
        self.physical_backend = None

        self.credentials = credentials
        self.provider = None

    def set_credentials(self, credentials: str):
        self.credentials = credentials

    def enable_account(self, credentials: str = ""):
        if credentials == "":
            credentials = self.credentials
        else:
            self.credentials = credentials

        self.provider = IBMQ.enable_account(credentials)

    def find_least_busy(self):
        self.physical_backend = least_busy(self.provider.backends(filters=lambda x: x.configuration().n_qubits >= self.n_qubits and
                                   not x.configuration().simulator and x.status().operational==True))
        print("backend:", self.physical_backend.name())

    def set_specific_backend(self, backend_name: str):
        self.physical_backend = self.provider.get_backend(backend_name)
        print(self.physical_backend.name())

    def simulate_quantum_circuit(self, circuit: QuantumCircuit, noise_model: NoiseModel = None) -> dict:
        if noise_model == None:
            return execute(circuit, backend=self.aer_backend, shots=self.shots)
        else:
            return execute(circuit, backend=self.aer_backend, noise_model=noise_model, shots=self.shots)

    def run_quantum_circuit_on_IBMQ(self, circuit: QuantumCircuit) -> dict:
        return execute(circuit, backend=self.physical_backend, shots=self.shots)

    def retrieve_job(self, job_id: str):
        return self.physical_backend.retrieve_job(job_id=job_id)
