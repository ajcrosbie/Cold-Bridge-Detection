import numpy as np
import aggregate_calculations
import value_calculation
from image import Image

def make_dummy_image(cb_value, sf_value, int_amb, ext, epsilon, lx, lch):
    # Create an Image with constant pixel temperatures
    pix = np.zeros(100)
    cb_pix = np.full(100, cb_value)
    # psi value calculation assumes edge of 'cold bridge' is actually wall.
    # Probably want to change this
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

    expected = value_calculation.calc_psi(
        img.int_amb,
        img.ext,
        np.mean(img.get_sf()),
        img.get_cb(),
        img.epsilon,
        img.lx,
        img.lch,
    )

    result = aggregate_calculations.plot_psis([img])
    assert len(result) == 1
    # psi is a floating point calculation; allow a small tolerance
    assert np.isclose(result[0], expected, rtol=1e-6)

def test_plot_psis_multiple_images():
    imgs = [
        make_dummy_image(280, 285, 295, 270, 0.9, 0.001, 0.1),
        make_dummy_image(282, 286, 296, 271, 0.92, 0.0015, 0.12),
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

    result = aggregate_calculations.plot_psis(imgs)
    assert len(result) == 2
    assert np.allclose(result, expected, rtol=1e-6)

def main():
    test_plot_psis_multiple_images()
    test_plot_psis_single_image()

if __name__ == "__main__":
    main()