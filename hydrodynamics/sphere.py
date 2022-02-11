'''
Calculation of translational and rotational velocities from the direction of power strokes,
using the mobility matrix of a sphere.
See Lauga and Powers (2009).

These velocities are essentially proportional to forces and torques, so that's what we calculate.

We use spherical coordinates (theta, phi).
The angle of the local force is psi, with 0 meaning vertical downward, i.e. North to South (z<0).
'''
from numpy import *
from numpy.linalg import norm

__all__ = ['sphere_total_force_torque', 'spinning_velocity', 'translational_velocity', 'rotation_angle', 'speed_along_axis']

def sphere_total_force_torque(anterior_left, anterior_right, posterior_left, posterior_right):
    '''
    Calculates total force and torque, given the angle spi of the force in 4 quarters of the sphere,
    relative to the oral groove (e.g. anterior left = anterior side, left when facing the oral groove).

    The force is that produced by the fluid, i.e., the opposite of the power stroke.
    The force is assumed equal to 1.

    Returns the velocity vector U and the rotation vector Omega.
    '''
    N = 1000
    theta, phi = meshgrid(linspace(0,pi,N), linspace(-pi,pi,N))
    x_2D = sin(theta)*cos(phi)
    y_2D = sin(theta)*sin(phi)
    z_2D = cos(theta)
    theta = theta.flatten()
    phi = phi.flatten()

    # Angle of the force produced by the power stroke on the sphere
    # (opposite of power stroke vector, i.e. +pi)
    psi = zeros_like(theta)
    psi[(phi<0) & (theta<pi/2)] = anterior_left
    psi[(phi > 0) & (theta < pi / 2)] = anterior_right
    psi[(phi < 0) & (theta > pi / 2)] = posterior_left
    psi[(phi > 0) & (theta > pi / 2)] = posterior_right

    # Magnitude of force
    magnitude = ones_like(theta)

    # Sphere radius
    r = 0.006 # in mm

    # Local force
    F = magnitude*array([cos(theta)*cos(psi)*cos(phi)-sin(psi)*sin(phi),
               cos(theta)*cos(psi)*sin(phi)+sin(psi)*cos(phi),
               -sin(theta)*cos(psi)])
    # Local torque
    L = r*magnitude*array([-cos(theta)*sin(psi)*cos(phi)-cos(psi)*sin(phi),
               -cos(theta)*sin(psi)*sin(phi)+cos(psi)*cos(phi),
               sin(theta)*sin(psi)])

    # Surface element
    dtheta = pi/N
    dphi = 2*pi/N
    dS = sin(theta)*dtheta*dphi

    # Total force
    F_tot = sum(F*dS, axis=1)
    L_tot = sum(L*dS, axis=1)

    # Velocities (unitless since we don't know the magnitude of the forces)
    U = F_tot/(6*pi*r)
    Omega = L_tot/(8*pi*r**3)

    return U, Omega

def spinning_velocity(Omega):
    return norm(Omega)/(2*pi)

def translational_velocity(U):
    return norm(U)

def rotation_angle(Omega):
    return arctan2(abs(Omega[0]), abs(Omega[2]))

def speed_along_axis(U, Omega):
    return abs(dot(Omega,U)/norm(Omega))
