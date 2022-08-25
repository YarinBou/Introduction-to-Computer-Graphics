# Pre-requirments
import numpy as np


# This function gets a vector and returns its normalized form.
def normalize(vector):
    return vector / np.linalg.norm(vector)


# This function gets a vector and the normal of the surface it hit
# This function returns the vector that reflects from the surface
def reflected(vector, normal):
    v = normalize(vector - 2 * np.dot(vector, normal) * normal)
    return v


# Lights
class LightSource:
    def __init__(self, intensity):
        self.intensity = np.array(intensity)


class DirectionalLight(LightSource):
    def __init__(self, intensity, direction):
        super().__init__(intensity)
        self.direction = normalize(np.array(direction, dtype=np.float64))

    # This function returns the ray that goes from the light source to a point
    def get_light_ray(self, intersection_point):
        return Ray(intersection_point, self.direction)

    # This function returns the distance from a point to the light source
    def get_distance_from_light(self, intersection):
        return np.inf

    # This function returns the light intensity at a point
    def get_intensity(self, intersection):
        return self.intensity


class PointLight(LightSource):
    def __init__(self, intensity, position, kc, kl, kq):
        super().__init__(intensity)
        self.position = np.array(position, dtype=np.float64)
        self.kc = kc
        self.kl = kl
        self.kq = kq

    # This function returns the ray that goes from the light source to a point
    def get_light_ray(self, intersection):
        return Ray(intersection, normalize(self.position - intersection))

    # This function returns the distance from a point to the light source
    def get_distance_from_light(self, intersection):
        return np.linalg.norm(intersection - self.position)

    # This function returns the light intensity at a point
    def get_intensity(self, intersection):
        d = self.get_distance_from_light(intersection)
        return self.intensity / (self.kc + self.kl * d + self.kq * np.power(d, 2))


class SpotLight(LightSource):
    def __init__(self, intensity, position, direction, kc, kl, kq):
        super().__init__(intensity)
        self.position = np.array(position, dtype=np.float64)
        self.direction = normalize(np.array(direction, dtype=np.float64)) * -1
        self.kc = kc
        self.kl = kl
        self.kq = kq

    # This function returns the ray that goes from the light source to a point
    def get_light_ray(self, intersection):
        # TODO
        return Ray(intersection, normalize(self.position - intersection))

    def get_distance_from_light(self, intersection):
        return np.linalg.norm(intersection - self.position)

    def get_intensity(self, intersection):
        v = normalize(intersection - self.position)
        d = self.get_distance_from_light(intersection)
        return self.intensity * np.dot(self.direction, v) / (self.kc + self.kl * d + self.kq * (d ** 2))


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = normalize(np.array(direction, dtype=np.float64))

    # The function is getting the collection of objects in the scene and looks for the one with minimum distance.
    # The function should return the nearest object and its distance (in two different arguments)
    def nearest_intersected_object(self, objects):
        nearest_object = None
        min_distance = np.inf
        for current_obj in objects:
            res = current_obj.intersect(self)
            if res[0]:
                if res[1] < min_distance:
                    nearest_object = res[0]
                    min_distance = res[1]

        return nearest_object, min_distance

    # helper function that get the new point.
    def get_new_point(self, t: float) -> np.array:
        if t > 0:
            return self.origin + t * self.direction
        else:
            return None


class Object3D:
    def set_material(self, ambient, diffuse, specular, shininess, reflection):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflection = reflection


class Plane(Object3D):
    def __init__(self, normal, point):
        self.normal = normalize(np.array(normal, dtype=np.float64))
        self.point = np.array(point, dtype=np.float64)
        self.d = -np.dot(normal, point)

    def compute_normal(self, P):
        return self.normal

    def intersect(self, ray: Ray):
        v = self.point - ray.origin
        t = (np.dot(v, self.normal) / np.dot(self.normal, ray.direction))
        if t > 0:
            return self, t
        else:
            return None, None


