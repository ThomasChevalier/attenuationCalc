#version 330 core
out vec4 FragColor;
  
in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

/* At first the shader used the Normal to calculate lighting, together with a light
color and a light position. However this is not necessary so I removed this feature.
I left Normal and TexCoord because it's easier to have them here when I will need them.*/

uniform sampler2D texture1;

void main()
{
	FragColor = texture(texture1, TexCoord);
}
