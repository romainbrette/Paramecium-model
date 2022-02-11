'''
Simulates Paramecium motion.
Uses quaternions for 3D motion.

The cell coordinate system is chosen so that the cell points upward (along positive z axis).
'''
import numpy as np
from pyquaternion import Quaternion
from numpy.linalg import norm
import imageio

__all__ = ['MovingCell', 'PlaneMovingCell']

class MovingCell(object):
    '''
    A cell moving in 3D.
    All coordinates in um.
    '''
    def __init__(self, x=None, q=None):
        # Initial position
        if x is None:
            self.x = np.zeros(3)
        else:
            self.x = x

        # Initial orientation
        if q is None: # Default: horizontal
            self.q = Quaternion(axis=np.array([1., 0., 0.]), radians=np.pi / 2) # radians: gives the mouth position
        elif isinstance(q,Quaternion):
            self.q = q
        else: # assuming a 3D axis is given
            self.q = Quaternion(axis=q, radians=np.pi / 2)

        self.dt = 1 # to be changed by user
        self.v_sedimentation = np.zeros(3) # sedimentation velocity
        self.set_velocity(1000.) # 1 mm/s
        self.set_rotation_angle(20./180.*np.pi) # 20 degrees
        self.beta_gravity = 0.

    def set_gravity(self, v_sedimentation = 84., beta = 7/180.*np.pi):
        '''
        Sets gravity parameters.
        `v_sedimentation` : sedimentation velocity (Machemer et al. 1991: 84 um/s)
        `beta` : gravity torque in rad/s (Roberts: 7 deg/s = 7/180*pi rad/s)
        '''
        self.v_sedimentation = v_sedimentation*np.array([0.,0.,-1.])
        self.beta_gravity = beta

    def set_velocity(self, v):
        '''
        Sets linear velocity vector, along main cell axis
        '''
        self.v = v*np.array([0., 0., 1.])

    def set_rotation_angle(self, theta, spin=2*np.pi):
        '''
        Sets the angle of the rotation axis, facing the mouth.
        '''
        self.omega = -np.array([np.sin(theta),0.,np.cos(theta)])*spin # left spiral, default 1 Hz

    def spiral_axis(self):
        '''
        Returns the spiral axis vector in the observer coordinate system.
        The magnitude is the angular speed.
        '''
        return (self.q*Quaternion(vector=self.omega)*self.q.conjugate).vector

    def integrate(self, dt=None):
        '''
        Moves the cell by one timestep.
        `v` : linear velocity
        `omega` : angular velocity vector
        Both in the cell coordinate system.
        '''
        if dt is None:
            dt = self.dt

        # Gravity torque (in Paramecium system!)
        p = (self.q.conjugate * Quaternion(vector=np.array([0., 0., -1.])) * self.q).vector  # gravity vector
        omega_gravity = -self.beta_gravity * np.cross(np.array([0., 0., 1.]), p)

        self.x += ((self.q*Quaternion(vector=self.v)*self.q.conjugate).vector + self.v_sedimentation)*dt
        self.q.integrate(self.omega+omega_gravity,dt)

class PlaneMovingCell(MovingCell):
    '''
    A cell moving in a plane.
    Coordinates are still given in 3D, but with z = 0.
    '''
    def __init__(self, x=None, theta=0.):
        '''
        Here `x` is (x,y) coordinates.
        '''
        if x is not None:
            x= np.array([x[0], x[1], 0.])
        q = np.array([np.cos(theta),np.sin(theta),0.])
        MovingCell.__init__(self, x, q)

    def set_gravity(self, v_sedimentation, beta):
        raise NotImplementedError('No gravity in a 2D constrained cell')

    def integrate(self, dt=None):
        # We make a 3D movement, then move the cell back into the plane
        MovingCell.integrate(self, dt)

        # Orientation vector
        p = (self.q * Quaternion(vector=np.array([0., 0., 1.])) * self.q.conjugate).vector
        p = p / norm(p)

        # Orthogonal axis: this is the rotation axis to move the orientation vector back to the plane
        axis = np.cross(np.array([0., 0., 1.]), p)

        # Projection on the horizontal plane
        p_H = np.zeros_like(p)
        p_H[:2] = p[:2]

        # Angle
        cos_theta = norm(p_H)
        sin_theta = p[2]
        theta = np.arctan2(sin_theta, cos_theta)

        # Corrective rotation
        correction = Quaternion(radians=theta, axis=axis)
        self.q = correction * self.q

    def orientation(self):
        '''
        Returns the 2D angle of the cell.
        '''
        # Orientation vector (missing: the spin angle)
        p = (self.q * Quaternion(vector=np.array([0., 0., 1.])) * self.q.conjugate).vector[:2]
        p = p / norm(p)
        return np.arctan2(p[1],p[0])

    def mouth_position(self):
        '''
        Returns (x,y) mouth position relative to the center, assuming cell width is 1
        '''
        p2 = (self.q * Quaternion(vector=np.array([1., 0., 0.])) * self.q.conjugate).vector
        # Side
        if p2[2] < 0.:
            return None # mouth is not visible
        else:
            # Project on plane
            return p2[0], p2[1]

if __name__ == '__main__':
    from pylab import *
    from plotting import cell_mask

    if True:
        cell = MovingCell()
        cell.set_gravity()

        trajectory = []
        for _ in range(1000):
            cell.integrate(dt=0.005)
            trajectory.append(copy(cell.x))
        trajectory = array(trajectory)

        fig = plt.figure()
        ax_3D = fig.add_subplot(111, projection='3d')
        m, M = trajectory.min(), trajectory.max()

        x, y, z = trajectory.T
        ax_3D.plot(x, y, z)
        ax_3D.set_xlim(m, M)
        ax_3D.set_ylim(m, M)
        ax_3D.set_zlim(m, M)

        #image = zeros((500,500))
        #imshow(cell_mask(200,200,image, pixel_size=2., theta = pi/2.))
        show()
    else:
        cell = PlaneMovingCell((2000,2000),theta=pi/4)

        trajectory = []
        orientation = []
        for _ in range(1000):
            cell.integrate(dt=0.033)
            trajectory.append(copy(cell.x))
            orientation.append(cell.orientation())
        trajectory = array(trajectory)
        x, y, _ = trajectory.T

        image = zeros((500,500))
        writer = imageio.get_writer('cell.mp4', fps=30.)

        for i in range(len(trajectory)):
            im = cell_mask(x[i],y[i],image, pixel_size=8., theta = orientation[i])
            writer.append_data(im)

        writer.close()
