from qiskit import(
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

        provider = IBMQ.enable_account(credentials)

    def find_least_busy(self):
        self.physical_backend = least_busy(self.provider.backends(filters=lambda x: x.configuration().n_qubits >= self.n_qubits and
                                   not x.configuration().simulator and x.status().operational==True))
        print(self.physical_backend)

    def run_quantum_circuit(self, backend, shots: int, circuit: QuantumCircuit, noise_model: NoiseModel):
        if noise_model == None:
            job = execute(circuit, backend=self.aer_backend, shots=self.shots)
        else:
            job = execute(circuit, backend=self.aer_backend, noise_model=noise_model, shots=self.shots)

        result = job.result()
        measurement_results = result.get_counts()

        return measurement_results

    def simulate_quantum_circuit(self, circuit: QuantumCircuit, noise_model: NoiseModel = None) -> dict:
        return self.run_quantum_circuit(backend=self.aer_backend,
                                   shots = self.shots,
                                   circuit=circuit,
                                   noise_model= noise_model)

    def run_quantum_circuit_on_IBMQ(self, circuit: QuantumCircuit, noise_model: NoiseModel = None) -> dict:
        if self.physical_backend == None:
            print("Backend for IBMQ not set up")
            return {}

        return self.run_quantum_circuit(backend=self.physical_backend,
                                   shots = self.shots,
                                   circuit=circuit,
                                   noise_model= noise_model)
