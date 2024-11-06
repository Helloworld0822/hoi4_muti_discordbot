import discord # discord.py 라이브러리를 가져옴
from discord import app_commands, Embed  # discord.py에서 app_commands를 가져옴
from discord.ext import commands # discord.ext에서 commands를 가져옴
import datetime, re, pymysql, json, emoji
from steam_web_api import *

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

with open("botset.json", "r") as f:
    data = json.load(f)

list_cha = data["playlist_chenal_id"]
canplay_list_cha = data["canplay_contry_list_id"]
steam = Steam(data["Steam"])

conn = pymysql.connect(
    user=data["user"],
    passwd=data["passwd"],
    host=data["sql_ip"],
    db=data["db"],
    charset="utf8"
)

cur = conn.cursor()
canGPList = ["독일","이탈리아","프랑스","소련","영국","미국","일본"]
canminorlist = ["캐나다","멕시코","아일랜드","벨기에","네덜란드","체코","폴란드","리투아니아","라트비아","에스토니아","덴마크","스웨덴","노르웨이","헝가리","루마니아","유고","불가리아","그리스","터키","이라크","이란","사우디","스페인","에티오피아","남아공","포르투갈","인도","티베트","서북삼마","신강","산서","공산당","중국","운남","광서","만주국","시암","아프간"]
cur.execute("SELECT contry FROM muti_list")

GPList = ["독일","이탈리아","프랑스","소련","영국","미국","일본"]
minorlist = ["캐나다","멕시코","아일랜드","벨기에","네덜란드","체코","폴란드","리투아니아","라트비아","에스토니아","덴마크","스웨덴","노르웨이","헝가리","루마니아","유고","불가리아","그리스","터키","이라크","이란","사우디","스페인","에티오피아","남아공","포르투갈","인도","티베트","서북삼마","신강","산서","공산당","중국","운남","광서","만주국","시암","아프간"]

players = []
contry = []

game_start_date = datetime.datetime(2024, 8, 6)

appstart = False

passtart = False

def hoiplaytime(steamid):
    try:#아이디
        ID=steam.users.search_user(steamid)["player"]["steamid"]
        #게임목록 추출(리스트)
        game=steam.users.get_owned_games(ID)["games"]
        for a in game:
            if a["name"] == "Hearts of Iron IV": # 만약에 스팀 게임 목록에 있는 게임 이름중에 Hearts of Iron IV가 있다면
                if int(a["playtime_forever"]) == 0: # 만약에 게임 시간이 0이라면
                    return None # None을 리턴함
                else:
                    return(int(a["playtime_forever"] / 60)) # 분으로 나타난 플탐을 나누기 60하여 시간으로 바꿈 
    except:
        try:#고유코드
            game=steam.users.get_owned_games(steamid)["games"]
            for a in game:
                    if a["name"] == "Hearts of Iron IV":
                        if int(a["playtime_forever"]) == 0:
                            return None
                        else:
                            return(int(a["playtime_forever"] / 60))
        except:
            try:#프로필주소
                game=steam.users.get_owned_games(steamid[36:-1])["games"]
                for a in game:
                    if a["name"] == "Hearts of Iron IV":
                        if int(a["playtime_forever"]) == 0:
                            return None
                        else:
                            return(int(a["playtime_forever"] / 60))
            except:
                return None

def GPcontrylist():
    global canGPList
    cur.execute("SELECT contry FROM muti_list")
    result = list(cur.fetchall())
    contry.clear()
    canGPList = ["독일","이탈리아","프랑스","소련","영국","미국","일본"]
    for a in range(len(result)):
        contry.append(result[a][0])
    for a in contry:
        if a in GPList:
            canGPList.remove(f'{a}')
    return canGPList

def minorcontrylist():
    global canminorlist
    cur.execute("SELECT contry FROM muti_list")
    result = list(cur.fetchall())
    contry.clear()
    canminorlist = ["캐나다","멕시코","아일랜드","벨기에","네덜란드","체코","폴란드","리투아니아","라트비아","에스토니아","덴마크","스웨덴","노르웨이","헝가리","루마니아","유고","불가리아","그리스","터키","이라크","이란","사우디","스페인","에티오피아","남아공","포르투갈","인도","티베트","서북삼마","신강","산서","공산당","중국","운남","광서","만주국","시암","아프간"]
    for a in range(len(result)):
        contry.append(result[a][0])
    for a in contry:
        if a in minorlist:
            canminorlist.remove(f'{a}')
    return canminorlist

