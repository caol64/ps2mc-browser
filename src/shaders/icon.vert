#version 330 core

// Input vertex attributes
in vec3 vertexPos;       // Current vertex position
in vec3 nextVertexPos;   // Next vertex position (for tweening)
in vec2 texCoord;        // Texture coordinates
in vec3 normal;          // Vertex normal

// Output variables for fragment shader
out vec2 uv0;            // Texture coordinates for fragment shader
out vec4 normal0;        // Transformed normal for fragment shader

// Uniform matrices
uniform mat4 proj;       // Projection matrix
uniform mat4 view;       // View matrix
uniform mat4 model;      // Model matrix
uniform float tweenFactor; // Tweening factor for vertex animation

void main() {
    // Pass texture coordinates to fragment shader
    uv0 = texCoord;

    // Transform and pass normal to fragment shader
    normal0 = model * vec4(normal, 1);

    // Interpolate between current and next vertex positions based on tween factor
    vec4 basePos = vec4(mix(vertexPos, nextVertexPos, tweenFactor), 1.0);

    // Combine transformations and set the final vertex position
    gl_Position = proj * view * model * basePos;
}
