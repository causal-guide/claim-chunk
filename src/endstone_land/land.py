from endstone.plugin import Plugin
from endstone.command import Command, CommandSender ,CommandSenderWrapper
from endstone import ColorFormat 
from endstone.form import ActionForm
import os
import json
import uuid
import math
from datetime import datetime
from endstone.event import event_handler, BlockBreakEvent, BlockPlaceEvent, PlayerInteractEvent
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput
from endstone import ColorFormat

def transfer_land(land_file_path, user_from, user_to, land_name):
    """
    将 land_name 从 user_from 转移给 user_to。
    
    参数:
    land_file_path: 领地数据的文件路径
    user_from: 转出用户
    user_to: 转入用户
    land_name: 要转移的领地名称
    """
    # 读取 JSON 文件
    with open(land_file_path, 'r', encoding='utf-8') as f:
        land_data = json.load(f)
    
    # 检查源用户是否拥有该领地
    if user_from not in land_data:
        print(f"用户 {user_from} 不存在.")
        return
    
    # 查找源用户是否有该领地
    user_from_land = None
    for land_info in land_data[user_from]:
        if land_name in land_info:
            user_from_land = land_info[land_name]
            break
    
    if not user_from_land:
        print(f"用户 {user_from} 没有 {land_name} 领地.")
        return
    
    # 如果目标用户没有，则初始化目标用户数据
    if user_to not in land_data:
        land_data[user_to] = []
    
    # 将领地数据添加到目标用户
    land_data[user_to].append({land_name: user_from_land})
    
    # 从源用户删除该领地
    land_data[user_from] = [land for land in land_data[user_from] if land_name not in land]
    
    # 保存更新后的数据回 JSON 文件
    with open(land_file_path, 'w', encoding='utf-8') as f:
        json.dump(land_data, f, ensure_ascii=False, indent=4)
    
    print(f"领地 {land_name} 已成功从 {user_from} 转移给 {user_to}.")


# 定义检测长方体是否重合的函数
def no_intersection_between_cuboids(a, b, c, d, e, f, g, h, i, j, k, l):
    if max(a, d) < min(g, j) or max(g, j) < min(a, d):
        return True
    if max(b, e) < min(h, k) or max(h, k) < min(b, e):
        return True
    if max(c, f) < min(i, l) or max(i, l) < min(c, f):
        return True
    return False
class Land:
    def __init__(self, land:dict):
        self.name=list(land.keys())[0]
        land_info=list(land.values())[0]
        self.info=list(land.values())[0]
        self.posa=list(map(int, list(land.values())[0]["posa"].split(', ')))
        self.posb=list(map(int, list(land.values())[0]["posa"].split(', ')))
        self.dim=list(land.values())[0]["dim"]
        if list(land.values())[0]["dim"]=="Overworld":
            self.dim_index=0
        if list(land.values())[0]["dim"]=="Nether":
            self.dim_index=1
        if list(land.values())[0]["dim"]=="TheEnd":
            self.dim_index=2
        self.anti_right_click_block=land_info["anti_right_click_block"]
        self.arcb=land_info["anti_right_click_block"]
        self.member=land_info["member"]
        self.tppos=[land_info["tpposx"],land_info["tpposy"],land_info["tpposz"]]
        
        containterget=list(land.values())[0]["permission"][0]["containter"]
        containter_bool=containterget.lower()=="true"
        self.containter=containter_bool
        
        buildget=list(land.values())[0]["permission"][1]["build"]
        build_bool=buildget.lower()=="true"
        self.build=build_bool
        
        mineget=list(land.values())[0]["permission"][2]["mine"]
        mine_bool=mineget.lower()=="true"
        self.mine=mine_bool
        
        tpget=list(land.values())[0]["permission"][3]["tp"]
        tp_bool=tpget.lower()=="true"
        self.tp=tp_bool
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        self.fire=land_info["fire"]
        self.mobgriefing=land_info["mobgriefing"]
        self.explode=land_info["explode"]
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            print("领地文件不存在，无法检查领地权限！")
            return
        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
        for owner, lands in land_data.items():
            for oneland in lands:
                if land==oneland:
                    self.owner=owner
 
 
    from endstone.block import Block
    def landdata_to_Land(self,land:dict):
        return Land(land)
    
    def Block_to_landname(self, block:Block):
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            print("领地文件不存在，无法检查领地权限！")
            return
        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
        block_x = math.floor(block.location.x)
        block_y = math.floor(block.location.y)
        block_z = math.floor(block.location.z)
        block_dimension = block.location.dimension.name
        for owner, lands in land_data.items():
            for land in lands:
                for land_name, land_info in land.items():
                    posa = list(map(int, land_info["posa"].split(', ')))
                    posb = list(map(int, land_info["posb"].split(', ')))
                    dim = land_info["dim"]
                    if dim == block_dimension:
                        if (min(posa[0], posb[0]) <= block_x <= max(posa[0], posb[0]) and
                            min(posa[1], posb[1]) <= block_y <= max(posa[1], posb[1]) and
                            min(posa[2], posb[2]) <= block_z <= max(posa[2], posb[2])):
                                return land_name
                    else:
                        return None
                    
    from endstone import Player
    def Player_to_landname(self,player:Player) -> None:
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        if not os.path.exists(land_json_path):
            self.logger.info("领地文件不存在，无法检查领地信息！")
            return
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
        oneplayer = player
        player_x = math.floor(oneplayer.location.x)
        player_y = math.floor(oneplayer.location.y)
        player_z = math.floor(oneplayer.location.z)
        player_dim = oneplayer.location.dimension.name
        for owner, lands in land_data.items():
            for land in lands:
                for land_name, land_info in land.items():
                    posa = list(map(int, land_info["posa"].split(', ')))
                    posb = list(map(int, land_info["posb"].split(', ')))
                    land_dim = land_info["dim"]
                    #print(f"{player_dim},{player_x},{player_y},{player_z},{land_name},{str(posa)},{str(posb)},{land_dim}")
                    if player_dim == land_dim:
                        if (min(posa[0], posb[0]) <= player_x <= max(posa[0], posb[0]) and
                            min(posa[1], posb[1]) <= player_y <= max(posa[1], posb[1]) and
                            min(posa[2], posb[2]) <= player_z <= max(posa[2], posb[2])):
                            return land_name

    def landname_to_landdata(self, name:str):
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            print("领地文件不存在，无法检查领地权限！")
            return
        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
        for owner, lands in land_data.items():
            for land in lands:
                for land_name, land_info in land.items():
                    if name==land_name:
                        return land
    def landname_to_Land(self,name:str):
        landdata=self.landname_to_landdata(name)
        return self.landdata_to_Land(landdata)