def loadcancontry():
    global Gemb
    global minmsg
    Gemb = Embed(title="가능한 열강",color=discord.Color.green())
    V = emoji.emojize(":white_check_mark:")
    X = emoji.emojize(":x:")
    GPcontrylist()
    minorcontrylist()
    for a in GPList:
        if a in canGPList:
            Gemb.add_field(name=a,value=V)
        else:
            Gemb.add_field(name=a,value=X)
    minmsg = str()
    for a in minorlist:
        if a in canminorlist:
            minmsg += f"{a} : {V} \n"
        else:
            minmsg += f"{a} : {X} \n"

@bot.event
async def on_ready():
    print("봇이 실행되었습니다!")
    await bot.tree.sync(guild=None)
    
mutigroup = app_commands.Group(name="멀티", description="멀티를 신청하거나 취소합니다")
contrygroup = app_commands.Group(name="국가", description="국가를 변경합니다")
admingroup = app_commands.Group(name="관리자", description="위 기능은 관리자만 사용할수 있습니다")

@admingroup.command(name='신청시작', description='멀티를 신청을 받습니다 (위 기능은 관리자만 사용할수 있습니다)')
@app_commands.describe(년='몇년도 까지 받는지', 월='몇월 까지 받는지', 일='몇일 까지 받는지', 시="몇시까지 받는지 (24시간제)")
async def mutistr(interaction: discord.Integration, 년:int, 월:int, 일:int, 시:int):
    global error_cha, two_warning_role, one_warning_role
    two_warning_role = interaction.guild.get_role(data["two_warning_role"])
    one_warning_role = interaction.guild.get_role(data["one_warning_role"])
    error_cha = interaction.guild.get_channel(data["error_chenal"])
    try:
        global game_start_date,appstart,GPemb,minoremb
        if (appstart == False):
            appstart = True
            await bot.change_presence(activity=discord.Game('멀티 신청'), status=discord.Status.online)
            await interaction.response.send_message("지금 부터 멀티 신청 받습니다", ephemeral=False)
            game_start_date = datetime.datetime(년, 월, 일, 시)
            one = list()
            two = list()
            contry.clear()
            for a in discord.utils.find(lambda m: m == two_warning_role, interaction.guild.roles).members:
                await a.remove_roles(one_warning_role)
                one.append(a.mention)
            for x in discord.utils.find(lambda m: m == one_warning_role, interaction.guild.roles).members:
                await x.remove_roles(two_warning_role)
                await x.add_roles(one_warning_role)
                two.append(x.mention)
            print(one)
            print(two)
            loadcancontry()
            GPemb = await interaction.guild.get_channel(canplay_list_cha).send(embed=Gemb)
            minoremb = await interaction.guild.get_channel(canplay_list_cha).send(minmsg)
        else:
            await interaction.response.send_message("멀티를 이미 시작했습니다 멀티 신청을 끝낼려면 /신청마감 을 실행해주세요", ephemeral=True)
    except Exception as error:
        await interaction.response.send_message("명령어를 실행 하던중 에러가 발생하하였습니다 봇 개발자에게 문의 바랍니다", ephemeral=True)
        await error_cha.send(f"{interaction.user.mention}님이 에러가 발생하였습니다 에러 코드 : {error}")  

@admingroup.command(name='제한조회', description='멀티가 제한된 모든 유저를 조회합니다')
async def mutichk(interaction: discord.Integration):
    try:
        one = list()
        two = list()
        one.clear()
        two.clear()
        for a in discord.utils.find(lambda m: m.name == '1회 참여불가', interaction.guild.roles).members:
            one.append(a.mention)
        for b in discord.utils.find(lambda m: m.name == '2회 참여불가', interaction.guild.roles).members:
            two.append(b.mention)
        await interaction.response.send_message(f"1회 금지 \n {one} \n 2회 금지 \n {two} ", ephemeral=True)
    except Exception as error:
        await interaction.response.send_message("명령어를 실행 하던중 에러가 발생하하였습니다 봇 개발자에게 문의 바랍니다", ephemeral=True)
        await error_cha.send(f"{interaction.user.mention}님이 에러가 발생하였습니다 에러 코드 : {error}")

