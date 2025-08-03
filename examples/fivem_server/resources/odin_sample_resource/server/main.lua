-- ODIN Sample Resource - Server Main
-- Testing ODIN v6.0 - Semantic Integrity Hash, TestGen, and DepGuard

-- Initialize server-side functionality
print("^2[ODIN Sample Resource] ^7Server starting...")
print("^2[ODIN Sample Resource] ^7Version: " .. Config.Version)

-- Global variables
local playerData = {}
local serverStats = {
    startTime = os.time(),
    totalConnections = 0,
    currentPlayers = 0,
    dataOperations = 0
}

-- Player connection handler
AddEventHandler('playerConnecting', function(name, setKickReason, deferrals)
    local source = source
    local identifier = GetPlayerIdentifier(source, 0)
    
    deferrals.defer()
    Wait(0)
    
    deferrals.update("Loading ODIN data...")
    
    -- Load player data from database
    LoadPlayerData(source, function(success, data)
        if success then
            playerData[source] = data
            serverStats.totalConnections = serverStats.totalConnections + 1
            deferrals.done()
            print("^2[ODIN Sample Resource] ^7Player " .. name .. " connected successfully")
        else
            deferrals.done("Failed to load player data. Please try again.")
            print("^1[ODIN Sample Resource] ^7Failed to load data for " .. name)
        end
    end)
end)

-- Player join handler
AddEventHandler('playerJoining', function()
    local source = source
    serverStats.currentPlayers = serverStats.currentPlayers + 1
    
    -- Initialize default player data if new
    if not playerData[source] then
        playerData[source] = {
            money = Config.DefaultMoney,
            rank = Config.DefaultRank,
            inventory = {},
            lastLogin = os.time(),
            playtime = 0
        }
    end
    
    -- Send welcome notification
    TriggerClientEvent('odin:sendNotification', source, {
        type = 'success',
        title = 'ODIN Server',
        message = 'Welcome to ODIN v6.0 Testing Environment!',
        duration = Config.NotificationDuration
    })
end)

-- Player disconnect handler
AddEventHandler('playerDropped', function(reason)
    local source = source
    
    if playerData[source] then
        -- Save player data before disconnect
        SavePlayerData(source, playerData[source])
        playerData[source] = nil
    end
    
    serverStats.currentPlayers = math.max(0, serverStats.currentPlayers - 1)
    print("^3[ODIN Sample Resource] ^7Player disconnected: " .. reason)
end)

-- Get player data function (exported)
function GetPlayerData(source)
    return playerData[source] or {}
end

-- Set player data function (exported)
function SetPlayerData(source, key, value)
    if playerData[source] then
        playerData[source][key] = value
        serverStats.dataOperations = serverStats.dataOperations + 1
        return true
    end
    return false
end

-- Get server statistics (exported)
function GetServerStats()
    local uptime = os.time() - serverStats.startTime
    return {
        uptime = uptime,
        totalConnections = serverStats.totalConnections,
        currentPlayers = serverStats.currentPlayers,
        dataOperations = serverStats.dataOperations,
        maxPlayers = Config.MaxPlayers,
        version = Config.Version
    }
end

-- Send notification function (exported)
function SendNotification(source, notification)
    TriggerClientEvent('odin:sendNotification', source, notification)
end

-- Periodic save task
CreateThread(function()
    while true do
        Wait(Config.SaveInterval)
        
        for source, data in pairs(playerData) do
            SavePlayerData(source, data)
        end
        
        print("^5[ODIN Sample Resource] ^7Auto-saved player data for " .. GetNumPlayerIndices() .. " players")
    end
end)

-- Resource stopping handler
AddEventHandler('onResourceStop', function(resourceName)
    if resourceName == GetCurrentResourceName() then
        print("^1[ODIN Sample Resource] ^7Stopping resource...")
        
        -- Save all player data before stopping
        for source, data in pairs(playerData) do
            SavePlayerData(source, data)
        end
        
        print("^2[ODIN Sample Resource] ^7Resource stopped successfully")
    end
end)

-- ODIN integrity check function
function PerformIntegrityCheck()
    local checksums = {}
    local files = {
        'fxmanifest.lua',
        'server/main.lua',
        'client/main.lua',
        'shared/config.lua'
    }
    
    for _, file in ipairs(files) do
        -- In a real implementation, this would calculate actual file checksums
        checksums[file] = "sha256_placeholder_" .. tostring(math.random(1000000, 9999999))
    end
    
    return checksums
end

-- Export functions
exports('GetPlayerData', GetPlayerData)
exports('SetPlayerData', SetPlayerData)
exports('SendNotification', SendNotification)
exports('GetServerStats', GetServerStats)
exports('PerformIntegrityCheck', PerformIntegrityCheck)

print("^2[ODIN Sample Resource] ^7Server initialized successfully!")
