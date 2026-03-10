class Image :

    def __init__(self, pix, cb_pix, sf_temp, int_amb, ext, epsilon, lx, lch):
        self.image = pix        # float[]/ float[][] all pixels in the image (extract_temps)
        self.cb_pix = cb_pix    # float[] pixels in the image which are int he cold bridge (extract_cold_bridge)
        self.sf_temp = sf_temp   # (float) mean temperature of non-cold bridge surface
        self.int_amb = int_amb  # (float) internal ambient temperature (UI)
        self.ext = ext          # (float) external temperature, K (UI)
        self.epsilon = epsilon  # (float) emmisivity value (HC)
        self.lx = lx            # (float) length of one pixel, m (values_calc)
        self.lch = lch          # (float) height of wall being analysed, m (UI)

    def get_cb(self):
        """
        Returns a float[] of pixels that appear in the cold bridge
        Placeholder for now
        """
        return self.cb_pix  