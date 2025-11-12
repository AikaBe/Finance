# open3d_assignment.py
import open3d as o3d
import numpy as np
import copy
import os

model_path = "gltf\Wolf-Blender-2.82a.gltf" 

def print_mesh_info(mesh, label="Mesh"):
    v = np.asarray(mesh.vertices).shape[0]
    t = np.asarray(mesh.triangles).shape[0] if len(mesh.triangles) > 0 else 0
    has_colors = mesh.has_vertex_colors()
    has_normals = mesh.has_vertex_normals()
    print(f"\n--- {label} ---")
    print(f"Vertices (points): {v}")
    print(f"Triangles: {t}")
    print(f"Has vertex colors: {has_colors}")
    print(f"Has vertex normals: {has_normals}")

def print_pcd_info(pcd, label="PointCloud"):
    v = np.asarray(pcd.points).shape[0]
    has_colors = pcd.has_colors()
    has_normals = pcd.has_normals()
    print(f"\n--- {label} ---")
    print(f"Points: {v}")
    print(f"Has colors: {has_colors}")
    print(f"Has normals: {has_normals}")

def print_voxel_info(vg, label="VoxelGrid"):
    voxels = len(vg.get_voxels())
    print(f"\n--- {label} ---")
    print(f"Voxels count: {voxels}")

# 1) Загрузка и визуализация 
print("1) Loading mesh...")
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Файл не найден: {model_path}. Укажи правильный путь.")

mesh = o3d.io.read_triangle_mesh(model_path)
if mesh is None or len(mesh.vertices) == 0:
    raise RuntimeError("Не удалось загрузить mesh. Убедись, что формат поддерживается и файлы (bin/текстуры) находятся рядом с gltf.")
if not mesh.has_vertex_normals():
    mesh.compute_vertex_normals()

print_mesh_info(mesh, label="Исходная модель (mesh)")

o3d.visualization.draw_geometries([mesh], window_name="1 - Исходная модель (mesh)")

# 2) Преобразование в облако точек 
print("\n2) Преобразование в point cloud (через промежуточное сохранение и o3d.io.read_point_cloud)...")
num_points = 200000  
pc_from_mesh = mesh.sample_points_poisson_disk(number_of_points=min(num_points, max(1000, len(mesh.vertices)*10)))
temp_ply = "temp_sampled_cloud.ply"
o3d.io.write_point_cloud(temp_ply, pc_from_mesh)
pc = o3d.io.read_point_cloud(temp_ply)
print_pcd_info(pc, label="Point cloud (после o3d.io.read_point_cloud)")

o3d.visualization.draw_geometries([pc], window_name="2 - Облако точек (pc)")

# 3) Реконструкция поверхности из облака точек (Poisson)
print("\n3) Poisson reconstruction из облака точек...")
if not pc.has_normals():
    print(" - Нормали отсутствуют у point cloud: вычисляем нормали.")
    pc.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.05, max_nn=30))
with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
    mesh_poisson, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pc, depth=9)

print(" - Всего вершин/треуголов в Poisson mesh (перед очисткой):",
      len(mesh_poisson.vertices), len(mesh_poisson.triangles))

bbox = mesh.get_axis_aligned_bounding_box()
try:
    mesh_poisson_crop = mesh_poisson.crop(bbox)
    mesh_poisson_crop.remove_unreferenced_vertices()
    mesh_poisson_crop.remove_degenerate_triangles()
    mesh_poisson_crop.compute_vertex_normals()
    mesh_poisson = mesh_poisson_crop
except Exception as e:
    print(" - Warning: не удалось использовать mesh.crop(bbox) — попробуем фильтрацию по плотности.")
    densities = np.asarray(densities)
    density_thresh = np.quantile(densities, 0.01)
    vertices_to_keep = densities > density_thresh
    mesh_poisson.remove_vertices_by_mask(~vertices_to_keep)
    mesh_poisson.remove_unreferenced_vertices()
    mesh_poisson.compute_vertex_normals()

print_mesh_info(mesh_poisson, label="Реконструированный mesh (Poisson, после очистки)")
o3d.visualization.draw_geometries([mesh_poisson], window_name="3 - Реконструированный объект (Poisson)")

# 4) Вокселизация
print("\n4) Вокселизация point cloud -> VoxelGrid")
voxel_size = 0.05 
vg = o3d.geometry.VoxelGrid.create_from_point_cloud(pc, voxel_size=voxel_size)
print_voxel_info(vg, label=f"VoxelGrid (voxel_size={voxel_size})")

o3d.visualization.draw_geometries([vg], window_name="4 - Воксели (VoxelGrid)")

