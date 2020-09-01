from pypozyx import Quaternion, EulerAngles

class pose :
    def __init__(self,x,y,z,q,e):
        self.x = 0
        self.y = 0
        self.z = 0
        self.q = Quaternion()
        self.e = EulerAngles()
