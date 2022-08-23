import pythreejs as THREE

base = THREE.Mesh(
    THREE.BoxBufferGeometry(20, 0.1, 20),
    THREE.MeshLambertMaterial(color='green', opacity=0.5, transparent=True),
    position=(0, 0, 0),
)
cube = THREE.Mesh(
    THREE.BoxBufferGeometry(10, 10, 10),
    THREE.MeshLambertMaterial(color='green', opacity=0.5, transparent=False),
    position=(0, 5, 0),
)

view_width = 800
view_height = 600
target = (0, 5, 0)
camera = THREE.CombinedCamera(position=[60, 60, 60], width=view_width, height=view_height)
camera.mode = 'orthographic'
camera.lookAt(target)
camera.zoom = 4
orbit = THREE.OrbitControls(controlling=camera, target=target)

lights = [
    THREE.PointLight(position=[100, 0, 0], color="#ffffff"),
    THREE.PointLight(position=[0, 100, 0], color="#bbbbbb"),
    THREE.PointLight(position=[0, 0, 100], color="#888888"),
    THREE.AmbientLight(intensity=0.2),
]

scene = THREE.Scene(children=[base, cube, camera] + lights)

renderer = THREE.Renderer(scene=scene, camera=camera, controls=[orbit],
                    width=view_width, height=view_height)


from ipywidgets import embed
snippet = embed.embed_snippet(views=renderer)
html = embed.html_template.format(title="", snippet=snippet)

import streamlit.components.v1 as components
components.html(html, width=view_width, height=view_height)
