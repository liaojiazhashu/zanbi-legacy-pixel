-- LibreSprite Lua 脚本测试：创建 sprite、画像素、保存
local spr = app.newSprite(96, 160)
if not spr then
    print("ERROR: newSprite failed")
    return
end
app.activeSprite = spr
local img = app.activeImage
print("sprite created:", img.width, "x", img.height)

-- 画一个测试像素块
for y = 10, 30 do
    for x = 10, 40 do
        local c = Color{r=200, g=100, b=50, a=255}
        img:putPixel(x, y, c)
    end
end

-- 保存为 PNG
app.command.SaveFileAs{filename="D:/AAAAI/动画视频尝试/赞比的遗产/_ls_test.png", asCopy=true}
print("saved")
