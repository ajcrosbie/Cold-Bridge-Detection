import numpy as np
import aggregate_calculations
import value_calculation
from image import Image

def make_dummy_image(cb_value, sf_value, int_amb, ext, epsilon, lx, lch):
    # Create an Image with constant pixel temperatures
    pix = np.zeros(100)
    cb_pix = np.full(100, cb_value)
    # psi value calculation assumes edge of 'cold bridge' is actually wall.
    # TODO: Probably want to change this
    cb_pix[:10] = np.full(10, sf_value)
    sf_pix = np.full(100, sf_value)

    return Image(pix, cb_pix, sf_pix, int_amb, ext, epsilon, lx, lch)

def test_plot_psis_single_image():

    img = make_dummy_image(
        cb_value=280.0,
        sf_value=285.0,
        int_amb=295.0,
        ext=270.0,
        epsilon=0.95,
        lx=0.001,
        lch=0.1,
    )

    aggregate_calculations.plot_psis([img])

def test_get_psis_single_image():

    img = make_dummy_image(
        cb_value=280.0,
        sf_value=285.0,
        int_amb=295.0,
        ext=270.0,
        epsilon=0.95,
        lx=0.001,
        lch=0.1,
    )

    expected = value_calculation.calc_psi(
        img.int_amb,
        img.ext,
        np.mean(img.get_sf()),
        img.get_cb(),
        img.epsilon,
        img.lx,
        img.lch,
    )

    result = aggregate_calculations.get_psis([img])
    assert len(result) == 1
    # psi is a floating point calculation; allow a small tolerance
    assert np.isclose(result[0], expected, rtol=1e-6)

def test_plot_psis_multiple_images():
    imgs = [
        make_dummy_image(280, 287, 293, 273, 0.9, 0.001, 0.1),
        make_dummy_image(286, 292, 296, 283, 0.92, 0.0015, 0.12),
        make_dummy_image(277, 284, 290, 270, 0.88, 0.005, 1)
    ]

    aggregate_calculations.plot_psis(imgs)

def test_get_psis_multiple_images():
    imgs = [
        make_dummy_image(280, 287, 293, 273, 0.9, 0.001, 0.1),
        make_dummy_image(286, 292, 296, 283, 0.92, 0.0015, 0.12),
        make_dummy_image(277, 284, 290, 270, 0.88, 0.005, 1)
    ]

    expected = np.array([
        value_calculation.calc_psi(
            img.int_amb,
            img.ext,
            np.mean(img.get_sf()),
            img.get_cb(),
            img.epsilon,
            img.lx,
            img.lch,
        )
        for img in imgs
    ])

    result = aggregate_calculations.get_psis(imgs)
    assert len(result) == 3
    assert np.allclose(result, expected, rtol=1e-6)

def test_plot_sensitivities():
    imgs = [
        make_dummy_image(280, 287, 293, 273, 0.9, 0.001, 0.1),
        make_dummy_image(286, 292, 296, 283, 0.92, 0.0015, 0.12),
        make_dummy_image(277, 284, 290, 270, 0.88, 0.005, 1)
    ]

    expected = value_calculation.calc_sensitivity(
            {img.ext: np.mean(img.get_cb()) for img in imgs}
        )

    sensitivity = aggregate_calculations.plot_sensitivies(imgs)
    assert np.allclose(sensitivity, expected, rtol=1e-6)

def main():
    test_plot_psis_multiple_images()
    test_plot_psis_single_image()
    test_get_psis_single_image()
    test_get_psis_multiple_images()
    test_plot_sensitivities()

if __name__ == "__main__":
    main()