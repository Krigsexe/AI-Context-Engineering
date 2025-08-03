-- ODIN Sample Resource Configuration
-- Testing ODIN v6.0 - Semantic Integrity Hash, TestGen, and DepGuard

Config = {}

-- General settings
Config.ResourceName = "odin_sample_resource"
Config.Version = "6.0.0"
Config.Author = "Make With Passion by Krigs"
Config.DebugMode = true

-- Server settings
Config.MaxPlayers = 32
Config.SaveInterval = 300000 -- 5 minutes in milliseconds
Config.DatabaseTimeout = 10000 -- 10 seconds

-- Player settings
Config.DefaultMoney = 5000
Config.DefaultRank = "citizen"
Config.MaxInventorySlots = 40

-- Notification settings
Config.NotificationDuration = 5000 -- 5 seconds
Config.NotificationPosition = "top-right"

-- Commands
Config.Commands = {
    {
        name = "odin_stats",
        description = "Show ODIN server statistics",
        restricted = false
    },
    {
        name = "odin_reload",
        description = "Reload ODIN configuration",
        restricted = true
    },
    {
        name = "odin_save",
        description = "Force save player data",
        restricted = true
    }
}

-- Database tables
Config.Tables = {
    players = "odin_players",
    vehicles = "odin_vehicles",
    properties = "odin_properties",
    logs = "odin_logs"
}

-- Ranks and permissions
Config.Ranks = {
    ["superadmin"] = {
        level = 100,
        label = "Super Admin",
        permissions = {"*"}
    },
    ["admin"] = {
        level = 80,
        label = "Administrator",
        permissions = {"kick", "ban", "teleport", "give_money", "spawn_vehicle"}
    },
    ["moderator"] = {
        level = 60,
        label = "Moderator",
        permissions = {"kick", "teleport", "freeze"}
    },
    ["vip"] = {
        level = 20,
        label = "VIP Player",
        permissions = {"spawn_vehicle"}
    },
    ["citizen"] = {
        level = 0,
        label = "Citizen",
        permissions = {}
    }
}

-- Vehicle spawn locations
Config.VehicleSpawns = {
    {x = -1038.59, y = -2738.45, z = 13.84, h = 240.0},
    {x = -1026.15, y = -2741.68, z = 13.78, h = 240.0},
    {x = -1013.71, y = -2744.91, z = 13.72, h = 240.0}
}

-- Teleport locations
Config.TeleportLocations = {
    spawn = {x = -1037.81, y = -2737.84, z = 20.17, label = "Spawn Point"},
    airport = {x = -1037.55, y = -2965.86, z = 13.94, label = "Airport"},
    city = {x = 215.52, y = -810.13, z = 30.73, label = "City Center"},
    beach = {x = -1394.31, y = -1020.77, z = 13.0, label = "Beach"}
}

-- Items configuration
Config.Items = {
    ["water"] = {
        label = "Water Bottle",
        weight = 0.5,
        type = "consumable",
        usable = true
    },
    ["bread"] = {
        label = "Bread",
        weight = 0.3,
        type = "consumable",
        usable = true
    },
    ["phone"] = {
        label = "Mobile Phone",
        weight = 0.2,
        type = "tool",
        usable = true
    }
}

-- Logging levels
Config.LogLevels = {
    TRACE = 0,
    DEBUG = 1,
    INFO = 2,
    WARN = 3,
    ERROR = 4,
    FATAL = 5
}

-- Current log level (based on ODIN settings)
Config.CurrentLogLevel = Config.DebugMode and Config.LogLevels.DEBUG or Config.LogLevels.INFO

-- ODIN-specific settings for testing
Config.ODIN = {
    TestMode = true,
    IntegrityChecks = true,
    AutoBackup = true,
    TestGeneration = true,
    DepGuardEnabled = true
}
