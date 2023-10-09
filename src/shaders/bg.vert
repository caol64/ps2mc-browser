#version 330 core

in vec2 vertexPos;
in vec4 vertexColor;

out vec3 fragColor0;

void main() {
    fragColor0 = vertexColor.rgb;
    gl_Position = vec4(vertexPos.xy, 0.9999, 1.0);
}