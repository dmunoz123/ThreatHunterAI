import WobblySphere from "./WobblySphere";
import { Canvas } from "@react-three/fiber";
import { PerspectiveCamera, Bvh, OrbitControls } from "@react-three/drei";
import { useControls } from "leva";

export default function CanvasComponent() {

  const { lightColor, lightIntensity } = useControls("Directional Light", {
    lightColor: { value: "#ffffff" },
    lightIntensity: { value: 1.5, min: 0, max: 5, step: 0.1 },
  });

  return (
    <div className="canvas-container">
      <Canvas shadows>
        <Bvh>
          <PerspectiveCamera
            makeDefault
            fov={25}
            near={0.1}
            far={100}
            position={[0, 0.85, 14]}
          />
          <OrbitControls enableDamping />
          <directionalLight
            // Pass the Leva-controlled values into the light's args.
            args={[lightColor, lightIntensity]}
            position={[0.0, 3.0, 5.0]}
            castShadow
          />
          <ambientLight intensity={0.6}/>
          <WobblySphere />
        </Bvh>
      </Canvas>
    </div>
  );
}