# 5) Добавление плоскости 
print("\n5) Создаём плоскость и размещаем рядом с объектом")
plane = o3d.geometry.TriangleMesh.create_box(width=5.0, height=0.01, depth=5.0)
plane.compute_vertex_normals()
mesh_center = mesh.get_center()
bbox_mesh = mesh.get_axis_aligned_bounding_box()
min_z = bbox_mesh.get_min_bound()[2]
plane.translate(mesh_center - plane.get_center())  
plane.translate((0.0, 0.0, min_z - 0.02))
plane.paint_uniform_color([0.7, 0.7, 0.7])

o3d.visualization.draw_geometries([mesh, plane], window_name="5 - Модель + плоскость")

# 6) Обрезка по поверхности (клиппинг)
print("\n6) Клиппинг: удаляем точки правее (по одну сторону) плоскости")

n = np.mean(np.asarray(plane.vertex_normals), axis=0)
n = n / np.linalg.norm(n)
p0 = plane.get_center()
points = np.asarray(pc.points)
dots = (points - p0) @ n
keep_mask = dots <= 0  
indices_keep = np.where(keep_mask)[0]
pc_clipped = pc.select_by_index(indices_keep.tolist())
print_pcd_info(pc_clipped, label="Point cloud после клиппинга")
mesh_for_clip = copy.deepcopy(mesh_poisson)  
verts = np.asarray(mesh_for_clip.vertices)
dots_mesh = (verts - p0) @ n
mask_remove = dots_mesh > 0
try:
    mesh_for_clip.remove_vertices_by_mask(mask_remove)
    mesh_for_clip.remove_unreferenced_vertices()
    mesh_for_clip.remove_degenerate_triangles()
    mesh_for_clip.compute_vertex_normals()
except Exception as e:
    print(" - Warning: remove_vertices_by_mask не сработал как ожидалось:", e)
    if np.asarray(pc_clipped.points).shape[0] > 50:
        mesh_for_clip, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pc_clipped, depth=8)
        mesh_for_clip.remove_unreferenced_vertices()
        mesh_for_clip.compute_vertex_normals()

print_mesh_info(mesh_for_clip, label="Mesh после клиппинга")
o3d.visualization.draw_geometries([mesh_for_clip], window_name="6 - Модель после клиппинга")

# 7) Работа с цветом и экстремумами
print("\n7) Работа с цветом: убираем исходные цвета и задаём градиент по выбранной оси.")
target_mesh = mesh_for_clip if len(mesh_for_clip.vertices) > 0 else mesh
verts = np.asarray(target_mesh.vertices)
if len(verts) == 0:
    raise RuntimeError("Нет вершин для задания цвета / поиска экстремумов.")

axis = 0 
coords = verts[:, axis]
min_val = coords.min()
max_val = coords.max()
if max_val - min_val == 0:
    norm = np.zeros_like(coords)
else:
    norm = (coords - min_val) / (max_val - min_val)

colors = np.zeros((len(norm), 3))
colors[:, 0] = norm      
colors[:, 2] = 1.0 - norm
target_mesh.vertex_colors = o3d.utility.Vector3dVector(colors)

min_idx = int(np.argmin(coords))
max_idx = int(np.argmax(coords))
min_pt = verts[min_idx]
max_pt = verts[max_idx]
print(f"\nExtremums along axis {axis}:")
print("Min coord:", min_pt)
print("Max coord:", max_pt)

s_min = o3d.geometry.TriangleMesh.create_sphere(radius=(max_val-min_val)*0.02 if max_val!=min_val else 0.01)
s_min.compute_vertex_normals()
s_min.paint_uniform_color([0.0, 1.0, 0.0])  
s_min.translate(min_pt)

s_max = o3d.geometry.TriangleMesh.create_sphere(radius=(max_val-min_val)*0.02 if max_val!=min_val else 0.01)
s_max.compute_vertex_normals()
s_max.paint_uniform_color([1.0, 0.0, 0.0])
s_max.translate(max_pt)

o3d.visualization.draw_geometries([target_mesh, s_min, s_max], window_name="7 - Градиент + экстремумы")

print("\n--- Итог ---")
print_mesh_info(target_mesh, label="Итоговый mesh")
print("Координаты экстремумов:")
print("Min:", min_pt)
print("Max:", max_pt)

o3d.io.write_triangle_mesh("result_mesh.ply", target_mesh)
o3d.io.write_point_cloud("result_pcd.ply", pc_clipped)
print("\nСохранены result_mesh.ply и result_pcd.ply.")
