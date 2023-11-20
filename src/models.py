import glm
import numpy as np
import utils


class Camera:
    """
    A camera class providing the view space.
    """

    FOV = 50
    NEAR = 0.1
    FAR = 100

    def __init__(self, win_size):
        self.aspect_ratio = win_size[0] / win_size[1]
        self.position = glm.vec3(0, -4.0, -10)
        self.up = glm.vec3(0, -1, 0)
        self.view = glm.lookAt(self.position, glm.vec3(0, -2, 0), self.up)
        self.proj = glm.perspective(
            glm.radians(Camera.FOV), self.aspect_ratio, Camera.NEAR, Camera.FAR
        )


class IconModel:
    """
    Vertex data for the 3D icon.
    """
    __FIXED_POINT_FACTOR = 4096.0

    def __init__(self, ctx, program, icon):
        self.vbos = []
        self._vaos = []
        for i in range(icon.animation_shapes):
            h = i + 1
            if h >= icon.animation_shapes:
                h = 0
            vertex_data = np.hstack(
                (
                    icon.vertex_data[..., i, :3],
                    icon.vertex_data[..., h, :3],
                    icon.uv_data,
                    icon.normal_data[..., :3],
                )
            )
            vertex_data /= IconModel.__FIXED_POINT_FACTOR
            vertex_data = vertex_data.astype("f2")
            self.vbos.append(ctx.buffer(vertex_data))
            self._vaos.append(
                ctx.vertex_array(
                    program["icon"],
                    [
                        (
                            self.vbos[i],
                            "3f2 3f2 2f2 3f2",
                            "vertexPos",
                            "nextVertexPos",
                            "texCoord",
                            "normal",
                        )
                    ],
                )
            )

        texture_data = icon.texture
        self.texture = None
        if texture_data is not None:
            self.texture = ctx.texture(size=(128, 128), data=texture_data, components=3)
            self.texture.use()

    def vao(self, n):
        return self._vaos[n]

    def release(self):
        [vbo.release() for vbo in self.vbos]
        [vao.release() for vao in self._vaos]
        if self.texture is not None:
            self.texture.release()


class BgModel:
    """
    Vertex data for the background.
    """
    __FIXED_COLOR_FACTOR = 255.0
    __FIXED_ALPHA_FACTOR = 128.0

    def __init__(self, ctx, program, icon_sys):
        self.ctx = ctx
        self.program = program
        alpha = icon_sys.background_transparency / BgModel.__FIXED_ALPHA_FACTOR
        alpha = np.full((4, 1), fill_value=alpha)
        bg_colors = icon_sys.bg_colors
        bg_colors = np.asarray(
            (bg_colors[0][:3], bg_colors[2][:3], bg_colors[3][:3], bg_colors[1][:3])
        )
        bg_colors = bg_colors / BgModel.__FIXED_COLOR_FACTOR
        bg_colors = np.hstack([bg_colors, alpha])
        bg_vertex = [(-1, 1, 0.99), (-1, -1, 0.99), (1, -1, 0.99), (1, 1, 0.99)]
        bg_vertex_indices = [(0, 1, 3), (2, 3, 1)]
        bg_vertex = [bg_vertex[p] for index in bg_vertex_indices for p in index]
        bg_colors = [bg_colors[p] for index in bg_vertex_indices for p in index]
        bg_vertex_data = np.hstack([bg_vertex, bg_colors])
        skybox_vertex = [(-1, 1, 0.999), (-1, -1, 0.999), (1, -1, 0.999), (1, 1, 0.999)]
        skybox_colors = [
            (0.6, 0.6, 0.6, 1),
            (0.6, 0.6, 0.6, 1),
            (0.6, 0.6, 0.6, 1),
            (0.6, 0.6, 0.6, 1),
        ]
        skybox_vertex = [skybox_vertex[p] for index in bg_vertex_indices for p in index]
        skybox_colors = [skybox_colors[p] for index in bg_vertex_indices for p in index]
        skybox_vertex_data = np.hstack([skybox_vertex, skybox_colors])
        vertex_data = np.vstack([skybox_vertex_data, bg_vertex_data])
        self.vbo = self.ctx.buffer(vertex_data.astype("f2"))
        self._vao = self.ctx.vertex_array(
            self.program["bg"], [(self.vbo, "3f2 4f2", "vertexPos", "vertexColor")]
        )

    def vao(self):
        return self._vao

    def release(self):
        self.vbo.release()
        self._vao.release()


class CircleModel:
    """
    Vertex data for the action button.
    """

    def __init__(self, ctx, program, n):
        self.ctx = ctx
        self.program = program
        self.vbos = []
        self._vaos = []
        self.circle_centers = utils.circle_centers(n)
        if self.circle_centers:
            for circle_center in self.circle_centers:
                vertex_data = utils.circle_data(circle_center)
                vbo = self.ctx.buffer(vertex_data)
                self.vbos.append(vbo)
                self._vaos.append(self.ctx.simple_vertex_array(self.program["circle"], vbo, "vertexPos"))

    def circle_centers(self):
        return self.circle_centers

    def vaos(self):
        return self._vaos

    def release(self):
        [vbo.release() for vbo in self.vbos]
        [vao.release() for vao in self._vaos]
