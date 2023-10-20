#version 330 core

in vec3 vertexPos;
in vec4 vertexColor;

out vec4 fragColor0;

void main() {
    fragColor0 = vertexColor;
    gl_Position = vec4(vertexPos, 1.0);
}