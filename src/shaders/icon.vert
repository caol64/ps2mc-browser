#version 330 core

in vec3 vertexPos;
in vec3 nextVertexPos;
in vec2 texCoord;
in vec3 normal;

out vec2 uv0;
out vec4 normal0;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;
uniform float tweenFactor;

void main() {
    uv0 = texCoord;
    normal0 = model * vec4(normal, 1);
    vec4 basePos = vec4(mix(vertexPos, nextVertexPos, tweenFactor), 1.0);
    gl_Position = proj * view * model * basePos;
}