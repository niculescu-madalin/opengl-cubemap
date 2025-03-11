import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image
import os


def load_texture(filename):
    """Load an image file as an OpenGL texture"""
    try:
        img = Image.open(filename)
        img_data = np.array(list(img.getdata()), np.uint8)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

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


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("prezentare1")

    # Set up the camera
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 0, 0, 0, -1, 0, 1, 0)

    # Enable textures
    glEnable(GL_TEXTURE_2D)

    # Create skybox
    vertices, tex_coords = create_skybox()

    skybox_textures = []

    # texture paths
    texture_paths = [
        "skybox/posx.jpg", "skybox/negx.jpg", "skybox/posz.jpg",
        "skybox/negz.jpg", "skybox/negy.jpg", "skybox/posy.jpg"
    ]

    for i, path in enumerate(texture_paths):
        texture = load_texture(path)
        if texture:
            skybox_textures.append(texture)
        else:
            print(f"Texture {path} not found, using color face instead")
            skybox_textures.append(None)

    # Camera position and rotation
    camera_pos = [0, 0, 0]
    yaw = 0
    pitch = 180

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

        # Handle keyboard input for camera movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            yaw += 1
        if keys[pygame.K_RIGHT]:
            yaw -= 1
        if keys[pygame.K_UP]:
            pitch -= 1
        if keys[pygame.K_DOWN]:
            pitch += 1

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Reset the modelview matrix
        glLoadIdentity()

        # Apply camera rotation
        glRotatef(pitch, 1, 0, 0)
        glRotatef(yaw, 0, 1, 0)

        # Draw the skybox
        for i in range(6):  # 6 faces
            if skybox_textures[i]:
                glBindTexture(GL_TEXTURE_2D, skybox_textures[i])
            else:
                # If texture not loaded, use a solid color
                glDisable(GL_TEXTURE_2D)
                colors = [
                    (1.0, 0.5, 0.5),  # Front - Light Red
                    (0.5, 0.5, 1.0),  # Back - Light Blue
                    (0.5, 1.0, 0.5),  # Left - Light Green
                    (1.0, 1.0, 0.5),  # Right - Light Yellow
                    (0.5, 1.0, 1.0),  # Top - Light Cyan
                    (1.0, 0.5, 1.0)  # Bottom - Light Magenta
                ]
                glColor3fv(colors[i])

            # Draw the face as a quad
            glBegin(GL_QUADS)
            for j in range(4):
                idx = i * 4 + j
                if skybox_textures[i]:
                    glTexCoord2fv(tex_coords[idx])
                glVertex3fv(vertices[idx])
            glEnd()

            if not skybox_textures[i]:
                glEnable(GL_TEXTURE_2D)
                glColor3f(1.0, 1.0, 1.0)  # Reset color

        pygame.display.flip()
        clock.tick(60)

    # Clean up
    pygame.quit()


if __name__ == "__main__":
    main()