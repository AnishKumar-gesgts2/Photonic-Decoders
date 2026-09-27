from run_ancilla_free_pauli_gate import encoded_action_classes
from encoded_proxy import sample_shots
import numpy as np


def test_encoded_y_fault_is_not_always_joint() -> None:
    assert encoded_action_classes() == {"joint_xx_zz": 16,
                                        "xx_only": 8, "zz_erased": 8}


def test_encoded_shot_generator_agrees_with_exact_y_action_classes() -> None:
    shots = sample_shots(2000, 1.0, .5, 0.0, 1.0, 3711,
                         photons_per_bsm=2)
    error = shots["errors"].reshape(2000, 81, 2)
    known = shots["known"].reshape(2000, 81, 2)
    assert np.all(error[:, :, 0] == 1)
    fractions = (np.mean(known[:, :, 1] & (error[:, :, 1] == 1)),
                 np.mean(known[:, :, 1] & (error[:, :, 1] == 0)),
                 np.mean(~known[:, :, 1]))
    assert np.allclose(fractions, (.5, .25, .25), atol=.02)