@admingroup.command(name='신청마감', description='멀티를 신청을 마감합니다 (위 기능은 관리자만 사용할수 있습니다)')
async def mutiend(interaction: discord.Integration):
    global game_start_date,appstart,canminorlist,canGPList
    if (appstart == True):
        game_start_date =  datetime.datetime.now()
        appstart = False
        await interaction.response.send_message("멀티를 마감했습니다", ephemeral=True)  
        await interaction.guild.get_channel(list_cha).send("------------------")
        await interaction.guild.get_channel(list_cha).send("멀티가 마감되었습니다.")
        cur.execute(f'CREATE table list_{game_start_date.strftime("%Y_%m_%d_%I_%M_%S")} (select * from muti_list)')
        cur.execute("TRUNCATE TABLE muti_list")
        conn.commit()
        canGPList = ["독일","이탈리아","프랑스","소련","영국","미국","일본"]
        canminorlist = ["캐나다","멕시코","아일랜드","벨기에","네덜란드","체코","폴란드","리투아니아","라트비아","에스토니아","덴마크","스웨덴","노르웨이","헝가리","루마니아","유고","불가리아","그리스","터키","이라크","이란","사우디","스페인","에티오피아","남아공","포르투갈","인도","티베트","서북삼마","신강","산서","공산당","중국","운남","광서","만주국","시암","아프간"]
    else:
        await interaction.response.send_message("멀티를 시작하지 않았습니다", ephemeral=True)         

@admingroup.command(name='멀티강제취소', description='해당 유저의 멀티를 강제로 취소합니다')
@app_commands.describe(유저='멀티를 취소시킬 유저')
async def mutiyesin(interaction: discord.Integration, 유저:discord.Member):
    if (유저.mention in players):
        players.remove(유저.mention)
        cur.execute(f'delete from muti_list where discordname = "{유저.mention}"')
        conn.commit()
        await interaction.response.send_message(f'{유저.mention}님 멀티를 강제로 취소했습니다', ephemeral=True)
        await globals()[유저.mention].delete()
          

@mutigroup.command(name='프로필등록', description='스팀 프로필을 등록하여 호이4 플탐을 불러옵니다(등록해야 멀티 신청이 가능합니다)')
@app_commands.describe(프로필아이디='스팀 프로필 아이디 예시 : 76561198830999507')
async def profile_registration(interaction: discord.Interaction, 프로필아이디:str):
    try:
        youtuber = ["76561198028539878", "76561198081937490"]
        print(f"스팀 : {프로필아이디}, 디스코드 : {interaction.user.mention}")
        if 프로필아이디 not in youtuber:
            if hoiplaytime(프로필아이디) != None:
                try:
                    cur.execute(f'select steamid from steamid where discordname = "{interaction.user.mention}"')
                    id = list(cur.fetchall())
                    if (len(id[0][0]) != 0): 
                        await interaction.response.send_message(f'{interaction.user.mention}님 이미 스팀 프로필을 등록하셨습니다.', ephemeral=True)
                    else:
                        cur.execute(f'insert into steamid values("{interaction.user.mention}","{프로필아이디}")')
                        await interaction.response.send_message(f'{interaction.user.mention}님 성공적으로 스팀 프로필을 등록하였습니다.', ephemeral=True)
                        await interaction.guild.get_channel(data["admin_log_chenal_id"]).send(f"{interaction.user.mention}님이 스팀 아이디를 등록하셨습니다 {프로필아이디}")
                        conn.commit()
                except IndexError:
                    cur.execute(f'insert into steamid values("{interaction.user.mention}","{프로필아이디}")')
                    await interaction.response.send_message(f'{interaction.user.mention}님 성공적으로 스팀 프로필을 등록하였습니다.', ephemeral=True)
                    await interaction.guild.get_channel(data["admin_log_chenal_id"]).send(f"{interaction.user.mention}님이 스팀 아이디를 등록하셨습니다 {프로필아이디}")
                    conn.commit()
            else:
                await interaction.guild.get_channel(data["admin_log_chenal_id"]).send(f"{interaction.user.mention}님이 스팀 아이디가 비공개이거나 게임 세부 정보가 비공개입니다 공개후 다시 해주시기 바랍니다")
        else:
            await interaction.response.send_message(f'{interaction.user.mention}위 스팀 프로필은 유명 유튜버의 아이디입니다 관리자들이 검토 후 등록됩니다.', ephemeral=True)
            await interaction.guild.get_channel(data["admin_log_chenal_id"]).send(f"{interaction.user.mention}님이 유명 유튜버의 아이디로 프로필 등록을 시도하였습니다 검토 해주시기 바랍니다")
            await interaction.guild.get_channel(data["admin_log_chenal_id"]).send(f"https://steamcommunity.com/profiles/{프로필아이디}")
    except Exception as error:
        await interaction.response.send_message("명령어를 실행 하던중 에러가 발생하하였습니다 봇 개발자에게 문의 바랍니다", ephemeral=True)
        await error_cha.send(f"{interaction.user.mention}님이 에러가 발생하였습니다 에러 코드 : {error}")

