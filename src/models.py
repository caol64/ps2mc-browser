import glm
import numpy as np


class Camera:
    FOV = 50
    NEAR = 0.1
    FAR = 100

    def __init__(self, win_size):
        self.aspect_ratio = win_size[0] / win_size[1]
        self.position = glm.vec3(0, -4.0, -10)
        self.up = glm.vec3(0, -1, 0)
        self.view = glm.lookAt(self.position, glm.vec3(0, -2, 0), self.up)
        self.proj = glm.perspective(glm.radians(Camera.FOV), self.aspect_ratio, Camera.NEAR, Camera.FAR)


class IconVbo:

    def __init__(self, icon):
        self.vertex_data = []
        for i in range(icon.animation_shapes):
            vertex_data = icon.vertex_data[:, i]
            uv_data = icon.uv_data
            color_data = icon.color_data
            vertex_data = np.hstack((vertex_data, uv_data))
            vertex_data = vertex_data.astype(np.float16)
            vertex_data = np.hstack((vertex_data, color_data))
            h = i + 1
            if h >= icon.animation_shapes:
                h = 0
            vertex_data = np.hstack((vertex_data, icon.vertex_data[:, h]))
            self.vertex_data.append(np.hstack((vertex_data, icon.normal_data)))


class BgVbo:
    def __init__(self, icon_sys):
        bg_colors = icon_sys.bg_colors
        bg_colors = np.asarray((bg_colors[0], bg_colors[2], bg_colors[3], bg_colors[1]))
        bg_colors = bg_colors / 255.0
        bg_vertex = [(-1, 1, 0.99), (-1, -1, 0.99), (1, -1, 0.99), (1, 1, 0.99)]
        bg_vertex_indices = [(0, 1, 3), (2, 3, 1)]
        bg_vertex = [bg_vertex[p] for index in bg_vertex_indices for p in index]
        bg_colors = [bg_colors[p] for index in bg_vertex_indices for p in index]
        bg_vertex_data = np.hstack([bg_vertex, bg_colors])
        self.bg_vertex_data = bg_vertex_data.astype(np.float16)


class SkyboxVbo:
    def __init__(self):
        bg_vertex = [(-1, 1, 0.999), (-1, -1, 0.999), (1, -1, 0.999), (1, 1, 0.999)]
        bg_vertex_indices = [(0, 1, 3), (2, 3, 1)]
        bg_vertex_data = [bg_vertex[p] for index in bg_vertex_indices for p in index]
        self.bg_vertex_data = np.asarray(bg_vertex_data, np.float16)


class IconVao:
    def __init__(self, ctx, program, vbo):
        self.vao = []
        for i in range(len(vbo)):
            self.vao.append(ctx.vertex_array(program, [
                (vbo[i], '4f2 2f2 4f2 4f2 4f2', 'vertexPos', 'texCoord', 'vertexColor', 'nextVertexPos', 'normal')]))


class BgVao:
    def __init__(self, ctx, program, vbo):
        self.vao = ctx.vertex_array(program, [(vbo, '3f2 4f2', 'vertexPos', 'vertexColor')])


class SkyboxVao:
    def __init__(self, ctx, program, vbo):
        self.vao = ctx.vertex_array(program, [(vbo, '3f2', 'vertexPos')])
