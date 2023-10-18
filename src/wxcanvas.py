from wx import Timer, EVT_TIMER
from wx.glcanvas import *
import moderngl as mgl
import glm
import time

from models import BgVbo
from models import SkyboxVbo
from models import IconVbo
from models import BgVao
from models import SkyboxVao
from models import IconVao
from models import Camera


class WxCanvas(GLCanvas):
    SIZE = (640, 480)
    FPS = 60

    def __init__(self, parent):
        GLCanvas.__init__(self, parent, size=WxCanvas.SIZE,
                          attribList=[
                              WX_GL_CORE_PROFILE,
                              WX_GL_DOUBLEBUFFER,
                              WX_GL_MAJOR_VERSION, 3,
                              WX_GL_MINOR_VERSION, 3,
                              WX_GL_RGBA,
                              WX_GL_DEPTH_SIZE, 24
                          ])
        self._context = GLContext(self)
        self.SetCurrent(self._context)

        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.icon_sys, self.icon = None, None
        self.start_time = 0
        self.vao_index = 0

        self.shader_program = dict()
        self.shader_program['skybox'] = self.get_shader_program('skybox')
        self.shader_program['bg'] = self.get_shader_program('bg')
        self.shader_program['icon'] = self.get_shader_program('icon')
        self.vbo = dict()
        self.vbo['skybox'] = self.ctx.buffer(SkyboxVbo().bg_vertex_data)
        self.vao = dict()
        self.vao['skybox'] = SkyboxVao(self.ctx, self.shader_program['skybox'], self.vbo['skybox']).vao

        self.m_model = glm.mat4()
        self.camera = Camera(WxCanvas.SIZE)
        self.texture_enabled = False
        self.texture = None

        self.frame_duration = 0.0
        self.ticker = Timer(self)
        self.Bind(EVT_TIMER, self.on_tick, self.ticker)

    def on_tick(self, evt):
        self.render()

    def refresh(self, icon_sys, icon):
        self.ticker.Stop()
        if self.start_time == 0:
            self.start_time = time.time()
        self.icon_sys, self.icon = icon_sys, icon
        bg_vbo = self.ctx.buffer(BgVbo(self.icon_sys).bg_vertex_data)
        icon_vbo = [self.ctx.buffer(x) for x in IconVbo(self.icon).vertex_data]

        self.vao['bg'] = BgVao(self.ctx, self.shader_program['bg'], bg_vbo).vao
        self.vao['icon'] = IconVao(self.ctx, self.shader_program['icon'], icon_vbo).vao

        texture_data = self.icon.texture
        if texture_data is not None:
            self.texture = self.ctx.texture(size=(128, 128), data=texture_data, components=3)
            self.texture_enabled = True

        self.shader_program['bg']['alpha0'].write(glm.float32(self.icon_sys.background_transparency / 128))
        self.shader_program['icon']['proj'].write(self.camera.proj)
        self.shader_program['icon']['view'].write(self.camera.view)
        self.shader_program['icon']['model'].write(self.m_model)
        self.shader_program['icon']['ambient'] = self.icon_sys.ambient
        for index, light_pos in enumerate(self.icon_sys.light_dir):
            self.shader_program['icon'][f'lights[{index}].dir'] = light_pos
        for index, light_color in enumerate(self.icon_sys.light_colors):
            self.shader_program['icon'][f'lights[{index}].color'] = light_color
        self.shader_program['icon']['texture0'] = 0
        if self.texture_enabled:
            self.texture.use()
        self.frame_duration = 1.0 / WxCanvas.FPS * self.icon.frame_length / self.icon.frame_count
        self.ticker.Start(WxCanvas.FPS)

    def render(self):
        self.ctx.clear()
        self.update()
        self.vao['skybox'].render()
        self.vao['bg'].render()
        self.vao['icon'][self.vao_index].render()
        self.SwapBuffers()

    def update(self):
        animation_time = time.time() - self.start_time
        curr_frame = int(animation_time * WxCanvas.FPS * self.icon.anim_speed) % self.icon.frame_length
        curr_shape = int(curr_frame // (self.icon.frame_length / self.icon.animation_shapes))
        frames_in_shape = self.icon.frame_length / self.icon.animation_shapes
        curr_frame_in_shape = curr_frame % frames_in_shape / frames_in_shape
        self.vao_index = curr_shape
        tween_factor = glm.float32(curr_frame_in_shape)
        self.shader_program['icon']['tweenFactor'].write(tween_factor)
        m_model = glm.rotate(self.m_model, animation_time / 2, glm.vec3(0, 1, 0))
        self.shader_program['icon']['model'].write(m_model)

    def get_shader_program(self, shader_name):
        with open(f'shaders/{shader_name}.vert') as file:
            vertex_shader = file.read()
        with open(f'shaders/{shader_name}.frag') as file:
            fragment_shader = file.read()
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program
