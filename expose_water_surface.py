import re

import bmesh
import bpy


def expose_water_surface(target_pattern=r"^\d+_dem_\d+$", edge_length=20.0):
    """
    PLATEAUモデルのdemから水面を削除する

    少なくとも横浜市（2020年度）のdemモデルでは
    - 水面に頂点はないが面が貼られている
    - 地面は5mごとに頂点がある
    となっていることから、8m以上の辺を削除すればよさそう。ただしある程度は丸めたいのでしきい値は大きめ

    参考: https://bluebirdofoz.hatenablog.com/entry/2020/05/08/201030

    :param target_pattern: 対象オブジェクト名パターン（正規表現）
    :param edge_length: この長さ以上の辺を削除対象とする
    """

    for obj in bpy.context.scene.objects:
        obj.select_set(False)  # 一旦すべて非選択にする

    pattern = re.compile(target_pattern)
    for obj in bpy.context.scene.objects:
        if not pattern.match(obj.name):
            continue

        print("Found dem object: {}".format(obj.name))
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        mesh = bmesh.from_edit_mesh(obj.data)
        mesh.select_mode = {'EDGE'}
        bpy.ops.mesh.select_all(action='DESELECT')
        mesh.select_flush_mode()
        mesh.verts.ensure_lookup_table()

        remove_count = 0
        for edge in mesh.edges:
            if edge.calc_length() >= edge_length:
                mesh.edges.remove(edge)
                remove_count += 1

        print("Remove {} edges from {}".format(remove_count, obj.name))
        mesh.select_flush_mode()
        obj.data.update()

    return


def cleanup_isolated_vertices(target_pattern=r"^\d+_dem_\d+$"):
    """
    水面を削除した後、demに残った孤立頂点を削除する

    参考: https://bluebirdofoz.hatenablog.com/entry/2020/01/03/220637

    :param target_pattern: 対象オブジェクト名パターン（正規表現）
    :return:
    """

    for obj in bpy.context.scene.objects:
        obj.select_set(False)  # 一旦すべて非選択にする

    pattern = re.compile(target_pattern)
    for obj in bpy.context.scene.objects:
        if not pattern.match(obj.name):
            continue

        print("Found dem object: {}".format(obj.name))
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)  # 大きさ0を融解（結合距離 0.0001）

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)  # 孤立を削除（頂点、辺のみ）

        bpy.ops.mesh.select_all()
        bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)  # 重複頂点を削除（結合距離 0.0001、非選択部の結合無効）

    return


expose_water_surface()
cleanup_isolated_vertices()
