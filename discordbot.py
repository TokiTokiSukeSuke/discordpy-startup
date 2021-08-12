import discord
# import asyncio

# 用意したBOTのトークン
DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']

# ディスコードAPI を生成
client = discord.Client()

# 本BOTの名前
BOT_NAME = "創造ちゃんと破滅くん"
# テキストチャンネルにデフォルトで
CHANNEL_PREFIX = "の部屋_"
# botたちのロール名 (botはテキストチャンネルに参加していてほしい)
BOT_ROLE_NAME = "Bot"
# 該当カテゴリに存在する部屋が対象
TGT_CATEGORY_NAME = "CREATION AND RUIN CATEGORY"
# 複製した部屋の名前(最大75桁)_新部屋ID_基部屋ID
CREATEROOM_NAME = "CreateRoom_"

#コマンド
CMD_ROOMNAME_CHANGE = "/car_rnc "

# 実行した際にログインされたかを確認 及び 初期化処理
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# テキストチャットに変更があった場合
@client.event
async def on_message(message):

    # 当ボットが発信したコメントは無視。
    if client.user == message.author: return

    # カテゴリ内でなければ無視。
    tgtCategoryCh = client.get_channel(message.channel.category_id)
    if tgtCategoryCh.name.upper() != TGT_CATEGORY_NAME: return

    # 部屋名の変更(部屋名 + ボイスチャンネルIDで紐づけ)
    if message.content.startswith(CMD_ROOMNAME_CHANGE):
        
        # テキストチャット部屋名から紐づくボイスチャットを探す
        voiceChatRoom = None
        voiceChatId = str(message.channel.name)[-18:]
        if voiceChatId.isdigit():
            voiceChatRoom = discord.utils.get(message.guild.voice_channels, id=int(voiceChatId))


        # 部屋が存在しない場合
        if voiceChatRoom is None:
            await message.channel.send("このテキストのボイスチャットが存在しません。")
            return


        # 部屋に人が存在しない場合
        blnTgtMember = False
        for member in voiceChatRoom.members:
            if member.id == message.author.id:
                blnTgtMember = True
                break
        
        if blnTgtMember == False:
            await message.channel.send(message.author.name+"様がこのテキストのボイスチャットに居ない為、変更できません。")
            return


        # メッセージ発信者のIDと部屋名のIDが一致しない場合は、変更できない！
        if str(message.author.id) != str(voiceChatRoom.name)[-18:]: 
            
            # 変更できない旨、発信して処理終了。
            await message.channel.send("この部屋の作成者が"+message.author.name+"様でない為、部屋名の変更が出来ません。")
            return
        
        
        # 変更後の部屋名を取得
        strChangeName = message.content[(len(CMD_ROOMNAME_CHANGE)):]

        # 部屋名の文字数制限
        if len(strChangeName) > 75:
            await message.channel.send("部屋名の文字数は、75文字以内で設定して下さい。")
            return
        
        # # 問題なければ、ボイス及びテキストの部屋名の変更を行う。
        # strChangeVcName = strChangeName+str(voiceChatRoom.name)[-22:]
        # strChangeTxName = strChangeName+str(message.channel.name)[-22:]
        # await voiceChatRoom.edit(name=strChangeVcName)
        # await message.channel.edit(name=strChangeTxName)
        
        await _channel_name_change(message.channel,voiceChatRoom,strChangeName)
        # try:
        #     await asyncio.wait_for(_channel_name_change(message.channel,voiceChatRoom,strChangeName), timeout=1.5)
        # except asyncio.TimeoutError:
        #     await message.channel.send("部屋名の変更に失敗！時間を置いてもう一度試すか、部屋を作り直してください。")

# 部屋名の変更
async def _channel_name_change(textChat,voiceChat,editName):
    await textChat.edit(name=editName+str(textChat.name)[-22:])
    await voiceChat.edit(name=editName+str(voiceChat.name)[-22:])
    await textChat.send("部屋名変更完了！")


