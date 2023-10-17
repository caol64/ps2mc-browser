#version 330 core

in vec3 vertexPos;

void main() {
    gl_Position = vec4(vertexPos, 1.0);
}