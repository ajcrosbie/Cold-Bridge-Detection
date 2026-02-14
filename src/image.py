class Image :

    def __init__(self, pix, cb_pix, sf_pix, int_amb, ext, epsilon, lx, lch):
        self.image = pix
        self.cb_pix = cb_pix
        self.sf_pix = sf_pix
        self.int_amb = int_amb
        self.ext = ext
        self.epsilon = epsilon
        self.lx = lx
        self.lch = lch

    def get_cb(self):
        return self.cb_pix

    def get_sf(self):
        return self.sf_pix
    