@mutigroup.command(name='신청', description='멀티를 신청합니다')
@app_commands.describe(닉네임='호이4 닉네임', 국가 = '멀티때 하실 국가(열강은 1500이상부터)') 
async def mutiin(interaction: discord.Interaction, 닉네임:str, 국가:str):
        print(f"{닉네임}, {국가}")
        global participant
        participant = interaction.guild.get_role(data["participant_role"])
        if (appstart == True):
            try:
                cur.execute(f'SELECT steamid FROM steamid where discordname = "{interaction.user.mention}"')
                result = list(cur.fetchall())
                print(result)
                timeid = result[0][0]
                time = hoiplaytime(timeid)
                print(time)
                if (time != None):
                    for roles in interaction.user.roles:
                        if roles == two_warning_role:
                            await interaction.response.send_message(f'{닉네임}님 멀티 2회 금지 경고가 있어 멀티를 하실수 없습니다 나중에 다시해주세요', ephemeral=True)
                            continue
                        elif roles == one_warning_role:
                            await interaction.response.send_message(f'{닉네임}님 멀티 1회 금지 경고가 있어 멀티를 하실수 없습니다 다음에 다시해주세요', ephemeral=True)
                            continue

                    p = re.compile('[ㄱ-힣]')
                    r = p.search(닉네임)
                    if r is None and 닉네임 != "Player":
                        cur.execute("SELECT contry FROM muti_list")
                        result = list(cur.fetchall())
                        contry.clear()
                        for a in range(0, len(result)):
                            contry.append(result[a][0])
                        loadcancontry()
                        if (국가 in canminorlist or 국가 in canGPList):
                            if 국가 in GPList:
                                if (time >= 1500):
                                    cur.execute(f'insert into muti_list values("{국가}","{interaction.user.mention}","{닉네임}", {time});')
                                    conn.commit()
                                    await interaction.response.send_message(f'{닉네임}님 멀티 신청이 완료되었습니다 국가 : {국가} 멀티 날짜  {game_start_date}', ephemeral=True)
                                    emb = Embed(title=국가, color=discord.Color.green())
                                    emb.add_field(name="닉네임", value=닉네임,inline=False)
                                    emb.add_field(name="시간", value=time,inline=False)
                                    emb.add_field(name="디코 닉네임", value=interaction.user.mention,inline=False)
                                    globals()[interaction.user.mention.format()] = await interaction.guild.get_channel(list_cha).send(embed=emb)
                                    await interaction.user.add_roles(participant)
                                    loadcancontry()
                                    await GPemb.edit(embed=Gemb)
                                else:
                                    await interaction.response.send_message(f'{닉네임}님 열강을 할려면 1500시간 이상이 되어야합니다', ephemeral=True)
                            elif 국가 in minorlist:
                                cur.execute(f'insert into muti_list values("{국가}","{interaction.user.mention}","{닉네임}",{time})')
                                conn.commit()
                                await interaction.response.send_message(f'{닉네임}님 멀티 신청이 완료되었습니다 국가 : {국가} 멀티 날짜  {game_start_date}', ephemeral=True)
                                emb = Embed(title=국가, color=discord.Color.green())
                                emb.add_field(name="닉네임", value=닉네임,inline=False)
                                emb.add_field(name="시간", value=time,inline=False)
                                emb.add_field(name="디코 닉네임", value=interaction.user.mention,inline=False)
                                globals()[interaction.user.mention.format()] = await interaction.guild.get_channel(list_cha).send(embed=emb)
                                await interaction.user.add_roles(participant)
                                loadcancontry()
                                await minoremb.edit(content=minmsg)
                            else:
                                await interaction.response.send_message(f'{닉네임}님 {국가}는 신청할수 없는 국가입니다', ephemeral=True)
                        else:
                            await interaction.response.send_message(f'{닉네임} 해당 국가는 누가 이미 했습니다 다른 국가를 해주시길 바랍니다', ephemeral=True)
                    else:
                        await interaction.response.send_message(f'{닉네임}님 닉네임이 Player거나 한글이면 안됩니다', ephemeral=True)  
                else: 
                    await interaction.response.send_message(f'{닉네임}님 스팀 프로필 게임 세부 정보가 비공개입니다 공개 후 다시 해주세요', ephemeral=True)
            except IndexError:
                await interaction.response.send_message(f'{닉네임}님 스팀 프로필을 등록하지 않으셨습니다 스팀 프로필을 등록해주세요', ephemeral=True)
            except Exception as error:
                await interaction.response.send_message("명령어를 실행 하던중 에러가 발생하였습니다 봇 개발자에게 문의 바랍니다", ephemeral=True)
                await error_cha.send(f"{interaction.user.mention}님이 에러가 발생하였습니다 에러 코드 : {error}")
        else:
            await interaction.response.send_message(f'{닉네임}님 지금은 멀티 신청을 받지 않습니다', ephemeral=True)
            
