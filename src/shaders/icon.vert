#version 330 core

in vec4 vertexPos;
in vec2 texCoord;
in vec4 vertexColor;
in vec4 nextVertexPos;
in vec4 normal;

out vec4 fragColor0;
out vec2 uv0;
out vec3 normal0;
out vec3 fragPos0;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;
uniform float tweenFactor;

void main() {
    uv0 = texCoord;
    fragColor0 = vertexColor;
    normal0 = mat3(model) * normalize(normal.xyz);
    vec4 basePos = vec4(mix(vertexPos.xyz, nextVertexPos.xyz, tweenFactor), 1.0);
    gl_Position = proj * view * model * basePos;
    fragPos0 = gl_Position.xyz;
}