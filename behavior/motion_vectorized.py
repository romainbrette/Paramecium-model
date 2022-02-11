'''
Simulates Paramecium motion of a group of cells.
Uses quaternions for 3D motion.

The cell coordinate system is chosen so that the cell points upward (along positive z axis).
'''
import numpy as np
import quaternion
from numpy.linalg import norm
import imageio

__all__ = ['MovingCells', 'PlaneMovingCells']

class MovingCells(object):
    '''
    Cells moving in 3D.
    All coordinates in um.

    `x` : coordinate array, of shape (N,3)
    `axis` : orientation of the cells
    '''
    def __init__(self, N, axis=None):
        # Initial position
        self.x = np.zeros((N,3))
        self.v = np.zeros((len(self),3))
        self.omega = np.zeros((len(self),3))

        # Initial orientation
        if axis is None: # Default: horizontal
            self.set_orientation(np.array([1., 0., 0.]), np.pi / 2) # radians: gives the mouth position
        else: # assuming a 3D axis is given
            self.set_orientation(axis,np.pi / 2)

        self.dt = 1 # to be changed by user
        self.set_gravity(0.) # sedimentation velocity
        self.set_velocity(1000.) # 1 mm/s
        self.set_rotation_angle(20./180.*np.pi) # 20 degrees
        self.beta_gravity = 0.

    def __len__(self):
        return self.x.shape[0]

    def set_orientation(self, axis, angle = np.pi / 2):
        '''
        Sets the orientation of cells.
        `angle` is in radians.
        '''
        if axis.shape == (3,): # The same axis for all
            self. q = np.ones(len(self))*quaternion.from_rotation_vector(axis*angle)
        else:
            self.q = quaternion.from_rotation_vector(axis*angle)

    def set_gravity(self, v_sedimentation = 84., beta = 7/180.*np.pi):
        '''
        Sets gravity parameters.
        `v_sedimentation` : sedimentation velocity (Machemer et al. 1991: 84 um/s)
        `beta` : gravity torque in rad/s (Roberts: 7 deg/s = 7/180*pi rad/s)
        '''
        self.v_sedimentation = np.zeros((len(self),3))
        self.v_sedimentation[:,2] = - v_sedimentation
        self.beta_gravity = beta

    def set_velocity(self, v):
        '''
        Sets linear velocity vector, along main cell axis
        '''
        self.v[:,:2] = 0
        self.v[:,2] = v

    def set_rotation_angle(self, theta, spin = 2*np.pi):
        '''
        Sets the angle of the rotation axis, facing the mouth.
        `spin` is the rotation speed in radians per second
        '''
        self.omega[:,0] = -np.sin(theta)*spin # left spiral, 1 Hz
        self.omega[:,1] = 0
        self.omega[:,2] = -np.cos(theta)*spin # left spiral, 1 Hz

    def spiral_axis(self):
        '''
        Returns the spiral axis vector in the observer coordinate system.
        The magnitude is the angular speed.
        '''
        return quaternion.as_vector_part(self.q*quaternion.from_rotation_vector(self.omega)*self.q.conjugate())

    def integrate(self, dt=None):
        '''
        Moves the cell by one timestep.
        '''
        if dt is None:
            dt = self.dt

        # Gravity torque (in Paramecium system!)
        p = quaternion.as_vector_part(self.q.conjugate() * quaternion.from_vector_part(np.array([0., 0., -1.])) * self.q)  # gravity vector
        omega_gravity = -self.beta_gravity * np.cross(np.array([0., 0., 1.]), p)

        self.x += (quaternion.as_vector_part(self.q*quaternion.from_vector_part(self.v)*self.q.conjugate()) + self.v_sedimentation)*dt

        #self.q.integrate(self.omega+omega_gravity,dt)
        self.q = self.q*quaternion.from_rotation_vector((self.omega+omega_gravity)*dt)
        # Renormalize
        self.q = self.q/np.absolute(self.q)

