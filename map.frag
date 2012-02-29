uniform sampler2D texture;

varying float light;

void main()
{
    vec4 color = texture2D(texture, gl_TexCoord[0].st);
    gl_FragColor = vec4(color.rgb * light, color.a);
}
