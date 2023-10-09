#version 330 core
#define MAX_NUM_TOTAL_LIGHTS 3

in vec2 uv0;
in vec4 fragColor0;
in vec3 normal0;
in vec3 fragPos0;

out vec4 fragColor;

struct Light {
    vec4 pos;
    vec4 color;
};

uniform sampler2D texture0;
uniform vec4 ambient;

uniform Light lights[MAX_NUM_TOTAL_LIGHTS];

void main() {
    vec3 normal = normalize(normal0);
    float alpha = fragColor0.a;
    vec3 color = fragColor0.rgb * texture(texture0, uv0).rgb;
    vec3 diffuse = vec3(0.0, 0.0, 0.0);
    for (int i = 0; i < MAX_NUM_TOTAL_LIGHTS; i++) {
        vec3 lightDir = normalize(lights[i].pos.xyz - fragPos0);
        float diff = max(dot(lightDir, normal), 0.0);
        diffuse += diff * lights[i].color.rgb;
    }
    color = (ambient.rgb + diffuse) * color;
    fragColor = vec4(color, alpha);
}