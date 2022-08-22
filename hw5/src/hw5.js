import { OrbitControls } from "./OrbitControls.js";
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
const spaceShip = new THREE.Group();
const mesh_white_props = {
    color: 0xf7f7f7,
    side: THREE.DoubleSide,
};
const mesh_blue_props = {
    color: 0x0036b2,
    side: THREE.DoubleSide,
};
const cylinderRadius = 2;
const cylinderHeight = 6;
const plantRadius = cylinderRadius * 5;
const headRadius = cylinderRadius * 3;

// body
const body_geo = new THREE.CylinderGeometry(
    cylinderRadius,
    cylinderRadius,
    cylinderHeight,
    40
);
const body_mat = new THREE.MeshBasicMaterial(mesh_blue_props);
const body = new THREE.Mesh(body_geo, body_mat);
spaceShip.add(body);
const body_trans = new THREE.Matrix4().makeTranslation(20, 5, 1);
body.applyMatrix4(body_trans);
// head
const head_geo = new THREE.ConeGeometry(2, headRadius, 32);
const head_mat = new THREE.MeshBasicMaterial(mesh_white_props);
const head = new THREE.Mesh(head_geo, head_mat);
spaceShip.add(head);
const head_trans = new THREE.Matrix4().makeTranslation(20, 9, 1);
head.applyMatrix4(head_trans);
// window 1
const window1_geo = new THREE.RingGeometry(0.3, 0.5, 40);
const window1_mat = new THREE.MeshBasicMaterial(mesh_white_props);
const window_1 = new THREE.Mesh(window1_geo, window1_mat);
spaceShip.add(window_1);
const window1_trans = new THREE.Matrix4().makeTranslation(20, 6, 3);
window_1.applyMatrix4(window1_trans);
// window 2
const window2_geo = new THREE.RingGeometry(0.3, 0.5, 40);
const window2_mat = new THREE.MeshBasicMaterial(mesh_white_props);
const window_2 = new THREE.Mesh(window2_geo, window2_mat);
spaceShip.add(window_2);
const window2_trans = new THREE.Matrix4().makeTranslation(20, 4, 3);
window_2.applyMatrix4(window2_trans);
// wing 1
const wing1_geo = new THREE.PlaneGeometry(1.5, 2);
const wing1_mat = new THREE.MeshBasicMaterial(mesh_white_props);
const wing_1 = new THREE.Mesh(wing1_geo, wing1_mat);
spaceShip.add(wing_1);
const wing1_trans = new THREE.Matrix4().makeTranslation(18, 2, 1);
wing_1.applyMatrix4(wing1_trans);
// wing 2
const wing2_geo = new THREE.PlaneGeometry(1.5, 2);
const wing2_mat = new THREE.MeshBasicMaterial(mesh_white_props);
const wing_2 = new THREE.Mesh(wing2_geo, wing2_mat);
spaceShip.add(wing_2);
const wing2_trans = new THREE.Matrix4().makeTranslation(22, 2, 1);
wing_2.applyMatrix4(wing2_trans);
// rot
const rot = new THREE.Matrix4().makeRotationAxis(
    new THREE.Vector3(0, 1, 0),
    Math.PI / 2
);
// wing 3
const wing3_g = new THREE.PlaneGeometry(1.5, 2);
const wing3_m = new THREE.MeshBasicMaterial(mesh_white_props);
const wing_3 = new THREE.Mesh(wing3_g, wing3_m);
spaceShip.add(wing_3);
const wing3_trans = new THREE.Matrix4().makeTranslation(20, 2, 3);
wing_3.applyMatrix4(wing3_trans.multiply(rot));
// wing 4
const wing4_g = new THREE.PlaneGeometry(1.5, 2);
const wing4_m = new THREE.MeshBasicMaterial(mesh_white_props);
const wing_4 = new THREE.Mesh(wing4_g, wing4_m);
spaceShip.add(wing_4);
const wing4_trans = new THREE.Matrix4().makeTranslation(20, 2, -1);
wing_4.applyMatrix4(wing4_trans.multiply(rot));
//  earth white
const earth_geo = new THREE.SphereGeometry(plantRadius, 40, 8);
const earth_mat = new THREE.MeshBasicMaterial({
    color: 0xffffff,
    wireframe: true,
});
const earth = new THREE.Mesh(earth_geo, earth_mat);
earth.add(spaceShip);
scene.add(earth);
const earth_trans = new THREE.Matrix4().makeTranslation(-6, -6, 0);
earth.applyMatrix4(earth_trans);
const cameraTranslate = new THREE.Matrix4();
cameraTranslate.makeTranslation(0, 0, 5);
camera.applyMatrix4(cameraTranslate);
renderer.render(scene, camera);
const controls = new OrbitControls(camera, renderer.domElement);
let isOrbitEnabled = true;
const toggleOrbit = (e) => {
    if (e.key == "o") {
        isOrbitEnabled = !isOrbitEnabled;
    }
};
let isWireFrameEnabled = false;
const toggleWireframe = (e) => {
    if (e.key == "w") {
        scene.traverse((object) => {
            if (object.material) {
                object.material.wireframe = !isWireFrameEnabled;
            }
        });
        isWireFrameEnabled = !isWireFrameEnabled;
    }
};
let state_one = false;
const toggleAnimationOne = (e) => {
    if (e.key == "1") {
        state_one = !state_one;
    }
};
let state_two = false;
const toggleAnimationTwo = (e) => {
    if (e.key == "2") {
        state_two = !state_two;
    }
};
let state_three = false;
const toggleAnimationThree = (e) => {
    if (e.key == "3") {
        state_three = !state_three;
    }
};
document.addEventListener("keydown", toggleOrbit);
document.addEventListener("keydown", toggleWireframe);
document.addEventListener("keydown", toggleAnimationOne);
document.addEventListener("keydown", toggleAnimationTwo);
document.addEventListener("keydown", toggleAnimationThree);
controls.update();

function animate() {
    requestAnimationFrame(animate);
    controls.enabled = isOrbitEnabled;
    if (state_one) {
        spaceShip.applyMatrix4(rot.makeRotationY(degrees_to_radians(1)));
    }
    if (state_two) {
        spaceShip.applyMatrix4(rot.makeRotationZ(degrees_to_radians(1)));
    }
    if (state_three) {
        let target = new THREE.Vector3();
        spaceShip.getWorldPosition(target);
        target.multiplyScalar(0.005);
        let translation = new THREE.Matrix4().makeTranslation(
            target.getComponent(0),
            target.getComponent(1),
            target.getComponent(2)
        );
        spaceShip.applyMatrix4(translation);
    }
    controls.update();
    renderer.render(scene, camera);
}
animate();