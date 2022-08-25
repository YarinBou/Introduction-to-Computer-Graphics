# Pre-requirments
from helper_classes import *
import matplotlib.pyplot as plt

# Render method
def render_scene(camera, ambient, lights, objects, screen_size, max_depth):
    width, height = screen_size
    ratio = float(width) / height
    screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom
    image = np.zeros((height, width, 3))
    for i, y in enumerate(np.linspace(screen[1], screen[3], height)):
        for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
            pixel = np.array([x, y, 0], dtype=np.float64)
            color = np.zeros(3)
            # This is the main loop where each pixel color is computed
            ray = Ray(camera, pixel - camera)
            current_obj, distance = ray.nearest_intersected_object(objects)
            if current_obj:
                hit_point = camera + distance * ray.direction
                color = get_current_color(ambient, lights, current_obj, objects, ray, hit_point, max_depth, camera)
            # We clip the values between 0 and 1 so all pixel values will make sense
            image[i, j] = np.clip(color, 0, 1)
    return image


# Write your own objects and lights
def your_own_scene():
    camera = np.array([0, 0, 1])
    plane_a = Plane([0, 1, 0], [0, -1, 0])
    plane_a.set_material([0.3, 0.5, 1], [0.3, 0.5, 1], [1, 1, 1], 100, 0.5)
    plane_b = Plane([0, 0, 1], [0, 0, -3])
    plane_b.set_material([0, 0.5, 0], [0, 1, 0], [1, 1, 1], 100, 0.5)
    sphere_a = Sphere([-0.5, 0.2, -1], 0.5)
    sphere_a.set_material([1, 0, 0], [1, 0, 0], [0.3, 0.3, 0.3], 100, 1)
    sphere_b = Sphere([0.8, 0, -0.5], 0.3)
    sphere_b.set_material([0, 1, 0], [0, 1, 0], [0.3, 0.3, 0.3], 100, 0.2)
    background = Plane([0, 0, 1], [0, 0, -3])
    background.set_material([0.2, 0.2, 0.2], [0.2, 0.2, 0.2], [0.2, 0.2, 0.2], 1000, 0.5)
    objects = [plane_a, plane_b, sphere_a, sphere_b, background]
    light_a = PointLight(intensity=np.array([1, 1, 1]), position=np.array([1, 1.5, 1]), kc=0.1, kl=0.1, kq=0.1)
    light_b = DirectionalLight(intensity=np.array([1, 1, 1]), direction=np.array([1, 1, 1]))
    lights = [light_a, light_b]
    return camera, lights, objects
