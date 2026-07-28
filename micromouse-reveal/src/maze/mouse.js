import * as THREE from 'three';

/**
 * A credible two-wheel differential-drive micromouse.
 * Compact square chassis, two driven wheels on the centre axis, a rear skid,
 * forward and diagonal IR sensors, low centre of gravity. No car body.
 */

// Proportioned against a real micromouse: a 180mm cell with a ~90mm robot.
export const MOUSE_W = 0.36;
export const MOUSE_L = 0.4;
export const MOUSE_H = 0.24;
export const WHEEL_R = 0.085;

export function createMouse() {
  const group = new THREE.Group();

  const pcb = new THREE.MeshStandardMaterial({ color: 0x0d3a3a, roughness: 0.55, metalness: 0.15 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x0a1418, roughness: 0.8, metalness: 0.1 });
  const rubber = new THREE.MeshStandardMaterial({ color: 0x14181a, roughness: 0.95, metalness: 0.0 });
  const mint = new THREE.MeshStandardMaterial({
    color: 0x6ff0d2,
    emissive: 0x6ff0d2,
    emissiveIntensity: 1.6,
    roughness: 0.4,
  });
  const orange = new THREE.MeshStandardMaterial({
    color: 0xff5b2e,
    emissive: 0xff5b2e,
    emissiveIntensity: 0.9,
    roughness: 0.5,
  });

  // Main PCB chassis, sitting low.
  const chassis = new THREE.Mesh(new THREE.BoxGeometry(MOUSE_W, 0.035, MOUSE_L), pcb);
  chassis.position.y = WHEEL_R;
  chassis.castShadow = true;
  group.add(chassis);

  // Battery / motor mass under the deck keeps the CoG believable.
  const mass = new THREE.Mesh(new THREE.BoxGeometry(MOUSE_W * 0.62, 0.07, MOUSE_L * 0.42), dark);
  mass.position.set(0, WHEEL_R - 0.04, -0.02);
  group.add(mass);

  // Upper deck with the accent stripe.
  const deck = new THREE.Mesh(new THREE.BoxGeometry(MOUSE_W * 0.8, 0.028, MOUSE_L * 0.55), pcb);
  deck.position.set(0, WHEEL_R + 0.09, -0.03);
  group.add(deck);

  const stripe = new THREE.Mesh(new THREE.BoxGeometry(MOUSE_W * 0.8, 0.006, 0.035), orange);
  stripe.position.set(0, WHEEL_R + 0.105, -0.03);
  group.add(stripe);

  const standoffs = [
    [-MOUSE_W * 0.32, -0.14],
    [MOUSE_W * 0.32, -0.14],
    [-MOUSE_W * 0.32, 0.06],
    [MOUSE_W * 0.32, 0.06],
  ];
  for (const [x, z] of standoffs) {
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.085, 8), dark);
    post.position.set(x, WHEEL_R + 0.05, z);
    group.add(post);
  }

  // Two driven wheels on the centre axis.
  const wheels = [];
  for (const side of [-1, 1]) {
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(WHEEL_R, WHEEL_R, 0.05, 20), rubber);
    wheel.rotation.z = Math.PI / 2;
    wheel.position.set(side * (MOUSE_W / 2 + 0.012), WHEEL_R, -0.02);
    wheel.castShadow = true;
    group.add(wheel);
    wheels.push(wheel);

    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.032, 0.032, 0.055, 12), mint);
    hub.rotation.z = Math.PI / 2;
    hub.position.copy(wheel.position);
    group.add(hub);
    wheel.userData.hub = hub;
  }

  // Rear skid instead of a third wheel.
  const skid = new THREE.Mesh(new THREE.SphereGeometry(0.032, 12, 10), dark);
  skid.position.set(0, 0.032, -MOUSE_L / 2 + 0.05);
  group.add(skid);

  // IR sensors: two forward, two diagonal.
  const emitters = [];
  const sensorSpec = [
    [-0.07, MOUSE_L / 2 - 0.01, 0],
    [0.07, MOUSE_L / 2 - 0.01, 0],
    [-MOUSE_W / 2 + 0.03, MOUSE_L / 2 - 0.07, -0.6],
    [MOUSE_W / 2 - 0.03, MOUSE_L / 2 - 0.07, 0.6],
  ];
  for (const [x, z, yaw] of sensorSpec) {
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.018, 10, 8), mint);
    led.position.set(x, WHEEL_R + 0.045, z);
    group.add(led);
    emitters.push(led);

    // Faint emitted cone so the sensors read on camera.
    const cone = new THREE.Mesh(
      new THREE.ConeGeometry(0.055, 0.42, 12, 1, true),
      new THREE.MeshBasicMaterial({
        color: 0x6ff0d2,
        transparent: true,
        opacity: 0.1,
        depthWrite: false,
        side: THREE.DoubleSide,
      }),
    );
    cone.position.set(x, WHEEL_R + 0.045, z + 0.2);
    cone.rotation.x = Math.PI / 2;
    cone.rotation.z = yaw;
    group.add(cone);
  }

  // Sensor glow pool on the floor ahead of the mouse.
  const pool = new THREE.Mesh(
    new THREE.CircleGeometry(0.38, 24),
    new THREE.MeshBasicMaterial({ color: 0x6ff0d2, transparent: true, opacity: 0.06, depthWrite: false }),
  );
  pool.rotation.x = -Math.PI / 2;
  pool.position.set(0, 0.004, MOUSE_L / 2 + 0.18);
  group.add(pool);

  // Contact shadow. The corridor blocks most of the key light, so the cast
  // shadow alone is too weak and the mouse reads as hovering.
  const contact = new THREE.Mesh(
    new THREE.CircleGeometry(MOUSE_W * 0.85, 24),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.42, depthWrite: false }),
  );
  contact.rotation.x = -Math.PI / 2;
  contact.position.set(0, 0.002, -0.01);
  contact.scale.set(1, 1, 1.15);
  group.add(contact);

  const headlight = new THREE.PointLight(0x9ffbe6, 1.5, 3.2, 2);
  headlight.position.set(0, WHEEL_R + 0.12, MOUSE_L / 2);
  group.add(headlight);

  return { group, wheels, emitters, headlight };
}
