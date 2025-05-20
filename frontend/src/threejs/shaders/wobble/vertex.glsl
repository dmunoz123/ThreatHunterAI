#include ../includes/simplexNoise4d.glsl

uniform vec2 uMouse;
uniform float uMouseStrength;
uniform float uMouseRadius;

uniform float uTime;
uniform float uPositionFrequency;
uniform float uTimeFrequency;
uniform float uStrength;

uniform float uWarpPositionFrequency;
uniform float uWarpTimeFrequency;
uniform float uWarpStrength;

uniform float uShift;

attribute vec4 tangent;

varying float vWobble;

float getWobble(vec3 position)
{
  // Start with the original position
  vec3 warpedPosition = position;

  // Apply the global noise-based warp
  warpedPosition += simplexNoise4d(vec4(
    position * uWarpPositionFrequency,
    uTime * uWarpTimeFrequency
  )) * uWarpStrength;

  // Convert the 2D mouse uniform to a 3D position.
  // You may need to adjust this conversion depending on your scene setup.
  vec3 mousePos = vec3(uMouse, 0.25);

  // Calculate distance from the current vertex to the mouse position
  float distToMouse = length(position - mousePos);

  // Create an influence factor based on distance: 
  // Near the mouse, influence is strong (close to 1), and far away, it fades to 0.
  float mouseInfluence = 1.0 - smoothstep(0.0, uMouseRadius, distToMouse);

  // Compute the direction from the vertex to the mouse
  vec3 directionToMouse = normalize(mousePos - position);

  // Calculate the massive warp offset toward the mouse
  vec3 mouseWarp = cos(directionToMouse * mouseInfluence * uMouseStrength);

  // Add the extra massive warp to the already globally warped position
  warpedPosition += mouseWarp;

  // Finally, calculate the final displacement using noise on the warped position
  float finalPosition = simplexNoise4d(vec4(
    warpedPosition * uPositionFrequency, // XYZ
    uTime * uTimeFrequency                 // W
  )) * uStrength;

  return finalPosition;
}

void main()
{

  vec3 biTangent = cross(normal, tangent.xyz);

  // Neighbours Position
  float shift = uShift;
  vec3 positionA = csm_Position + tangent.xyz * shift;
  vec3 positionB = csm_Position + biTangent * shift;

  // Wobble
  float wobble = getWobble(csm_Position);
  csm_Position += wobble * normal;
  positionA    += getWobble(positionA) * normal;
  positionB    += getWobble(positionB) * normal;
  

  // compute normal (direction normalized for length of1)
  vec3 toA = normalize(positionA - csm_Position);
  vec3 toB = normalize(positionB - csm_Position);
  csm_Normal = cross(toA, toB);

  // varyings
  vWobble = wobble / uStrength;
}