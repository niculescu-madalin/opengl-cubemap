import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image
from camera import FirstPersonCamera
import os
import math


def load_texture(filename):
    """Load an image file as an OpenGL texture"""
    try:
        img = Image.open(filename)
        img_data = np.array(list(img.getdata()), np.uint8)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        return texture_id
    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
        return None


def create_skybox(size=100.0):
    """Create vertices and texture coordinates for a skybox cube"""
    vertices = [
        # Front face
        [-size, -size, size], [size, -size, size], [size, size, size], [-size, size, size],
        # Back face
        [-size, -size, -size], [-size, size, -size], [size, size, -size], [size, -size, -size],
        # Left face
        [-size, -size, -size], [-size, -size, size], [-size, size, size], [-size, size, -size],
        # Right face
        [size, -size, size], [size, -size, -size], [size, size, -size], [size, size, size],
        # Top face
        [-size, size, size], [size, size, size], [size, size, -size], [-size, size, -size],
        # Bottom face
        [-size, -size, size], [-size, -size, -size], [size, -size, -size], [size, -size, size]
    ]

    # Texture coordinates for each face
    tex_coords = [
        # Front face
        [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0],
        # Back face
        [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0],
        # Left face
        [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0],
        # Right face
        [1.0, 0.0], [0.0, 0.0], [0.0, 1.0], [1.0, 1.0],
        # Top face
        [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0],
        # Bottom face
        [0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]
    ]

    return vertices, tex_coords


def create_ground(size=50.0, y=-0.5):
    """Create a flat ground plane with grass texture"""
    vertices = [
        [-size, y, -size], [size, y, -size], [size, y, size], [-size, y, size]
    ]

    tex_coords = [
        [0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]
    ]

    normals = [
        [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 0.0]
    ]

    return vertices, tex_coords, normals


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Grass Platform with First-Person Camera")

    # Set up the camera
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)

    # Enable textures and depth testing
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.8, 0.8, 1])

    # Create skybox
    vertices, tex_coords = create_skybox()

    skybox_textures = []
    texture_paths = [
        "assets/skybox/posx.jpg", "assets/skybox/negx.jpg", "assets/skybox/posz.jpg",
        "assets/skybox/negz.jpg", "assets/skybox/posy.jpg", "assets/skybox/negy.jpg"
    ]

    for i, path in enumerate(texture_paths):
        texture = load_texture(path)
        if texture:
            skybox_textures.append(texture)
        else:
            print(f"Texture {path} not found, using color face instead")
            skybox_textures.append(None)

    # Create ground
    ground_vertices, ground_tex_coords, ground_normals = create_ground()
    grass_texture = load_texture("assets/grass.jpg")  # You'll need a grass texture

    # Initialize camera
    camera = FirstPersonCamera(position=[0, 0, 0])

    # Hide mouse and capture it
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # Main game loop
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_w:
                    camera.move_forward = True
                elif event.key == pygame.K_s:
                    camera.move_backward = True
                elif event.key == pygame.K_a:
                    camera.move_left = True
                elif event.key == pygame.K_d:
                    camera.move_right = True
                elif event.key == pygame.K_SPACE:
                    camera.move_up = True
                elif event.key == pygame.K_LSHIFT:
                    camera.move_down = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    camera.move_forward = False
                elif event.key == pygame.K_s:
                    camera.move_backward = False
                elif event.key == pygame.K_a:
                    camera.move_left = False
                elif event.key == pygame.K_d:
                    camera.move_right = False
                elif event.key == pygame.K_SPACE:
                    camera.move_up = False
                elif event.key == pygame.K_LSHIFT:
                    camera.move_down = False
            elif event.type == pygame.MOUSEMOTION:
                # Get mouse movement
                rel_x, rel_y = event.rel
                camera.yaw += rel_x * camera.mouse_sensitivity
                camera.pitch -= rel_y * camera.mouse_sensitivity
                # Clamp pitch to avoid gimbal lock
                camera.pitch = max(-89, min(89, camera.pitch))

        # Update camera position
        camera.update()

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Reset the modelview matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Apply camera transformation
        camera.look()

        # Draw the skybox
        glDepthMask(GL_FALSE)  # Disable writing to depth buffer for skybox
        for i in range(6):  # 6 faces
            if skybox_textures[i]:
                glBindTexture(GL_TEXTURE_2D, skybox_textures[i])
            else:
                glDisable(GL_TEXTURE_2D)
                colors = [
                    (1.0, 0.5, 0.5), (0.5, 0.5, 1.0), (0.5, 1.0, 0.5),
                    (1.0, 1.0, 0.5), (0.5, 1.0, 1.0), (1.0, 0.5, 1.0)
                ]
                glColor3fv(colors[i])

            glBegin(GL_QUADS)
            for j in range(4):
                idx = i * 4 + j
                if skybox_textures[i]:
                    glTexCoord2fv(tex_coords[idx])
                glVertex3fv(vertices[idx])
            glEnd()

            if not skybox_textures[i]:
                glEnable(GL_TEXTURE_2D)
                glColor3f(1.0, 1.0, 1.0)
        glDepthMask(GL_TRUE)  # Re-enable depth buffer writing

        # Draw the ground
        if grass_texture:
            glBindTexture(GL_TEXTURE_2D, grass_texture)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor3f(0.0, 0.6, 0.0)  # Green color for ground

        glBegin(GL_QUADS)
        for i in range(4):
            if grass_texture:
                glTexCoord2fv(ground_tex_coords[i])
            glNormal3fv(ground_normals[i])
            glVertex3fv(ground_vertices[i])
        glEnd()

        if not grass_texture:
            glEnable(GL_TEXTURE_2D)
            glColor3f(1.0, 1.0, 1.0)

        pygame.display.flip()
        clock.tick(60)

    # Clean up
    pygame.quit()


if __name__ == "__main__":
    main()