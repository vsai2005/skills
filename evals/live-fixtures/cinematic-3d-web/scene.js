// Deliberately weak starting point for the cinematic-3d-web live evaluation.
// The exercise is about production reasoning, not copying a finished demo.

const canvas = document.querySelector("#stage");

function startScene() {
  if (!window.THREE) return;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 2, 6);

  scene.add(new THREE.AmbientLight(0xffffff, 1.4));

  const subject = new THREE.Mesh(
    new THREE.BoxGeometry(2.5, 3, 2.5),
    new THREE.MeshStandardMaterial({ color: 0x315a78, roughness: 0.5 })
  );
  scene.add(subject);

  function render() {
    subject.rotation.y += 0.004;
    renderer.render(scene, camera);
    requestAnimationFrame(render);
  }
  render();

  window.addEventListener("scroll", () => {
    camera.position.z = 6 - window.scrollY / 900;
  });
}

startScene();
