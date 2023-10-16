#version 330 core
#define MAX_NUM_TOTAL_LIGHTS 3

in vec2 uv0;
in vec4 normal0;

out vec4 fragColor;

struct Light {
    vec4 dir;
    vec4 color;
};

uniform sampler2D texture0;
uniform vec4 ambient;
uniform mat4 model;

uniform Light lights[MAX_NUM_TOTAL_LIGHTS];

void main() {
    vec3 normal = normalize(vec3(model * normal0));
    vec3 color = texture(texture0, uv0).rgb;
    vec3 diffuse = vec3(0);
    for (int i = 0; i < MAX_NUM_TOTAL_LIGHTS; i++) {
        vec3 lightDir = normalize(vec3(model * -lights[i].dir));
        float diff = max(dot(lightDir, normal), 0.0);
        diffuse += diff * lights[i].color.rgb;
    }
    color = (ambient.rgb + diffuse) * color;
    fragColor = vec4(color, 1);
}