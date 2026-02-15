class Image :

    def __init__(self, pix, cb_pix, sf_pix, int_amb, ext, epsilon, lx, lch):
        self.image = pix        # float[]/ float[][] all pixels in the image
        self.cb_pix = cb_pix    # float[] pixels in the image which are int he cold bridge
        self.sf_pix = sf_pix    # (float[]) pixels that are on the unaffected surface of the external wall
        self.int_amb = int_amb  # (float) internal ambient temperature 
        self.ext = ext          # (float) external temperature, K
        self.epsilon = epsilon  # (float) emmisivity value
        self.lx = lx            # (float) length of one pixel, m
        self.lch = lch          # (float) height of wall being analysed, m

    def get_cb(self):
        """
        Returns a float[] of pixels that appear in the cold bridge
        Placeholder for now
        """
        return self.cb_pix

    def get_sf(self):
        """
        Returns a float[] of pixels that appear on the unaffected surface of the external wall
        Placeholder for now
        """
        return self.sf_pix
    