class PlaneMovingCells(MovingCells):
    '''
    A cell moving in a plane.
    Coordinates are still given in 3D, but with z = 0.
    '''
    def __init__(self, N, theta=0.):
        # Initial position
        self.x = np.zeros((N,3))
        self.v = np.zeros((len(self),3))
        self.omega = np.zeros((len(self),3))
        self.dt = 1 # to be changed by user
        self.set_velocity(1000.) # 1 mm/s
        self.set_rotation_angle(20./180.*np.pi) # 20 degrees
        self.set_gravity(0.)
        self.set_orientation(theta)

    def set_orientation(self, theta):
        '''
        Sets the 2D orientation of cells.
        `theta` is in radians.
        '''
        axis = np.zeros((len(self), 3))
        axis[:,0] = np.cos(theta)
        axis[:,1] = np.sin(theta)
        MovingCells.set_orientation(self, axis)

    def integrate(self, dt=None):
        # We make a 3D movement, then move the cell back into the plane
        MovingCells.integrate(self, dt)

        # Orientation vector
        p = quaternion.as_vector_part(self.q * quaternion.from_vector_part(np.array([0., 0., 1.])) * self.q.conjugate())
        p = (p.T / norm(p, axis=1)).T

        # Orthogonal axis: this is the rotation axis to move the orientation vector back to the plane
        axis = np.cross(np.array([0., 0., 1.]), p)

        # Projection on the horizontal plane
        p_H = np.zeros_like(p)
        p_H[:,2] = p[:,2]

        # Angle
        cos_theta = norm(p_H, axis=1)
        sin_theta = p[:,2]
        theta = np.arctan2(sin_theta, cos_theta)

        # Corrective rotation
        correction = quaternion.from_rotation_vector((axis.T*theta).T)
        self.q = correction * self.q

    def orientation(self):
        '''
        Returns the 2D angle of the cells.
        '''
        # Orientation vector (missing: the spin angle)
        p = quaternion.as_vector_part(self.q * quaternion.from_vector_part(np.array([0., 0., 1.])) * self.q.conjugate())[:,:2]
        p = (p.T / norm(p, axis=1)).T
        return np.arctan2(p[:,1],p[:,0])

    def mouth_position(self):
        '''
        Returns (x,y) mouth position relative to the center, assuming cell width is 1

        NOT VECTORIZED YET
        '''
        p2 = quaternion.as_vector_part(self.q * quaternion.from_vector_part(np.array([1., 0., 0.])) * self.q.conjugate())
        # Side
        if p2[2] < 0.:
            return None # mouth is not visible
        else:
            # Project on plane
            return p2[0], p2[1]

if __name__ == '__main__':
    from pylab import *
    from plotting import cell_mask, cell_indices

    if False:
        cells = MovingCells(2)
        cells.set_gravity()
        cells.set_orientation(np.array([[1., 0., 0.],[0.,1.,0.]]))

        print(cells.omega)

        trajectory = []
        for _ in range(1000):
            cells.integrate(dt=0.005)
            trajectory.append(1*cells.x[0,:])
        trajectory = array(trajectory)

        print(trajectory[:10,:])

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
        N = 100
        cells = PlaneMovingCells(N,theta=np.pi/4)
        cells.x[:,:2] = rand(N,2)*4000
        cells.set_orientation(2*np.pi*rand(N))

        image = np.zeros((500,500))
        writer = imageio.get_writer('cell.mp4', fps=30.)

        for _ in range(1000):
            cells.integrate(dt=0.033)
            im = np.zeros_like(image)
            for j in range(N):
                #im += cell_mask(cells.x[j,0], cells.x[j,1], image, pixel_size=8., theta=cells.orientation()[j])
                im[cell_indices(cells.x[j, 0], cells.x[j, 1], image, pixel_size=8., theta=cells.orientation()[j])] = 1
            #im = np.clip(im, 0, 1)
            writer.append_data(im)

        writer.close()
