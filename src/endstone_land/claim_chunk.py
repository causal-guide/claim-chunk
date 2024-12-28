from endstone.plugin import Plugin

from endstone.command import Command, CommandSender ,CommandSenderWrapper

from endstone import ColorFormat 
from endstone.form import ActionForm
import os
import json
import uuid
import math
from .land import LandManager
from datetime import datetime
from endstone.event import event_handler, BlockBreakEvent, BlockPlaceEvent, PlayerInteractEvent
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput
from endstone import ColorFormat


class ClaimChunk(Plugin):
  prefix = "ClaimChunk"
  api_version = "0.5"
  load = "POSTWORLD"
  
  def on_enable(self) -> None:
    self.register_events(self)
    
      # 事件监听器：玩家交互事件

    @event_handler

    def PlayerInteractEvent(self, event: PlayerInteractEvent):
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            event.player.send_message("领地文件不存在，无法检查领地权限！")
            return

        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)

        player_name = event.player.name
        block_x = math.floor(event.block.location.x)
        block_y = math.floor(event.block.location.y)
        block_z = math.floor(event.block.location.z)
        block_dimension = event.block.location.dimension.name
        #self.server.logger.info(f"block_xyz:{block_x} {block_y} {block_z} ,dim:{block_dimension}")

        # 遍历所有领地
        for owner, lands in land_data.items():
            for land in lands:
                for land_name, land_info in land.items():
                    posa = list(map(int, land_info["posa"].split(', ')))
                    posb = list(map(int, land_info["posb"].split(', ')))
                    dim = land_info["dim"]
                    #self.server.logger.info(f"{land_name}的信息:{posa[0]} {posa[1]} {posa[2]}到{posb[0]} {posb[1]} {posb[2]},维度{dim}")
                    
                    # 只检查与当前方块同维度的领地
                    if dim == block_dimension:
                        # 确定方块是否在该领地范围内
                        if (min(posa[0], posb[0]) <= block_x <= max(posa[0], posb[0]) and
                            min(posa[1], posb[1]) <= block_y <= max(posa[1], posb[1]) and
                            min(posa[2], posb[2]) <= block_z <= max(posa[2], posb[2])):
                            if land_info["permission"][0]["containter"] == "false" and player_name != owner and player_name not in land_info["member"]:
                                event.player.send_message(f"你不能在玩家 {owner} 的领地中进行任何右键")
                                event.cancelled = True
                                return
                            elif land_info["permission"][0]["containter"] == "true" and len(land_info.get("anti_right_click_block")) !=0 and player_name != owner and player_name not in land_info["member"]:
                                if event.block.type in land_info["anti_right_click_block"]:
                                    event.player.send_message(f"你不能在玩家 {owner} 的领地中右键操作{event.block.type}")
                                    event.cancelled = True
                                return


    # 事件监听器：方块放置事件
    @event_handler
    def BlockPlaceEvent(self, event: BlockPlaceEvent):
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            event.player.send_message("领地文件不存在，无法检查领地权限！")
            return

        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)

        player_name = event.player.name
        block_x = math.floor(event.block.location.x)
        block_y = math.floor(event.block.location.y)
        block_z = math.floor(event.block.location.z)
        block_dimension = event.block.location.dimension.name
        #self.server.logger.info(f"block_xyz:{block_x} {block_y} {block_z} ,dim:{block_dimension}")

        # 遍历所有领地
        for owner, lands in land_data.items():
            for land in lands:
                for land_name, land_info in land.items():
                    posa = list(map(int, land_info["posa"].split(', ')))
                    posb = list(map(int, land_info["posb"].split(', ')))
                    dim = land_info["dim"]
                    #self.server.logger.info(f"{land_name}的信息:{posa[0]} {posa[1]} {posa[2]}到{posb[0]} {posb[1]} {posb[2]},维度{dim}")
                    
                    # 只检查与当前方块同维度的领地
                    if dim == block_dimension:
                        # 确定方块是否在该领地范围内
                        if (min(posa[0], posb[0]) <= block_x <= max(posa[0], posb[0]) and
                            min(posa[1], posb[1]) <= block_y <= max(posa[1], posb[1]) and
                            min(posa[2], posb[2]) <= block_z <= max(posa[2], posb[2])):
                            
                            # 检查权限：如果 build 权限为 false 且玩家不是领主或成员
                            if land_info["permission"][1]["build"] == "false" and player_name != owner and player_name not in land_info["member"]:
                                event.player.send_message(f"你不能在玩家 {owner} 的领地中放置方块！")
                                event.cancelled = True
                                return    


    # 事件监听器：方块破坏事件
    @event_handler
    def BlockBreakEvent(self, event: BlockBreakEvent):
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            event.player.send_message("领地文件不存在，无法检查领地权限！")
            return

        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)

        player_name = event.player.name
        block_x = math.floor(event.block.location.x)
        block_y = math.floor(event.block.location.y)
        block_z = math.floor(event.block.location.z)
        block_dimension = event.block.location.dimension.name
        #self.server.logger.info(f"block_xyz:{block_x} {block_y} {block_z} ,dim:{block_dimension}")

        # 遍历所有领地
        for owner, lands in land_data.items():
            for land in lands:
                for land_name, land_info in land.items():
                    posa = list(map(int, land_info["posa"].split(', ')))
                    posb = list(map(int, land_info["posb"].split(', ')))
                    dim = land_info["dim"]
                    #self.server.logger.info(f"{land_name}的信息:{posa[0]} {posa[1]} {posa[2]}到{posb[0]} {posb[1]} {posb[2]},维度{dim}")
                    
                    # 只检查与当前方块同维度的领地
                    if dim == block_dimension:
                        # 确定方块是否在该领地范围内
                        if (min(posa[0], posb[0]) <= block_x <= max(posa[0], posb[0]) and
                            min(posa[1], posb[1]) <= block_y <= max(posa[1], posb[1]) and
                            min(posa[2], posb[2]) <= block_z <= max(posa[2], posb[2])):
                            
                            # 检查权限：如果 mine 权限为 false 且玩家不是领主或成员
                            if land_info["permission"][2]["mine"] == "false" and player_name != owner and player_name not in land_info["member"]:
                                event.player.send_message(f"你不能破坏玩家 {owner} 的领地中的方块！")
                                event.cancelled = True
                                return
