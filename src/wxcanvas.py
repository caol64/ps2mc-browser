import time
import wx
from pathlib import Path

import glm
import moderngl as mgl
from wx import EVT_TIMER, Timer, glcanvas
from wx.glcanvas import GLCanvas, GLContext

from models import BgModel, Camera, IconModel, CircleModel
import utils


class WxCanvas(GLCanvas):
    SIZE = (utils.CANVAS_WIDTH, utils.CANVAS_HEIGHT)
    FPS = 60

    def __init__(self, parent):
        GLCanvas.__init__(
            self,
            parent,
            size=WxCanvas.SIZE,
            attribList=[
                glcanvas.WX_GL_CORE_PROFILE,
                glcanvas.WX_GL_DOUBLEBUFFER,
                glcanvas.WX_GL_MAJOR_VERSION, 3,
                glcanvas.WX_GL_MINOR_VERSION, 3,
                glcanvas.WX_GL_RGBA,
                glcanvas.WX_GL_DEPTH_SIZE, 24,
            ],
        )
        self.parent = parent
        self._context = GLContext(self)
        self.SetCurrent(self._context)

        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.icon_sys, self.icons = None, None
        self.icon = None
        self.start_time = 0
        self.vao_index = 0
        self.circle_centers = []

        self.shader_program = dict()
        self.shader_program["bg"] = self.get_shader_program("bg")
        self.shader_program["icon"] = self.get_shader_program("icon")
        self.shader_program["circle"] = self.get_shader_program("circle")
        self.model = dict()

        self.m_model = glm.mat4()
        self.camera = Camera(WxCanvas.SIZE)

        self.frame_duration = 0.0
        self.ticker = Timer(self)
        self.Bind(EVT_TIMER, self.on_tick, self.ticker)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_MOTION, self.on_motion)

    def on_left_down(self, event):
        if self.circle_centers:
            screen_x, screen_y = event.GetPosition()
            index = utils.determine_circle_index(screen_x, screen_y, self.circle_centers)
            if index is not None:
                self.model["icon"].release()
                self.icon = self.icons[index]
                self.model["icon"] = IconModel(self.ctx, self.shader_program, self.icon)

    def on_motion(self, event):
        if self.circle_centers:
            screen_x, screen_y = event.GetPosition()
            ndc_x, ndc_y = utils.coord_convert(screen_x, screen_y)
            distance = 100
            for circle_center in self.circle_centers:
                _distance = utils.distance(ndc_x, ndc_y, circle_center[0], circle_center[1])
                if _distance < distance:
                    distance = _distance

            if distance <= utils.CIRCLE_RADIUS:
                self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            else:
                self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def on_tick(self, evt):
        self.render()

    def refresh(self, icon_sys, icons):
        """
        Refresh the canvas when a selected game is changed.
        The program will release the old 'bg' and 'icon' resources and initialize new 'bg' and 'icon'.
        """
        self.ticker.Stop()
        self.circle_centers = []
        [model.release() for model in self.model.values()]
        if self.start_time == 0:
            self.start_time = time.time()
        self.icon_sys, self.icons = icon_sys, icons
        self.icon = self.icons[0]

        self.model["icon"] = IconModel(self.ctx, self.shader_program, self.icon)
        self.model["bg"] = BgModel(self.ctx, self.shader_program, self.icon_sys)
        self.model["circles"] = CircleModel(self.ctx, self.shader_program, len(self.icons))
        self.circle_centers = self.model["circles"].circle_centers

        self.shader_program["icon"]["proj"].write(self.camera.proj)
        self.shader_program["icon"]["view"].write(self.camera.view)
        self.shader_program["icon"]["model"].write(self.m_model)
        self.shader_program["icon"]["ambient"] = self.icon_sys.ambient
        for index, light_pos in enumerate(self.icon_sys.light_dir):
            self.shader_program["icon"][f"lights[{index}].dir"] = light_pos
        for index, light_color in enumerate(self.icon_sys.light_colors):
            self.shader_program["icon"][f"lights[{index}].color"] = light_color
        self.shader_program["icon"]["texture0"] = 0
        self.frame_duration = (
            1.0 / WxCanvas.FPS * self.icon.frame_length / self.icon.frame_count
        )
        self.ticker.Start(WxCanvas.FPS)

    def render(self):
        """
        Render a frame of the image.
        """
        self.ctx.clear()
        self.update()
        self.model["bg"].vao().render()
        self.model["icon"].vao(self.vao_index).render()
        if self.model["circles"].vaos():
            for vao in self.model["circles"].vaos():
                vao.render(mgl.TRIANGLE_FAN)
        self.SwapBuffers()

    def update(self):
        """
        Update VAO, VBO, and other variables across frames.
        """
        animation_time = time.time() - self.start_time
        curr_frame = (
            int(animation_time * WxCanvas.FPS * self.icon.anim_speed)
            % self.icon.frame_length
        )
        curr_shape = int(
            curr_frame // (self.icon.frame_length / self.icon.animation_shapes)
        )
        frames_in_shape = self.icon.frame_length / self.icon.animation_shapes
        curr_frame_in_shape = curr_frame % frames_in_shape / frames_in_shape
        self.vao_index = curr_shape
        tween_factor = glm.float32(curr_frame_in_shape)
        self.shader_program["icon"]["tweenFactor"].write(tween_factor)
        m_model = glm.rotate(self.m_model, animation_time / 2, glm.vec3(0, 1, 0))
        self.shader_program["icon"]["model"].write(m_model)

    def get_shader_program(self, shader_name):
        with open(Path(__file__).parent / f"shaders/{shader_name}.vert") as file:
            vertex_shader = file.read()
        with open(Path(__file__).parent / f"shaders/{shader_name}.frag") as file:
            fragment_shader = file.read()
        program = self.ctx.program(
            vertex_shader=vertex_shader, fragment_shader=fragment_shader
        )
        return program

    def destroy(self):
        self.ticker.Destroy()
        [model.release() for model in self.model.values()]
        [program.release() for program in self.shader_program.values()]
        self.ctx.release()
