#version 330 core

in vec2 vertexPos;

void main() {
    gl_Position = vec4(vertexPos, 0, 1.0);
}