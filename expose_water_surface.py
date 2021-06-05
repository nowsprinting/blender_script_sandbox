import re

import bmesh
import bpy


def expose_water_surface(target_pattern=r"^\d+_dem_\d+$", edge_length=6.0):
    """
    PLATEAUモデルのdemから水面を削除する

    少なくとも横浜市（2020年度）のdemモデルでは
    - 水面に頂点はないが面が貼られている
    - 地面は5mごとに頂点がある
    となっていることから、6m以上の辺を削除すればよさそう

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


expose_water_surface()