##umaru写这里!
    def fire(self):
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            print("领地文件不存在，无法检查领地权限！")
            return
        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
            for owner, lands in land_data.items():
                for land in lands:
                    for land_name, land_info in land.items():
                        self.landname_to_Land(land_name).fire#fire权限开关
##umaru写这里!
    def explode(self):
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            print("领地文件不存在，无法检查领地权限！")
            return
        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
            for owner, lands in land_data.items():
                for land in lands:
                    for land_name, land_info in land.items():
                        self.landname_to_Land(land_name).explode#explode权限开关
                        
##umaru写这里!
    def mobgriefing(self):
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")
        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            print("领地文件不存在，无法检查领地权限！")
            return
        # 读取 land.json 文件
        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
            for owner, lands in land_data.items():
                for land in lands:
                    for land_name, land_info in land.items():
                        self.landname_to_Land(land_name).mobgriefing#mobgriefing权限开关



        self.register_events(self)
        current_dir = os.getcwd()
        self.land_dir = os.path.join(current_dir, "plugins", "land")
        self.money_dir = os.path.join(current_dir, "plugins", "money")
        self.land_file = os.path.join(self.land_dir, "land.json")
        self.config_file = os.path.join(self.land_dir, "config.json")
        self.money_file = os.path.join(self.money_dir, "money.json")

        # 如果 land.json 不存在，创建空的文件
        if not os.path.exists(self.land_file):
            os.makedirs(self.land_dir, exist_ok=True)
            with open(self.land_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        
        # 如果 config.json 不存在，创建默认配置
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w', encoding='utf-8') as f:
                # 默认值为 {"price": 1, "money": "json"}
                json.dump({"price": 1, "money": "json"}, f, ensure_ascii=False, indent=4)
        
        # 读取配置文件
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 读取地块单价和 money 类型（json 或 economyapi）
        self.price_per_block = config_data.get("price", 1)
        self.money_type = config_data.get("money", "json")  # 默认为 json

        # 日志信息
        self.logger.info(f"{ColorFormat.YELLOW}领地插件已启用！配置文件位于: {self.land_file}")
        self.logger.info(f"{ColorFormat.YELLOW}领地价格配置文件位于: {self.config_file}")
        self.logger.info(f"{ColorFormat.YELLOW}玩家金钱文件位于: {self.money_file}")

        # 周期性任务
        self.server.scheduler.run_task(self, self.landinfo, delay=0, period=20)
        import os
        import json

        # 获取领地文件的路径
        land_file_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")

        # 读取 JSON 文件
        with open(land_file_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)

        # 遍历所有用户的领地数据，并确保每个领地都包含 "anti_right_click_block"
        for user_data in land_data.values():
            for land_info in user_data:
                for land_name, details in land_info.items():
                    # 如果没有 anti_right_click_block 键，设置为一个空列表
                    details.setdefault("anti_right_click_block", [])
                    details.setdefault("fire", False)
                    details.setdefault("explode", False)
                    details.setdefault("mobgriefing", False)
        # 将修改后的数据写回到 JSON 文件
        with open(land_file_path, 'w', encoding='utf-8') as f:
            json.dump(land_data, f, ensure_ascii=False, indent=4)

        print("领地数据已更新，'anti_right_click_block' fire explode mobgriefing 已初始化。")



    def landinfo(self) -> None:
        land_json_path = os.path.join(os.getcwd(), "plugins", "land", "land.json")

        # 检查 land.json 文件是否存在
        if not os.path.exists(land_json_path):
            self.logger.info("领地文件不存在，无法检查领地信息！")
            return

        with open(land_json_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)

        # 遍历所有在线玩家
        for oneplayer in self.server.online_players:
            player_x = math.floor(oneplayer.location.x)
            player_y = math.floor(oneplayer.location.y)
            player_z = math.floor(oneplayer.location.z)
            player_dim = oneplayer.location.dimension.name

            # 默认提示信息（表示未在领地中）
            found_land = False

            for owner, lands in land_data.items():
                for land in lands:
                    for land_name, land_info in land.items():
                        posa = list(map(int, land_info["posa"].split(', ')))
                        posb = list(map(int, land_info["posb"].split(', ')))
                        land_dim = land_info["dim"]

                        if player_dim == land_dim:
                            # 判断玩家是否在领地范围内
                            if (min(posa[0], posb[0]) <= player_x <= max(posa[0], posb[0]) and
                                min(posa[1], posb[1]) <= player_y <= max(posa[1], posb[1]) and
                                min(posa[2], posb[2]) <= player_z <= max(posa[2], posb[2])):
                                
                                # 设置找到领地的标志
                                found_land = True

                                player_name = oneplayer.name
                                message = f'§l§b你现在在§1§e{owner}§b的领地§e{land_name}§b上'.replace(" ","")
                                self.server.get_player(player_name).send_tip(message)
                                #cmdreturn = self.server.dispatch_command(CommandSenderWrapper(self.server.command_sender), 
                                #                                        f'title {player_name} actionbar {message}')
                                #if not cmdreturn:
                                #    self.server.dispatch_command(CommandSenderWrapper(self.server.command_sender), 
                                #                                f'title {player_name} actionbar §l§b你现在在一个领地上')
                                break  # 找到领地后不再遍历，继续下一个玩家
                    if found_land:
                        break
                if found_land:
                    break


    


    def get_all_land_names(self):
        if os.path.exists(self.land_file):
            with open(self.land_file, 'r', encoding='utf-8') as f:
                land_data = json.load(f)

            all_land_names = []

            # 遍历所有玩家的领地
            for player, lands in land_data.items():
                for land in lands:
                    # 提取领地的名字，假设每个领地都是字典，键为领地名称
                    land_name = list(land.keys())[0]
                    all_land_names.append(land_name)

            return all_land_names
        else:
            print("找不到 land.json 文件")
            return []



class LandManager:
    def __init__(self):
        current_dir = os.getcwd()
        self.land_dir = os.path.join(current_dir, "plugins", "land")
        self.money_dir = os.path.join(current_dir, "plugins", "money")
        self.land_file = os.path.join(self.land_dir, "land.json")
        self.money_file = os.path.join(self.money_dir, "money.json")
        self.config_file = os.path.join(self.land_dir, "config.json")
        self.price_per_block = 1
        self.money_type = "json"

        os.makedirs(self.land_dir, exist_ok=True)
        os.makedirs(self.money_dir, exist_ok=True)
        if not os.path.exists(self.land_file):
            with open(self.land_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        if not os.path.exists(self.money_file):
            with open(self.money_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({"price": 1, "money": "json"}, f, ensure_ascii=False, indent=4)

        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            self.price_per_block = config_data.get("price", 1)
            self.money_type = config_data.get("money", "json")

    @staticmethod
    def no_intersection_between_cuboids(a, b, c, d, e, f, g, h, i, j, k, l):
        return (
            max(a, d) < min(g, j) or max(g, j) < min(a, d) or
            max(b, e) < min(h, k) or max(h, k) < min(b, e) or
            max(c, f) < min(i, l) or max(i, l) < min(c, f)
        )

    # Buy Land
    def buy_land(self, player_name, posa, posb, dimension, land_name=None):
        buy_posa_x, buy_posa_y, buy_posa_z = posa
        buy_posb_x, buy_posb_y, buy_posb_z = posb
        dx = abs(buy_posa_x - buy_posb_x) + 1
        dy = abs(buy_posa_y - buy_posb_y) + 1
        dz = abs(buy_posa_z - buy_posb_z) + 1
        total_blocks = dx * dy * dz
        total_price = total_blocks * self.price_per_block

        with open(self.money_file, 'r', encoding='utf-8') as f:
            money_data = json.load(f)
        player_money = money_data.get(player_name, 0)
        if player_money < total_price:
            return f"Not enough money! Required: {total_price}, Available: {player_money}"

        money_data[player_name] = player_money - total_price
        with open(self.money_file, 'w', encoding='utf-8') as f:
            json.dump(money_data, f, ensure_ascii=False, indent=4)

        with open(self.land_file, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
        for owner, lands in land_data.items():
            for land in lands:
                for _, land_info in land.items():
                    posa_x, posa_y, posa_z = map(int, land_info["posa"].split(", "))
                    posb_x, posb_y, posb_z = map(int, land_info["posb"].split(", "))
                    if not self.no_intersection_between_cuboids(
                        buy_posa_x, buy_posa_y, buy_posa_z, buy_posb_x, buy_posb_y, buy_posb_z,
                        posa_x, posa_y, posa_z, posb_x, posb_y, posb_z
                    ):
                        if land_info.get("dim") == dimension:
                            return f"Purchase failed! Overlaps with {owner}'s land."

        land_name = land_name or datetime.now().strftime("%Y%m%d%H%M%S")
        new_land = {
            land_name: {
                "posa": f"{buy_posa_x}, {buy_posa_y}, {buy_posa_z}",
                "posb": f"{buy_posb_x}, {buy_posb_y}, {buy_posb_z}",
                "dim": dimension,
                "member": [],
                "anti_right_click_block": [],
                "permission": [
                    {"containter": "false"},
                    {"build": "false"},
                    {"mine": "false"},
                    {"tp": "false"},
                ],
                "mobgriefing": False,
                "fire": False,
                "explode": False,
            }
        }
        if player_name in land_data:
            land_data[player_name].append(new_land)
        else:
            land_data[player_name] = [new_land]

        with open(self.land_file, 'w', encoding='utf-8') as f:
            json.dump(land_data, f, ensure_ascii=False, indent=4)
        return f"Land '{land_name}' purchased successfully for {total_price} units."

    # Add or Remove Members
    def manage_member(self, player_name, land_name, target_player, action):
        with open(self.land_file, 'r', encoding='utf-8') as f:
            land_data = json.load(f)

        if player_name in land_data:
            for land in land_data[player_name]:
                if land_name in land:
                    members = land[land_name]["member"]
                    if action == "add":
                        if target_player not in members:
                            members.append(target_player)
                            with open(self.land_file, 'w', encoding='utf-8') as f:
                                json.dump(land_data, f, ensure_ascii=False, indent=4)
                            return f"{target_player} added to land '{land_name}'."
                        return f"{target_player} is already a member."
                    elif action == "remove":
                        if target_player in members:
                            members.remove(target_player)
                            with open(self.land_file, 'w', encoding='utf-8') as f:
                                json.dump(land_data, f, ensure_ascii=False, indent=4)
                            return f"{target_player} removed from land '{land_name}'."
                        return f"{target_player} is not a member."
        return f"Land '{land_name}' not found or you don't have permission."

    # List Members
    def list_members(self, player_name, land_name):
        with open(self.land_file, 'r', encoding='utf-8') as f:
            land_data = json.load(f)

        if player_name in land_data:
            for land in land_data[player_name]:
                if land_name in land:
                    members = land[land_name]["member"]
                    return f"Members of '{land_name}': {', '.join(members)}"
        return f"Land '{land_name}' not found or you don't have permission."

    # Manage Permissions
    def manage_permission(self, player_name, land_name, permission_type, value):
        valid_permissions = ["containter", "build", "mine", "tp"]
        if permission_type not in valid_permissions:
            return f"Invalid permission type. Use one of: {', '.join(valid_permissions)}."

        with open(self.land_file, 'r', encoding='utf-8') as f:
            land_data = json.load(f)

        if player_name in land_data:
            for land in land_data[player_name]:
                if land_name in land:
                    permission_index = valid_permissions.index(permission_type)
                    land[land_name]["permission"][permission_index][permission_type] = value
                    with open(self.land_file, 'w', encoding='utf-8') as f:
                        json.dump(land_data, f, ensure_ascii=False, indent=4)
                    return f"Permission '{permission_type}' for '{land_name}' set to {value}."
        return f"Land '{land_name}' not found or you don't have permission."
