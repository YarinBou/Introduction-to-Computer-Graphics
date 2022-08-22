const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

function degrees_to_radians(degrees) {
    var pi = Math.PI;
    return degrees * (pi / 180);
}
const loader = new THREE.CubeTextureLoader();
const texture = loader.load([
    "src/skybox/right.png",
    "src/skybox/left.png",
    "src/skybox/top.png",
    "src/skybox/bottom.png",
    "src/skybox/front.png",
    "src/skybox/back.png",
]);
scene.background = texture;
const earthTexture = new THREE.TextureLoader().load("src/textures/earth.jpg");
const starTexture = new THREE.TextureLoader().load("src/textures/star.jpg");
const moonTexture = new THREE.TextureLoader().load("src/textures/moon.jpg");
const directionalLight = new THREE.DirectionalLight(0xffffff);
scene.add(directionalLight);
const ship_radius = 0.5;
const ship_height = 1.5;
const radial = 64;
const spaceship_geo = new THREE.CylinderGeometry(
    ship_radius,
    ship_radius,
    ship_height,
    radial
);
const spaceship_mat = new THREE.MeshBasicMaterial({ color: 0x0000ff });
const spaceship = new THREE.Mesh(spaceship_geo, spaceship_mat);
const shape = new THREE.Shape();
shape.moveTo(-ship_radius, (-ship_height * 5) / 8);
shape.lineTo(-ship_radius, (-ship_height * 1) / 8);
shape.lineTo(-2 * ship_radius, (-ship_height * 5) / 8);
const wing_geo = new THREE.ShapeGeometry(shape);
const wing_mat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    side: THREE.DoubleSide,
});
const wing_1 = new THREE.Mesh(wing_geo, wing_mat);
const rotate_Y_30 = new THREE.Matrix4().makeRotationY(degrees_to_radians(30));
const rotate_Y_120 = new THREE.Matrix4().makeRotationY(degrees_to_radians(120));
wing_1.applyMatrix4(rotate_Y_30);
const wing_2 = wing_1.clone();
wing_2.applyMatrix4(rotate_Y_120);
const wing_3 = wing_2.clone();
wing_3.applyMatrix4(rotate_Y_120);
spaceship.add(wing_1);
spaceship.add(wing_2);
spaceship.add(wing_3);
const inner_raduis = 0.05;
const outer_radius = 0.2;
const windowGeometry = new THREE.RingGeometry(
    inner_raduis,
    outer_radius,
    radial,
    radial / 8
);
const windowMaterial = new THREE.MeshBasicMaterial({
    color: 0xff0000,
    side: THREE.DoubleSide,
});
const window_1 = new THREE.Mesh(windowGeometry, windowMaterial);
window_1.applyMatrix4(new THREE.Matrix4().makeTranslation(0, 0, ship_radius));
spaceship.add(window_1);
const window_2 = window_1.clone();
window_2.applyMatrix4(
    new THREE.Matrix4().makeTranslation(0, outer_radius * 3, 0)
);
spaceship.add(window_2);
const head_radius = ship_radius;
const head_height = (ship_radius * 3) / 4;
const head_geo = new THREE.ConeGeometry(
    head_radius,
    (ship_radius * 3) / 4,
    radial
);
const head_mat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const head = new THREE.Mesh(head_geo, head_mat);
head.applyMatrix4(
    new THREE.Matrix4().makeTranslation(0, ship_height / 2 + head_height / 2, 0)
);
const spot_light = new THREE.PointLight(0xffffff, 0.8);
spot_light.applyMatrix4(new THREE.Matrix4().makeTranslation(0, head_height, 0));
head.add(spot_light);
spaceship.add(head);
scene.add(spaceship);
const moon_radius = 10;
const moon_geo = new THREE.SphereGeometry(moon_radius, 64, 64);
const moon_mat = new THREE.MeshPhongMaterial({ map: moonTexture });
const moon = new THREE.Mesh(moon_geo, moon_mat);
scene.add(moon);
const earth_radius = 20;
const earth_geo = new THREE.SphereGeometry(earth_radius, 64, 64);
const earth_mat = new THREE.MeshPhongMaterial({ map: earthTexture });
const earth = new THREE.Mesh(earth_geo, earth_mat);
scene.add(earth);
earth.applyMatrix4(new THREE.Matrix4().makeTranslation(100, 5, 100));
let earth_to_moon = new THREE.Vector3(100, 5, 100).normalize();
let moon_surface = earth_to_moon.multiplyScalar(moon_radius);
let earth_surface = new THREE.Vector3(100, 5, 100).sub(moon_surface);
const bezier_curve_1 = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 5, 40),
    new THREE.Vector3(100, 5, 100)
);

