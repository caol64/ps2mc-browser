#version 330 core

in vec3 fragColor0;

out vec4 fragColor;

uniform float alpha0;

void main() {
    fragColor = vec4(fragColor0, alpha0);
}