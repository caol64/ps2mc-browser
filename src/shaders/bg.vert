#version 330 core

in vec3 vertexPos;
in vec4 vertexColor;

out vec3 fragColor0;

void main() {
    fragColor0 = vertexColor.rgb;
    gl_Position = vec4(vertexPos, 1.0);
}