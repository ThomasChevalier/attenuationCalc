#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out vec3 FragPos;
out vec3 Normal;
out vec3 Color;

uniform mat4 view;
uniform mat4 projection;

/* Custom tag that will be replaced */
uniform vec3 offsets[#satellites_number#];
uniform vec3 colors[#satellites_number#];

void main()
{
	vec3 offseted = offsets[gl_InstanceID] + aPos;
    gl_Position = projection * view * vec4(offseted, 1.0);
    FragPos = offseted;
    Normal = aNormal;
    Color = colors[gl_InstanceID];
}
