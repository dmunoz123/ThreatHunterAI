varying float vWobble;

uniform vec3 uColorA;
uniform vec3 uColorB;



void main()
{

  // remaps wobble to smoothly transition from 0-1 instead of -1-1
  float colorMix = smoothstep(-1.0, 1.0, vWobble);
  // //keeping it green
  //csm_Emissive = vec3(0.0, vWobble, 0.0);
  //csm_Roughness = 1.0 - csm_Metalness;

  // Shiny tip
  csm_Roughness = 1.0 - colorMix;
  csm_Clearcoat = 1.0 - colorMix;
  // csm_Transmission = colorMix;

  

  csm_DiffuseColor.rgb = mix(uColorA, uColorB, colorMix);

  // Mirror step ( below 0.25 = 0 above =1 )
  //csm_Metalness = step(0.25, vWobble);
  // csm_Roughness = 1.0 - csm_Metalness;

  
}