class Triangle(Object3D):
    # Triangle gets 3 points as arguments
    def __init__(self, a, b, c):
        self.a = np.array(a, dtype=np.float64)
        self.b = np.array(b, dtype=np.float64)
        self.c = np.array(c, dtype=np.float64)
        self.normal = None
        self.normal = self.compute_normal(None)

    def compute_normal(self, P):
        if self.normal is not None:
            return self.normal
        ls = [self.a, self.b, self.c]
        a = max(ls, key=lambda t: t[0])
        remove_array(ls, a)
        b = max(ls, key=lambda t: t[1])
        remove_array(ls, b)
        c = ls[0]
        self.normal = normalize(np.cross((b - a), (c - a)))
        return self.normal

    def __onTriangle(self, p):
        return (np.dot(np.cross((self.b - self.a), (p - self.a)), self.normal) >= 0 and np.dot(
            np.cross((self.c - self.b), (p - self.b)), self.normal) >= 0 and
                np.dot(np.cross((self.a - self.c), (p - self.c)), self.normal) >= 0)

    # Hint: First find the intersection on the plane
    # Later, find if the point is in the triangle using barycentric coordinates
    def intersect(self, ray: Ray):
        d = -np.dot(self.normal, self.a)
        intersection, t = None, None
        if np.dot(self.normal, ray.direction) != 0:
            t = -(np.dot(self.normal, ray.origin) + d) / np.dot(self.normal, ray.direction)
            intersection = ray.get_new_point(t)
        if intersection is not None and self.__onTriangle(intersection):
            return self, t
        else:
            return None, None


class Sphere(Object3D):
    def __init__(self, center, radius: float):
        self.center = np.array(center, dtype=np.float64)
        self.radius = radius

    def compute_normal(self, P):
        return normalize(P - self.center)

    def intersect(self, ray: Ray):
        a = np.sum(ray.direction ** 2)
        b = np.sum(2 * ray.direction * (ray.origin - self.center))
        c = np.sum((ray.origin - self.center) ** 2) - self.radius ** 2
        coeff = np.array([a, b, c], dtype=np.float64)
        roots = np.roots(coeff)
        if np.isreal(roots[0]):
            roots.sort()
            if roots[0] > 0:
                return self, roots[0]
            elif roots[1] > 0:
                return self, roots[1]
        return None, None


def get_current_color(ambient, light_arr, obj: Object3D, obj_arr, ray: Ray, hit_point, max_depth, camera, level=0):
    # base case
    if obj is None or level == max_depth:
        return np.array([0, 0, 0], dtype=np.float64)

    color = obj.ambient * np.array(ambient, dtype=np.float64)

    for light in light_arr:

        shifted = hit_point + (1e-10 * obj.compute_normal(hit_point))
        hit_to_light = light.get_light_ray(shifted)
        hit_to_light_obj, hit_to_light_dis = hit_to_light.nearest_intersected_object(obj_arr)

        if hit_to_light_obj is None or hit_to_light_dis > light.get_distance_from_light(hit_point):
            color += obj.diffuse * light.get_intensity(hit_point) * np.dot(obj.compute_normal(hit_point),
                                                                           hit_to_light.direction)
            color += obj.specular * light.get_intensity(hit_point) * np.power(
                np.dot(reflected(-hit_to_light.direction, obj.compute_normal(hit_point)), -ray.direction),
                obj.shininess)

    if obj.reflection > 0:

        r_ray = Ray(shifted, reflected(ray.direction, obj.compute_normal(hit_point)))
        next_obj, next_dist = r_ray.nearest_intersected_object(obj_arr)
        nextHitP = r_ray.get_new_point(next_dist)

        if next_obj:
            color += get_current_color(ambient, light_arr, next_obj, obj_arr, r_ray, nextHitP, max_depth, camera,
                                       level + 1) * obj.reflection
    return color


def remove_array(ls, arr):
    i = 0
    size = len(ls)
    while i != size and not np.array_equal(ls[i], arr):
        i += 1
    if i != size:
        ls.pop(i)


class Mesh(Object3D):
    # Mesh are defined by a list of vertices, and a list of faces.
    # The faces are triplets of vertices by their index number.
    def __init__(self, v_list, f_list):
        self.v_list = v_list
        self.f_list = f_list
        self.triangle_list = self.create_triangle_list()

    def create_triangle_list(self):
        l = [Triangle(self.v_list[i[0]], self.v_list[i[1]], self.v_list[i[2]]) for i in self.f_list]
        return l

    def apply_materials_to_triangles(self):
        for t in self.triangle_list:
            t.set_material(self.ambient, self.diffuse, self.specular, self.shininess, self.reflection)

    # Hint: Intersect returns both distance and nearest object.
    # Keep track of both.
    def intersect(self, ray: Ray):
        return ray.nearest_intersected_object(self.triangle_list)
