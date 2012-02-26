function love.load()

    tilesetImage = love.graphics.newImage("dungeon.png")
    tilesetImage:setFilter("linear", "nearest")

    tileSize = 8
    tileQuads[0] = love.graphics.newQuad(0 * tileSize, 0 * tileSize, tileSize, tileSize, tilesetImage:getWidth(), tilesetImage:getHeight())
    tilesetBatch = love.graphics.newSpriteBatch(tilesetImage, tilesDisplayWidth * tilesDisplayHeight)

end
