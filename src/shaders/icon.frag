#version 330 core

// Define the maximum number of lights
#define MAX_NUM_TOTAL_LIGHTS 3

// Input variables
in vec2 uv0;
in vec4 normal0;

// Output color
out vec4 fragColor;

// Light structure
struct Light {
    vec4 dir;    // Light direction
    vec4 color;  // Light color
};

// Uniform variables
uniform sampler2D texture0;  // Texture
uniform vec4 ambient;        // Ambient light
uniform mat4 model;          // Model matrix

uniform Light lights[MAX_NUM_TOTAL_LIGHTS];  // Array of lights

void main() {
    // Calculate normalized normal vector
    vec3 normal = normalize(normal0).xyz;
    // Get color from the texture
    vec3 color = texture(texture0, uv0).rgb;
    // Calculate diffuse lighting
    vec3 diffuse = vec3(0);
    for (int i = 0; i < MAX_NUM_TOTAL_LIGHTS; i++) {
        // Calculate light direction
        vec3 lightDir = normalize(model * -lights[i].dir).xyz;
        // Calculate diffuse intensity
        float diff = max(dot(lightDir, normal), 0.0);
        // Accumulate diffuse lighting
        diffuse += diff * lights[i].color.rgb;
    }
    // Calculate the final color
    color = (ambient.rgb + diffuse) * color;
    // Set the output color
    fragColor = vec4(color, 1);
}