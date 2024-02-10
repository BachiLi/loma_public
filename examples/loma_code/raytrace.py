# Code from https://raytracing.github.io/books/RayTracingInOneWeekend.html

class Vec3:
    x : float
    y : float
    z : float

class Sphere:
    center : Vec3
    radius : float

class Ray:
    org : Vec3
    dir : Vec3

def add(a : In[Vec3], b : In[Vec3]) -> Vec3:
    ret : Vec3
    ret.x = a.x + b.x
    ret.y = a.y + b.y
    ret.z = a.z + b.z
    return ret

def sub(a : In[Vec3], b : In[Vec3]) -> Vec3:
    ret : Vec3
    ret.x = a.x - b.x
    ret.y = a.y - b.y
    ret.z = a.z - b.z
    return ret

def mul(a : In[float], b : In[Vec3]) -> Vec3:
    ret : Vec3
    ret.x = a * b.x
    ret.y = a * b.y
    ret.z = a * b.z
    return ret    

def dot(a : In[Vec3], b : In[Vec3]) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z

def normalize(v : In[Vec3]) -> Vec3:
    l : float = sqrt(dot(v, v))
    ret : Vec3
    ret.x = v.x / l
    ret.y = v.y / l
    ret.z = v.z / l
    return ret

# Returns distance. If distance is zero or negative, the hit misses
def sphere_isect(sph : In[Sphere], ray : In[Ray]) -> float:
    oc : Vec3 = sub(ray.org, sph.center)
    a : float = dot(ray.dir, ray.dir)
    b : float = 2 * dot(oc, ray.dir)
    c : float = dot(oc, oc) - sph.radius * sph.radius
    discriminant : float = b * b - 4 * a * c
    ret_dist : float = 0
    if discriminant < 0:
        ret_dist = -1
    else:
        ret_dist = (-b - sqrt(discriminant)) / (2 * a)
    return ret_dist

def ray_color(ray : In[Ray]) -> Vec3:
    sph : Sphere
    sph.center.x = 0
    sph.center.y = 0
    sph.center.z = -1
    sph.radius = 0.5

    ret_color : Vec3
    t : float = sphere_isect(sph, ray)
    if t > 0:
        N : Vec3 = normalize(sub(add(ray.org, mul(t, ray.dir)), sph.center))
        ret_color.x = 0.5 * (N.x + 1)
        ret_color.y = 0.5 * (N.y + 1)
        ret_color.z = 0.5 * (N.z + 1)
    else:
        a : float = 0.5 * ray.dir.y + 1
        white : Vec3
        white.x = 1
        white.y = 1
        white.z = 1
        blue : Vec3
        blue.x = 0.5
        blue.y = 0.7
        blue.z = 1
        ret_color = add(mul((1 - a), white), mul(a, blue))
    return ret_color

def raytrace(w : In[int], h : In[int], image : Out[Array[Vec3]]):
    # Camera setup
    aspect_ratio : float = int2float(w) / int2float(h)
    focal_length : float = 1.0
    viewport_height : float = 2.0
    viewport_width : float = viewport_height * aspect_ratio
    camera_center : Vec3
    camera_center.x = 0
    camera_center.y = 0
    camera_center.z = 0
    # Calculate the horizontal and vertical delta vectors from pixel to pixel.
    pixel_delta_u : Vec3
    pixel_delta_u.x = viewport_width / w
    pixel_delta_u.y = 0
    pixel_delta_u.z = 0
    pixel_delta_v : Vec3
    pixel_delta_v.x = 0
    pixel_delta_v.y = -viewport_height / h
    pixel_delta_v.z = 0
    # Calculate the location of the upper left pixel.
    viewport_upper_left : Vec3
    viewport_upper_left.x = camera_center.x - viewport_width / 2
    viewport_upper_left.y = camera_center.y + viewport_height / 2
    viewport_upper_left.z = camera_center.z - focal_length
    pixel00_loc : Vec3 = viewport_upper_left
    pixel00_loc.x = pixel00_loc.x + pixel_delta_u.x / 2
    pixel00_loc.y = pixel00_loc.y - pixel_delta_v.y / 2

    y : int = 0
    while (y < h, max_iter := 4096):
        x : int = 0
        while (x < w, max_iter := 4096):
            pixel_center : Vec3 = add(add(pixel00_loc, mul(x, pixel_delta_u)), mul(y, pixel_delta_v))
            ray : Ray
            ray.org = camera_center
            ray.dir = normalize(sub(pixel_center, camera_center))
            image[w * y + x] = ray_color(ray)

            x = x + 1
        y = y + 1
