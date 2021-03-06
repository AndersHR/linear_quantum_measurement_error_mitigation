from qiskit import (
    IBMQ, QuantumCircuit
)
from numpy import (
    ndarray, asarray, zeros, empty,
    sum, dot
)

from scipy.linalg import inv

#
# This class handles linear error mitigation for measurement errors on quantum computers.
# The script is based of off IBM's qiskit tutorial on the subject:
# https://qiskit.org/textbook/ch-quantum-hardware/measurement-error-mitigation.html
#


class MeasurementErrorMitigation:

    def __init__(self, n_qubits: int):

        self.n_qubits = n_qubits
        self.error_mitigation_matrix = empty(0)

    def build_mitigation_circuit(self):
        circuits = []
        for i in range(2 ** self.n_qubits):

            circuits.append(QuantumCircuit(5))

            bit_string = '{0:0{1}b}'.format(i, self.n_qubits)

            for k in range(self.n_qubits):
                if bit_string[self.n_qubits - k - 1] == '1':
                    circuits[i].x(k)

            circuits[i].measure_all()

        return circuits

    def build_error_mitigation_matrix(self, measurement_results: list):
        matrix = zeros((2 ** self.n_qubits, 2 ** self.n_qubits))

        for i in range(2 ** self.n_qubits):
            vec = build_vector(measurement_results[i], self.n_qubits)
            num_shots = sum(vec)

            for k in range(2 ** self.n_qubits):
                matrix[i][k] = vec[k] / num_shots

        self.error_mitigation_matrix = inv(matrix)

    def mitigate_errors(self, measurement_results: list or dict or ndarray) -> dict:
        if self.error_mitigation_matrix.shape[0] == 0:
            print("Error mitigation matrix not built")
            return {}

        if type(measurement_results) == dict:
            vec = build_vector(measurement_results, self.n_qubits)
        elif type(measurement_results) == list:
            vec = asarray(measurement_results)
        elif type(measurement_results) == ndarray:
            vec = measurement_results
        else:
            print("Invalid argument type", type(measurement_results))
            return {}

        return build_dict(dot(self.error_mitigation_matrix, vec), self.n_qubits)

# Utility functions:

# qiskit returns measurement result counts in dictionaries on the form:
# job.result.counts() = { "00000": 7000, "00001": 534, "00011": 12, ... , "11111": 35 }
# computational basis states where the measurement result count was 0 are not included in the dict

# This function builds a numpy array on the form
# vec = numpy.ndarray( [ 7000, 534, 0, 12, .... , 35 ] )

def build_vector(measurement_results: dict, n_qubits: int) -> ndarray:
    vec = zeros(2 ** n_qubits)

    for i in range(2 ** n_qubits):
        bit_string = '{0:0{1}b}'.format(i, n_qubits)    # every n-bit bitstring

        if bit_string in measurement_results.keys():
            vec[i] = measurement_results[bit_string]

    return vec


# This function takes a numpy array on the form outputted from the function above,
# and builds a dictionary on the same form as qiskit outputs the measurement results counts in

def build_dict(vec: ndarray, n_qubits: int) -> dict:
    dic = {}

    for i in range(2 ** n_qubits):
        if vec[i] != 0:
            bit_string = '{0:0{1}b}'.format(i, n_qubits)    # every n-bit bitstring

            dic[bit_string] = max(int(vec[i]), 0)

    return dic
