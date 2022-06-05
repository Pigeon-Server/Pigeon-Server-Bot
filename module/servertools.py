# 工具模块
import asyncio
from datetime import *
from threading import Timer
from rcon.source import *
from mcstatus import JavaServer
from module.sqlrelated import *
from module.botsendmsg import *
from module.logger import *


# 服务器执行
async def server_run(command):
    try:
        log.debug("[RCON]执行命令：{comm}".format(comm=command))
        return await rcon(
            command,
            host=config["RCON_host"], port=config["RCON_post"], passwd=config["RCON_password"]
        )
    except:
        log.error("[RCON]发生错误,请检查配置是否出错")


# 服务器执行(测试服)
async def server_run_test(command):
    try:
        log.debug("[RCON]执行命令：{comm}".format(comm=command))
        return await rcon(
            command,
            host=config["RCON_host_test"], port=config["RCON_post_test"], passwd=config["RCON_password_test"]
        )
    except:
        log.error("[RCON]发生错误,请检查配置是否出错")


# 添加白名单
async def whitelist_add(player):
    output = await server_run("easywhitelist add {player}".format(player=player))
    if "Player is already whitelisted" in output:
        return 1
    elif "Added" in output:
        log.info("[白名单-add]:已成功给予{player}白名单".format(player=player))
        return 0
    else:
        return -1


# 移除白名单
async def whitelist_del(player):
    output = await server_run("easywhitelist remove {player}".format(player=player))
    if "Player is not whitelisted" in output:
        print("[白名单-del]:该玩家未拥有白名单")
        return -1
    elif "Removed" in output:
        log.info("[白名单-del]:已成功移除{player}白名单".format(player=player))
        return 0


# 给予op
async def op_add(player):
    output = await server_run_test("op {player}".format(player=player))
    if "already" in output:
        return 1
    elif "a server operator" in output:
        log.info("[OP-add]:已成功给予{player}白名单".format(player=player))
        return 0
    else:
        return -1


# 移除op
async def op_del(player):
    output = await server_run_test("deop {player}".format(player=player))
    if "The player is not an operator" in output:
        print("[OP-del]:该玩家未拥有OP")
        return 1
    elif "no longer a server operator" in output:
        log.info("[OP-del]:已成功给予{player}白名单".format(player=player))
        return 0
    else:
        return -1


# ban 添加
async def ban_add(player, reason=None):
    await whitelist_del(player)
    output = await server_run("ban {player} {reason}".format(player=player, reason=reason))
    if "Nothing changed. The player is already banned" in output:
        print("[黑名单-add]:该玩家已在黑名单列表")
    elif "Banned by" in output:
        log.info("[黑名单-add]:已成功将{player}移入黑名单".format(player=player))
        return 0


# ban 删除
async def ban_del(player):
    output = await server_run("pardon {player}".format(player=player))
    if "Nothing changed. The player isn't banned" in output:
        print("[白名单-del]:该玩家未在黑名单内")
    elif "Unbanned" in output:
        log.info("[黑名单-del]:已成功移出{player}黑名单".format(player=player))
        return 0


# 玩家列表
async def get_server_players_list():
    temp_str = ""
    for index, host in enumerate(config["serverlist"]):
        temp_str = temp_str + "{server}：".format(server=config["servername"][index])
        try:
            server = JavaServer.lookup(host)  # 连接服务器
            status = server.status()  # 启动连接
            for player in status.players.sample:
                temp_str = temp_str + "[{name}] ".format(name=str(player.name))
        except:
            log.error("连接错误")
            temp_str = temp_str + "服务器连接失败"
        temp_str = temp_str + "\n"

    return temp_str


# 检查服务器状态
async def Server_Status():
    online = 0
    max = 0
    for index, host in enumerate(config["serverlist"]):
        try:
            server = JavaServer.lookup(host)  # 连接服务器
            status = server.status()  # 启动连接
            online = online + status.players.online
            max = max + status.players.max
        except:
            log.error("连接错误")
    players = await get_server_players_list()
    return "[Bot-服务器状态]\n在线人数：{online}/{max}\n在线玩家列表：\n{players}".format(online=online, max=max, players=players)

# 定时任务-踢出未登记假人
'''def kick_bot():
    server_bot_list = bot_get_list()
    success = cursor.execute("SELECT bot_name,time from usedbot")
    DB_bot_list = cursor.fetchall()
    if success == 1:
        for bot,time_add in DB_bot_list:
            if bot in DB_bot_list:
                server_bot_list.remove(bot)
                sql = "UPDATE usedbot SET time = '{time}' ,isused = true where bot_name = '{bot}'".format(
                    time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), bot=bot)
                asyncio.run(sql_run(sql))
                # asyncio.run(say_group(config["player_qun"], "在服务器中找到{bot}，关闭闲置模式".format(bot=bot)))
                print("在服务器中找到Bot：{bot}，已更新状态".format(bot=bot))
            else:
                print("在服务器中不存在Bot：{bot}".format(bot=bot))
                temp = str(time_add)
                Inquire_1 = cursor.execute("SELECT * from usedbot where bot_name = '{bot}' and isused = true".format(bot=bot))
                Inquire_2 = cursor.execute("SELECT * from usedbot where bot_name = '{bot}' and isused = false".format(bot=bot))
                print(Inquire_1, Inquire_2)
                if Inquire_1:
                    sql = "UPDATE usedbot SET time = '{time}' ,isused = false where bot_name = '{bot}'".format(time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), bot=bot)
                    asyncio.run(sql_run(sql))
                    # asyncio.run(say_group(config["player_qun"], "在服务器中找不到{bot}，已切换为闲置模式（30分钟后自动删除）".format(bot=bot)))
                elif Inquire_2:
                    if time.time() - (time.mktime(time.strptime(temp, '%Y-%m-%d %H:%M:%S'))) >= 1800.0:
                        sql = "DELETE from usedbot where bot_name = '{bot}'".format(bot=bot)
                        asyncio.run(sql_run(sql))
                        # asyncio.run(say_group(config["player_qun"], "Bot：{bot}因闲置超过30分钟被关闭！".format(bot=bot)))
                    del temp
        i = 0
        while i != len(server_bot_list):
            asyncio.run(server_run("say Bot:{bot}因未在服务器登记被踢出".format(bot="bot_" + server_bot_list[i])))
            asyncio.run(server_run("player {bot} kill".format(bot="bot_" + server_bot_list[i])))
            # TODO 修复这个鬼东西
            # asyncio.run(say_group(config["player_qun"], "Bot：{bot}未登记被踢出！".format(bot="bot_" + server_bot_list[i])))
            i += 1
    Timer(60.0, kick_bot).start()'''