@mutigroup.command(name='취소', description='멀티를 취소합니다')
@app_commands.describe(사유='멀티를 취소하는 이유') 
async def mutiout(interaction: discord.Interaction, 사유:str):
    try:
        cur.execute("SELECT discordname FROM muti_list")
        pla_result = list(cur.fetchall())
        players.clear()
        for a in range(len(pla_result)):
            players.append(pla_result[a][0])
        cur.execute(f'SELECT contry FROM muti_list WHERE discordname = "{interaction.user.mention}"')
        con_result = list(cur.fetchall())
        if(interaction.user.mention in players):
            if ((game_start_date.date() - datetime.datetime.now().date()).days <= 0): 
                cur.execute(f'delete from muti_list where discordname = "{interaction.user.mention}"')
                conn.commit()
                await interaction.response.send_message(f'{interaction.user.mention}님 멀티를 당일 취소하셨기 때문에 멀티를 2회 참여하실수 없게 됩니다', ephemeral=True)
                await globals()[interaction.user.mention].delete()
                await interaction.guild.get_channel(data["admin_log_chenal_id"]).send(f'{interaction.user.mention}님 멀티를 당일 취소했습니다 취소 사유 : {사유} 취소 국가 : {con_result[0][0]}')
                await interaction.user.add_roles(two_warning_role, "당일 멀티 취소")
                await interaction.user.remove_roles(participant)
                loadcancontry()
                await minoremb.edit(content=minmsg)
                await GPemb.edit(embed=Gemb)
            else:
                cur.execute(f'delete from muti_list where discordname = "{interaction.user.mention}"')
                conn.commit()
                await interaction.response.send_message(f'{interaction.user.mention}님 멀티를 취소했습니다', ephemeral=True)
                await interaction.guild.get_channel(data["admin_log_chenal_id"]).send(f'{interaction.user.mention}님 멀티를 취소했습니다 취소 사유 : {사유} 취소 국가 : {con_result[0][0]}')
                await interaction.user.remove_roles(participant)
                await globals()[interaction.user.mention].delete()
                loadcancontry()
                await minoremb.edit(content=minmsg)
                await GPemb.edit(embed=Gemb)
        else:
            await interaction.response.send_message(f'{interaction.user.mention}님 멀티를 신청 하지 않으셨습니다', ephemeral=True)
    except Exception as error:
        await interaction.response.send_message("명령어를 실행 하던중 에러가 발생하하였습니다 봇 개발자에게 문의 바랍니다", ephemeral=True)
        await error_cha.send(f"{interaction.user.mention}님이 에러가 발생하였습니다 에러 코드 : {error}")

@mutigroup.command(name="목록", description="신청할수 있는 목록을 보여줍니다")
async def mutilist(interaction: discord.Interaction):
    if (appstart == True):
        loadcancontry()
        print(GPcontrylist())
        print(minorcontrylist())
        await interaction.response.send_message(f'신청할수 있는 열강 \n {GPcontrylist()} \n 신청할수 있는 마이너 \n {minorcontrylist()}', ephemeral=True)
    else:
        await interaction.response.send_message(f"{interaction.user.mention}님 아직 멀티가 시작되지 않았습니다", ephemeral=True)
        


