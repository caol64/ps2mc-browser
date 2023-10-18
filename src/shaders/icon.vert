#version 330 core

in vec4 vertexPos;
in vec2 texCoord;
in vec4 vertexColor;
in vec4 nextVertexPos;
in vec4 normal;

out vec2 uv0;
out vec4 normal0;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;
uniform float tweenFactor;

void main() {
    uv0 = texCoord;
    normal0 = model * normal;
    vec4 basePos = vec4(mix(vertexPos.xyz, nextVertexPos.xyz, tweenFactor), 1.0);
    gl_Position = proj * view * model * basePos;
}