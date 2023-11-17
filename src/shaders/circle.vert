#version 330 core

in vec2 vertexPos;
uniform vec2 translation;

void main() {
    gl_Position = vec4(vertexPos + translation, 0, 1.0);
}