# ボイスチャンネルの状態が変化した時に実行(対象者、前状態、後状態)
@client.event
async def on_voice_state_update(member, before, after):

    # チャンネルを移動していない場合に処理をしない。
    # ※ミュートなどでもステータスが変わる為。
    if before.channel == after.channel: return

    # チャンネルから退出した場合
    if before.channel is not None:
        
        # 前まで入っていたボイスのカテゴリを退出した部屋が存在するカテゴリのIDで取得
        tgtCategoryCh = client.get_channel(before.channel.category_id)
        
        # 該当カテゴリ内であれば続行
        if tgtCategoryCh.name.upper() == TGT_CATEGORY_NAME:

            # 退出した部屋が複製用の部屋でなければ
            if before.channel != tgtCategoryCh.voice_channels[0]:
            
                # ボイスチャンネルに誰もいない場合
                if len(before.channel.members) == 0:
                    
                    # テキストチャンネルを削除
                    await _channel_delete(before.channel)

                    # ボイスチャンネルを削除
                    await before.channel.delete()

                else:
                    
                    # テキストチャンネルを見えなくする
                    await _channel_exit(member, before.channel)


    # チャンネルに入質した場合
    if after.channel is not None:
        
        # 今から入るボイスのカテゴリを入室する部屋が存在するカテゴリのIDで取得
        tgtCategoryCh = client.get_channel(after.channel.category_id)

        # 該当カテゴリ内であれば、続行
        if tgtCategoryCh.name.upper() == TGT_CATEGORY_NAME:

            # 複製用の部屋に入った時のみ部屋の複製を行い、終了する。
            if after.channel == tgtCategoryCh.voice_channels[0]:

                # 部屋の複製(部屋名_メンバーID)
                await tgtCategoryCh.voice_channels[0].clone(
                    name=member.name + CHANNEL_PREFIX + str(member.id),reason=None)

                # メンバーを複製した部屋に移動
                await member.move_to(tgtCategoryCh.voice_channels[-1],reason=None)
                
            # 複製の部屋でなければ、テキストチャンネル権限対応。
            else:
                
                # 一人目の場合
                if len(after.channel.members) == 1:

                    # 専用テキストチャンネルの作成(部屋名_ボイス部屋ID)
                    await _channel_create(member, after.channel)

                # そうでない場合
                else:
                    
                    # 既にテキストがある為、テキストチャットへ参加させる。
                    await _channel_join(member, after.channel)

            # 入場時にメンションでテキストチャンネルへ案内
            # await _channel_send_join(member, after.channel)


# テキストチャンネルを検索する関数
def _channel_find(voiceChannel):
    # カテゴリを取得
    tgtCategoryCh = client.get_channel(voiceChannel.category_id)
    # カテゴリ内のテキストチャットを繰り返して探して、IDが一致した部屋を返す
    for tgtTextChannel in tgtCategoryCh.text_channels:
        if str(tgtTextChannel.name)[-18:] == str(voiceChannel.id):
            return tgtTextChannel
    return None


# チャンネル作成時の権限リストを返す
def _init_overwrites(guild, member):
    
    # 参加するメンバーがオーナーの場合 元コード
    overwrites = {
        # デフォルトのユーザーはメッセージを見れないように
        guild.default_role:discord.PermissionOverwrite(read_messages=False),
        # 参加したメンバーは見ることができるように
        member: discord.PermissionOverwrite(read_messages=True)
    }
    
    # BOTが見れるように
    bots_role = discord.utils.get(guild.roles, name=BOT_NAME)
    if bots_role is not None:
        # Botもメッセージを見れるように
        bot_overwrite = {
            bots_role: discord.PermissionOverwrite(read_messages=True)
        }
        overwrites.update(bot_overwrite)

    # BOTが見れるように
    bots_role = discord.utils.get(guild.roles, name=BOT_ROLE_NAME)
    if bots_role is not None:
        # Botもメッセージを見れるように
        bot_overwrite = {
            bots_role: discord.PermissionOverwrite(read_messages=True)
        }
        overwrites.update(bot_overwrite)

    return overwrites


# テキストチャンネルを作成する関数
async def _channel_create(member, voiceChannel):
    guild = voiceChannel.guild

    channel_name = member.name + CHANNEL_PREFIX + str(voiceChannel.id)
    overwrites = _init_overwrites(guild, member)
    category = voiceChannel.category

    # テキストチャンネルを作成
    await guild.create_text_channel(
        channel_name, overwrites=overwrites, category=category)


# テキストチャンネルを削除する関数
async def _channel_delete(voiceChannel):
    target = _channel_find(voiceChannel)
    if target is not None:
        await target.delete()


# テキストチャンネルに参加させる関数
async def _channel_join(member, voiceChannel):
    target = _channel_find(voiceChannel)
    if target is not None:
        overwrites = discord.PermissionOverwrite(read_messages=True)
        # 該当メンバーに読み取り権限を付与
        await target.set_permissions(member, overwrite=overwrites)


# テキストチャンネルから退出させる関数
async def _channel_exit(member, voiceChannel):
    target = _channel_find(voiceChannel)
    if target is not None:
        # 該当メンバーの読取権限を取り消し
        await target.set_permissions(member, overwrite=None)


# 入室時にメンションを飛ばして案内したい
async def _channel_send_join(member, voiceChannel):
    target = _channel_find(voiceChannel)
    if target is not None:
        await target.send(member.mention + "通話中のチャットはこちらをお使いください")


# 設定されたTokenのボットへ動きを流し込む
client.run(DISCORD_BOT_TOKEN)
