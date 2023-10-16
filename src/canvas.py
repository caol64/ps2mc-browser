import time
import moderngl as mgl
import glm

from models import BgVbo
from models import IconVbo
from models import BgVao
from models import IconVao
from models import Camera


class Canvas:
    def __init__(self, window, game_name):
        self.window = window
        self.icon_sys, self.icon = window.get_icon(game_name)
        self.start_time = time.time()
        self.vao_index = 0
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        bg_vbo = self.ctx.buffer(BgVbo(self.icon_sys).bg_vertex_data)
        icon_vbo = [self.ctx.buffer(x) for x in IconVbo(self.icon).vertex_data]
        self.shader_program = {'bg': self.get_shader_program('bg'),
                               'icon': self.get_shader_program('icon')}
        self.vao = {'bg': BgVao(self.ctx, self.shader_program['bg'], bg_vbo).vao,
                    'icon': IconVao(self.ctx, self.shader_program['icon'], icon_vbo).vao}

        self.m_model = glm.mat4()
        self.camera = Camera((window.screen.get_width(), window.screen.get_height()))
        self.texture_enabled = False
        texture_data = self.icon.texture
        if texture_data is not None:
            self.texture = self.ctx.texture(size=(128, 128), data=texture_data, components=3)
            self.texture_enabled = True
        self.frame_duration = 1.0 / window.fps * self.icon.frame_length / self.icon.frame_count
        self.on_init()

    def on_init(self):
        self.shader_program['bg']['alpha0'].write(glm.float32(self.icon_sys.background_transparency / 128))
        self.shader_program['icon']['proj'].write(self.camera.proj)
        self.shader_program['icon']['view'].write(self.camera.view)
        self.shader_program['icon']['model'].write(self.m_model)
        self.shader_program['icon']['ambient'] = self.icon_sys.ambient
        for index, light_pos in enumerate(self.icon_sys.light_dir):
            self.shader_program['icon'][f'lights[{index}].pos'] = light_pos
        for index, light_color in enumerate(self.icon_sys.light_colors):
            self.shader_program['icon'][f'lights[{index}].color'] = light_color
        self.shader_program['icon']['texture0'] = 0
        if self.texture_enabled:
            self.texture.use()

    def render(self):
        self.ctx.clear()
        self.update()
        self.vao['icon'][self.vao_index].render()
        self.vao['bg'].render()

    def update(self):
        animation_time = time.time() - self.start_time
        curr_frame = int(animation_time * self.window.fps * self.icon.anim_speed) % self.icon.frame_length
        curr_shape = int(curr_frame // (self.icon.frame_length / self.icon.animation_shapes))
        frames_in_shape = self.icon.frame_length / self.icon.animation_shapes
        curr_frame_in_shape = curr_frame % frames_in_shape / frames_in_shape
        self.vao_index = curr_shape
        tween_factor = glm.float32(curr_frame_in_shape)
        self.shader_program['icon']['tweenFactor'].write(tween_factor)
        m_model = glm.rotate(self.m_model, glm.radians(180) + animation_time / 2, glm.vec3(0, 1, 0))
        self.shader_program['icon']['model'].write(m_model)

    def get_shader_program(self, shader_name):
        with open(f'shaders/{shader_name}.vert') as file:
            vertex_shader = file.read()
        with open(f'shaders/{shader_name}.frag') as file:
            fragment_shader = file.read()
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program