const bezier_curve_2 = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(15, 8, 30),
    new THREE.Vector3(100, 5, 100)
);

const bezier_curve_3 = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(30, 15, 20),
    new THREE.Vector3(100, 5, 100)
);
camera.position.set(-10, 40, -30);
camera.lookAt(0, 0, 0);
let curves_list = [bezier_curve_1, bezier_curve_2, bezier_curve_3];
const star_radius = 0.75;
const star_geo = new THREE.SphereGeometry(star_radius, 64, 64);
const star_mat = new THREE.MeshPhongMaterial({ map: starTexture });
class Star {
    constructor(t_value, curve_index, is_good = true) {
        this.t_value = t_value;
        this.curve_index = curve_index;
        if (is_good) {
            this.sphere = new THREE.Mesh(star_geo, star_mat);
        } else {
            this.sphere = new THREE.Mesh(star_geo, second_star_mat);
        }
        scene.add(this.sphere);
        this.sphere.position.copy(curves_list[curve_index].getPoint(t_value));
    }
}
const star_1 = new Star(0.2, 0);
const star_2 = new Star(0.8, 1);
const star_3 = new Star(0.5, 0);
const star_4 = new Star(0.3, 1);
const star_5 = new Star(0.6, 2);
const collectible_stars = [star_1, star_2, star_3, star_4, star_5];
const handle_keydown = (e) => {
    if (e.code == "ArrowLeft") {
        curve_index = (curve_index + 1) % 3;
    } else if (e.code == "ArrowRight") {
        if (curve_index == 0) {
            curve_index = 2;
        } else {
            curve_index = (curve_index - 1) % 3;
        }
    } else if (e.code == "ArrowUp") {
        if (t_increase_index != 2) {
            t_increase_index += 1;
        }
    } else if (e.code == "ArrowDown") {
        if (t_increase_index != 0) {
            t_increase_index -= 1;
        }
    }
};
document.addEventListener("keydown", handle_keydown);
const cameraPath = new THREE.Vector3(100, 5, 100);
let t = 0.1;
let t_increase_values = [0.0005, 0.001, 0.0015];
let t_increase_index = 1;
let curve_index = 0;
let score = 0;

function check_collision(star, t_value, curve_index, old_score) {
    if (
        Math.abs(star.t_value - t_value) <
        t_increase_values[t_increase_index] / 2 &&
        star.curve_index == curve_index
    ) {
        star.sphere.visible = false;
        score += old_score;
    }
}

function animate() {
    let id = requestAnimationFrame(animate);
    let curve = curves_list[curve_index];
    const up = new THREE.Vector3(0, 1, 0);
    const axis = new THREE.Vector3();
    const tangent = curve.getTangent(t);
    const new_position = curve.getPoint(t);
    let position_dif = new_position.sub(spaceship.position);
    spaceship.applyMatrix4(
        new THREE.Matrix4().makeTranslation(
            position_dif.getComponent(0),
            position_dif.getComponent(1),
            position_dif.getComponent(2)
        )
    );
    camera.applyMatrix4(
        new THREE.Matrix4().makeTranslation(
            cameraPath.getComponent(0) * t_increase_values[t_increase_index],
            cameraPath.getComponent(1) * t_increase_values[t_increase_index],
            cameraPath.getComponent(2) * t_increase_values[t_increase_index]
        )
    );
    axis.crossVectors(up, tangent).normalize();
    const radians = Math.acos(up.dot(tangent));
    spaceship.quaternion.setFromAxisAngle(axis, radians);
    collectible_stars.forEach((star) => check_collision(star, t, curve_index, 1));
    t += t_increase_values[t_increase_index];
    if (t > 1) {
        cancelAnimationFrame(id);
        alert(`Your score is ${score}`);
    }
    renderer.render(scene, camera);
}
animate();