@contrygroup.command(name='변경', description='멀티에서 할 국가를 바꿉니다')
@app_commands.describe(바꿀_국가='바꿀 국가')
async def muticha(interaction: discord.Interaction, 바꿀_국가:str):
    try:
        cur.execute("SELECT discordname FROM muti_list")
        pla_result = list(cur.fetchall())
        players.clear()
        for a in range(0, len(pla_result)):
            players.append(pla_result[a][0])
        if(interaction.user.mention in players):
            cur.execute("SELECT contry FROM muti_list")
            result = list(cur.fetchall())
            contry.clear()
            cur.execute(f'SELECT * from muti_list WHERE discordname = "{interaction.user.mention}"')
            row = [cur.fetchall()][0][0]
            name = row[2]
            time = int(row[3])
            players_contry = row[0]
            for a in range(0, len(result)):
                contry.append(result[a][0])
            if(바꿀_국가 in contry):
                await interaction.response.send_message(f'{interaction.user.mention}님 해당 국가는 누가 이미 했습니다 다른 나라를 해주시길 바랍니다', ephemeral=True)
            else:
                if 바꿀_국가 in ["독일","이탈리아", "프랑스", "영국", "일본","미국","소련"]:
                    if (time >= 1500):
                        cur.execute(f'update muti_list set contry = "{바꿀_국가}" where discordname = "{interaction.user.mention}"')
                        conn.commit()
                        emb = discord.Embed(title=바꿀_국가, color=discord.Color.green())
                        emb.add_field(name="닉네임", value=name,inline=False)
                        emb.add_field(name="시간", value=time,inline=False)
                        emb.add_field(name="디코 닉네임", value=interaction.user.mention,inline=False)
                        await globals()[interaction.user.mention].delete()
                        globals()[interaction.user.mention.format()] = await interaction.guild.get_channel(list_cha).send(embed=emb)
                        await interaction.response.send_message(f'{interaction.user.mention}님 국가를 {바꿀_국가}로 바꾸었습니다', ephemeral=True)
                        await interaction.guild.get_channel().send(f'{interaction.user.mention}님이 {players_contry} 에서 {바꿀_국가}로 국가를 변경하셨습니다.')
                        loadcancontry()
                        await GPemb.edit(embed=Gemb)
                    else:
                        await interaction.response.send_message(f'{interaction.user.mention}님 열강을 할려면 1500시간 이상이 되어야합니다', ephemeral=True)
                elif 바꿀_국가 in ["오스트리아","라이베리아","아우사술탄국","아우사 술탄국","탄누투바","부탄","네팔","알바니아","예멘","룩셈부르크","파라과이","우루과이"]:
                    await interaction.response.send_message(f'{interaction.user.mention}님 해당 국가는 신청할수 없습니다', ephemeral=True)
                else:
                    cur.execute(f'update muti_list set contry = "{바꿀_국가}" where discordname = "{interaction.user.mention}"')
                    conn.commit()
                    cur.execute(f'SELECT * from muti_list WHERE discordname = "{interaction.user.mention}"')
                    await interaction.response.send_message(f'{interaction.user.mention}님 국가를 {바꿀_국가}로 바꾸었습니다', ephemeral=True)
                    emb = discord.Embed(title=바꿀_국가, color=discord.Color.green())
                    emb.add_field(name="닉네임", value=name,inline=False)
                    emb.add_field(name="시간", value=time,inline=False)
                    emb.add_field(name="디코 닉네임", value=interaction.user.mention,inline=False)
                    await globals()[interaction.user.mention].delete()
                    globals()[interaction.user.mention.format()] = await interaction.guild.get_channel(list_cha).send(embed=emb)
                    await interaction.guild.get_channel().send(f'{interaction.user.mention}님이 {players_contry} 에서 {바꿀_국가}로 국가를 변경하셨습니다.')
                    loadcancontry()
                    await minoremb.edit(content=minmsg)
        else:
            await interaction.response.send_message(f'{interaction.user.mention}님 멀티를 신청 하지 않으셨습니다', ephemeral=True)
    except Exception as error:
        await interaction.response.send_message("명령어를 실행 하던중 에러가 발생하하였습니다 봇 개발자에게 문의 바랍니다", ephemeral=True)
        await error_cha.send(f"{interaction.user.mention}님이 에러가 발생하였습니다 에러 코드 : {error}")


bot.tree.add_command(mutigroup)
bot.tree.add_command(admingroup)
bot.tree.add_command(contrygroup)
bot.run(data["token"])